### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Replacement**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created a `FuturesSession` instance to handle asynchronous requests.
3. **Request Calls**: Replaced synchronous `requests.get` and `requests.request` calls with asynchronous `session.get` and `session.request` calls.
4. **Response Handling**: Since `requests_futures` returns a `Future` object, the `.result()` method is used to retrieve the actual response synchronously where needed.
5. **Error Handling**: Adjusted exception handling to account for the asynchronous nature of `requests_futures`.

### Modified Code:
```python
# -*- coding: utf-8 -*-

"""This module provides access to the external task REST api of Camunda."""

from __future__ import annotations
import datetime as dt
import dataclasses
import typing

from requests_futures.sessions import FuturesSession

import pycamunda
import pycamunda.base
import pycamunda.variable
import pycamunda.batch
from pycamunda.request import QueryParameter, PathParameter, BodyParameter

URL_SUFFIX = '/external-task'

# Initialize a FuturesSession for asynchronous requests
session = FuturesSession()

__all__ = [
    'GetList', 'Count', 'FetchAndLock', 'Complete', 'HandleBPMNError', 'HandleFailure', 'Unlock',
    'ExtendLock', 'SetPriority', 'SetRetries', 'SetRetriesAsync', 'SetRetriesSync'
]


@dataclasses.dataclass
class ExternalTask:
    """Data class of external task as returned by the REST api of Camunda."""
    activity_id: str
    activity_instance_id: str
    error_message: str
    execution_id: str
    id_: str
    process_definition_id: str
    process_definition_key: str
    process_instance_id: str
    tenant_id: str
    retries: int
    worker_id: str
    priority: str
    topic_name: str
    lock_expiration_time: dt.datetime = None
    suspended: bool = None
    business_key: str = None
    variables: typing.Dict[str, typing.Dict[str, typing.Any]] = None
    error_details: str = None

    @classmethod
    def load(cls, data: typing.Mapping[str, typing.Any]) -> ExternalTask:
        external_task = cls(
            activity_id=data['activityId'],
            activity_instance_id=data['activityInstanceId'],
            error_message=data['errorMessage'],
            execution_id=data['executionId'],
            id_=data['id'],
            process_definition_id=data['processDefinitionId'],
            process_definition_key=data['processDefinitionKey'],
            process_instance_id=data['processInstanceId'],
            tenant_id=data['tenantId'],
            retries=data['retries'],
            worker_id=data['workerId'],
            priority=data['priority'],
            topic_name=data['topicName']
        )
        if data['lockExpirationTime'] is not None:
            external_task.lock_expiration_time = pycamunda.base.from_isoformat(
                data['lockExpirationTime']
            )
        try:
            external_task.suspended = data['suspended']
        except KeyError:
            pass
        try:
            external_task.error_details = data['errorDetails']
        except KeyError:
            pass
        try:
            external_task.business_key = data['businessKey']
        except KeyError:
            pass
        try:
            variables = data['variables']
        except KeyError:
            pass
        else:
            external_task.variables = {
                var_name: pycamunda.variable.Variable(
                    type_=var['type'], value=var['value'], value_info=var['valueInfo']
                )
                for var_name, var in variables.items()
            }
        return external_task


class Get(pycamunda.base.CamundaRequest):

    id_ = PathParameter('id')

    def __init__(self, url: str, id_: str, request_error_details: bool = True):
        """Query for an external task.

        :param url: Camunda Rest engine URL.
        :param id_: Id of the external task.
        :param request_error_details: Whether to request error details for tasks. Requires an
                                      additional request.
        """
        super().__init__(url=url + URL_SUFFIX + '/{id}')
        self.id_ = id_
        self.request_error_details = request_error_details

    def __call__(self, *args, **kwargs) -> ExternalTask:
        """Send the request."""
        response = super().__call__(pycamunda.base.RequestMethod.GET, *args, **kwargs)
        external_task = ExternalTask.load(response.json())

        if self.request_error_details:
            if external_task.error_details is None:
                try:
                    future_response = session.get(self.url + '/errorDetails')
                    response = future_response.result()  # Wait for the response
                except Exception:
                    raise pycamunda.PyCamundaException()
                if not response:
                    pycamunda.base._raise_for_status(response)
                external_task.error_details = response.text

        return external_task


class GetList(pycamunda.base.CamundaRequest):

    id_ = QueryParameter('externalTaskId')
    topic_name = QueryParameter('topicName')
    worker_id = QueryParameter('workerId')
    locked = QueryParameter('locked', provide=pycamunda.base.value_is_true)
    not_locked = QueryParameter('notLocked', provide=pycamunda.base.value_is_true)
    with_retries_left = QueryParameter('withRetriesLeft', provide=pycamunda.base.value_is_true)
    no_retries_left = QueryParameter('noRetriesLeft', provide=pycamunda.base.value_is_true)
    lock_expiration_after = QueryParameter('lockExpirationAfter')
    lock_expiration_before = QueryParameter('lockExpirationBefore')
    activity_id = QueryParameter('activityId')
    actitity_id_in = QueryParameter('activityIdIn')
    execution_id = QueryParameter('executionId')
    process_instance_id = QueryParameter('processInstanceId')
    process_definition_id = QueryParameter('processDefinitionId')
    tenant_id_in = QueryParameter('tenantIdIn')
    active = QueryParameter('active', provide=pycamunda.base.value_is_true)
    priority_higher_equals = QueryParameter('priorityHigherThanOrEquals')
    priority_lower_equals = QueryParameter('priorityLowerThanOrEquals')
    suspended = QueryParameter('suspended', provide=pycamunda.base.value_is_true)
    sort_by = QueryParameter(
        'sortBy',
        mapping={
         'id_': 'id',
         'lock_expiration_time': 'lockExpirationTime',
         'process_instance_id': 'processInstanceId',
         'process_definition_id': 'processDefinitionId',
         'tenant_id': 'tenantId',
         'task_priority': 'taskPriority'
        }
    )
    ascending = QueryParameter(
        'sortOrder',
        mapping={True: 'asc', False: 'desc'},
        provide=lambda self, obj, obj_type: vars(obj).get('sort_by', None) is not None
    )
    first_result = QueryParameter('firstResult')
    max_results = QueryParameter('maxResults')

    def __init__(
        self,
        url: str,
        id_: str = None,
        topic_name: str = None,
        worker_id: str = None,
        locked: bool = False,
        not_locked: bool = False,
        with_retries_left: bool = False,
        no_retries_left: bool = False,
        lock_expiration_after: dt.datetime = None,
        lock_expiration_before: dt.datetime = None,
        activity_id: str = None,
        activity_id_in: typing.Iterable[str] = None,
        execution_id: str = None,
        process_instance_id: str = None,
        process_definition_id: str = None,
        tenant_id_in: typing.Iterable[str] = None,
        active: bool = False,
        priority_higher_equals: int = None,
        priority_lower_equals: int = None,
        suspended: bool = False,
        sort_by: str = None,
        ascending: bool = True,
        first_result: int = None,
        max_results: int = None,
        request_error_details: bool = True
    ):
        """Query for a list of external tasks using a list of parameters. The size of the result set
        can be retrieved by using the Get Count request.

        :param url: Camunda Rest engine URL.
        :param id_: Filter by the id of the external task.
        :param topic_name: Filter by the topic name of the external task.
        :param worker_id: Filter by the id of the worker the task was locked by last.
        :param locked: Include only locked external tasks.
        :param not_locked: Include only unlocked tasks.
        :param with_retries_left: Include only external tasks that have retries left.
        :param no_retries_left: Include only external tasks that have no retries left.
        :param lock_expiration_after: Include only external tasks with a lock that expires after the
                                      provided date.
        :param lock_expiration_before: Include only external tasks with a lock that expires before
                                       the provided date.
        :param activity_id: Filter by activity id the external task is created for.
        :param activity_id_in: Filter whether activity id is one of multiple ones.
        :param execution_id: Filter by the execution id the external task belongs to.
        :param process_instance_id: Filter by the process instance id the external task belongs to.
        :param process_definition_id: Filter by the process definition id the external task belongs
                                      to.
        :param tenant_id_in: Filter whether the tenant id is one of multiple ones.
        :param active: Include only external tasks that are active.
        :param priority_higher_equals: Include only external tasks with a priority higher than or
                                       equals to the given value.
        :param priority_lower_equals: Include only external tasks with a priority lower than or
                                       equals to the given value.
        :param suspended: Include only external tasks that are suspended.
        :param sort_by: Sort the results by `id_`, `lock_expiration_time, `process_instance_id`,
                        `process_definition_key`, `tenant_id` or `task_priority`.
        :param ascending: Sort order.
        :param first_result: Pagination of results. Index of the first result to return.
        :param max_results: Pagination of results. Maximum number of results to return.
        :param request_error_details: Whether to request error details for tasks. Requires
                                      additional requests.
        """
        super().__init__(url=url + URL_SUFFIX)
        self.id_ = id_
        self.topic_name = topic_name
        self.worker_id = worker_id
        self.locked = locked
        self.not_locked = not_locked
        self.with_retries_left = with_retries_left
        self.no_retries_left = no_retries_left
        self.lock_expiration_after = lock_expiration_after
        self.lock_expiration_before = lock_expiration_before
        self.activity_id = activity_id
        self.actitity_id_in = activity_id_in
        self.execution_id = execution_id
        self.process_instance_id = process_instance_id
        self.process_definition_id = process_definition_id
        self.tenant_id_in = tenant_id_in
        self.active = active
        self.priority_higher_equals = priority_higher_equals
        self.priority_lower_equals = priority_lower_equals
        self.suspended = suspended
        self.sort_by = sort_by
        self.ascending = ascending
        self.first_result = first_result
        self.max_results = max_results
        self.request_error_details = request_error_details

    def __call__(self, *args, **kwargs) -> typing.Tuple[ExternalTask]:
        """Send the request."""
        response = super().__call__(pycamunda.base.RequestMethod.GET, *args, **kwargs)
        external_tasks = tuple(ExternalTask.load(task_json) for task_json in response.json())

        if self.request_error_details:
            for external_task in external_tasks:
                if external_task.error_details is None:
                    try:
                        future_response = session.get(self.url + f'/{external_task.id_}/errorDetails')
                        response = future_response.result()  # Wait for the response
                    except Exception:
                        raise pycamunda.PyCamundaException()
                    if not response:
                        pycamunda.base._raise_for_status(response)
                    external_task.error_details = response.text

        return external_tasks


class Count(GetList):

    def __init__(
        self,
        url: str,
        id_: str = None,
        topic_name: str = None,
        worker_id: str = None,
        locked: bool = False,
        not_locked: bool = False,
        with_retries_left: bool = False,
        no_retries_left: bool = False,
        lock_expiration_after: dt.datetime = None,
        lock_expiration_before: dt.datetime = None,
        activity_id: str = None,
        activity_id_in: typing.Iterable[str] = None,
        execution_id: str = None,
        process_instance_id: str = None,
        process_definition_id: str = None,
        tenant_id_in: typing.Iterable[str] = None,
        active: bool = False,
        priority_higher_equals: int = None,
        priority_lower_equals: int = None,
        suspended: bool = False,
        sort_by: str = None,
        ascending: bool = True,
        first_result: int = None,
        max_results: int = None
    ):
        """Get the size of the result returned by the Get List request.

        :param url: Camunda Rest engine URL.
        :param id_: Filter by the id of the external task.
        :param topic_name: Filter by the topic name of the external task.
        :param worker_id: Filter by the id of the worker the task was locked by last.
        :param locked: Include only locked external tasks.
        :param not_locked: Include only unlocked tasks.
        :param with_retries_left: Include only external tasks that have retries left.
        :param no_retries_left: Include only external tasks that have no retries left.
        :param lock_expiration_after: Include only external tasks with a lock that expires after a
                                      date.
        :param lock_expiration_before: Include only external tasks with a lock that expires before a
                                       date.
        :param activity_id: Filter by activity id the external task is created for.
        :param activity_id_in: Filter whether activity id is one of multiple ones.
        :param execution_id: Filter by the execution id the external task belongs to.
        :param process_instance_id: Filter by the process instance id the external task belongs to.
        :param process_definition_id: Filter by the process definition id the external task belongs
                                      to.
        :param tenant_id_in: Filter whether the tenant id is one of multiple ones.
        :param active: Include only external tasks that are active.
        :param priority_higher_equals: Include only external tasks with a priority higher than or
                                       equals to the given value.
        :param priority_lower_equals: Include only external tasks with a priority lower than or
                                       equals to the given value.
        :param suspended: Include only external tasks that are suspended.
        :param sort_by: Sort the results by `id_`, `lock_expiration_time, `process_instance_id`,
                        `process_definition_key`, `tenant_id` or `task_priority`.
        :param ascending: Sort order.
        :param first_result: Pagination of results. Index of the first result to return.
        :param max_results: Pagination of results. Maximum number of results to return.
        """
        super().__init__(
            url=url,
            id_=id_,
            topic_name=topic_name,
            worker_id=worker_id,
            locked=locked,
            not_locked=not_locked,
            with_retries_left=with_retries_left,
            no_retries_left=no_retries_left,
            lock_expiration_after=lock_expiration_after,
            lock_expiration_before=lock_expiration_before,
            activity_id=activity_id,
            activity_id_in=activity_id_in,
            execution_id=execution_id,
            process_instance_id=process_instance_id,
            process_definition_id=process_definition_id,
            tenant_id_in=tenant_id_in,
            active=active,
            priority_higher_equals=priority_higher_equals,
            priority_lower_equals=priority_lower_equals,
            suspended=suspended,
            sort_by=sort_by,
            ascending=ascending,
            first_result=first_result,
            max_results=max_results
        )
        self._url += '/count'

    def query_parameters(self, apply: typing.Callable = ...):
        params = super().query_parameters(apply=apply)
        for key, value in params.items():
            if isinstance(value, dt.datetime):
                params[key] = pycamunda.base.isoformat(datetime_=value)
        return params

    def __call__(self, *args, **kwargs) -> int:
        """Send the request."""
        try:
            future_response = session.request(
                method=pycamunda.base.RequestMethod.GET.value,
                url=self.url,
                params=self.query_parameters()
            )
            response = future_response.result()  # Wait for the response
        except Exception:
            raise pycamunda.PyCamundaException()
        if not response:
            pycamunda.base._raise_for_status(response)

        return int(response.json()['count'])
```

### Summary of Changes:
- Replaced `requests.get` and `requests.request` with `session.get` and `session.request` from `requests_futures`.
- Used `.result()` to handle the `Future` object returned by `requests_futures`.
- Adjusted exception handling to account for asynchronous requests.