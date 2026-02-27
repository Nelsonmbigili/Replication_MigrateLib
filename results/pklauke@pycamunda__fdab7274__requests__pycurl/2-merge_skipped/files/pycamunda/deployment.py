# -*- coding: utf-8 -*-

"""This module provides access to the deployment REST api of Camunda."""

from __future__ import annotations
import datetime as dt
import dataclasses
import typing
import pycurl
import io
import json

import pycamunda.variable
import pycamunda.base
import pycamunda.resource
import pycamunda.processdef
import pycamunda.casedef
import pycamunda.decisiondef
import pycamunda.decisionreqdef
from pycamunda.request import QueryParameter, PathParameter, BodyParameter

URL_SUFFIX = '/deployment'


__all__ = ['GetList', 'Get', 'Create', 'GetResources', 'GetResource', 'Delete']


@dataclasses.dataclass
class Deployment:
    """Data class of deployment as returned by the REST api of Camunda."""
    id_: str
    name: str
    source: str
    tenant_id: str
    deployment_time: dt.datetime = None

    @classmethod
    def load(cls, data: typing.Mapping[str, typing.Any]) -> Deployment:
        deployment = cls(
            id_=data['id'],
            name=data['name'],
            source=data['source'],
            tenant_id=data['tenantId'],
        )
        if data['deploymentTime'] is not None:
            deployment.deployment_time = pycamunda.base.from_isoformat(data['deploymentTime'])

        return deployment


@dataclasses.dataclass
class Resource:
    """Data class of resource as returned by the REST api of Camunda."""
    id_: str
    name: str
    deployment_id: str

    @classmethod
    def load(cls, data: typing.Mapping[str, typing.Any]) -> Resource:
        return cls(
            id_=data['id'],
            name=data['name'],
            deployment_id=data['deploymentId']
        )


@dataclasses.dataclass
class DeploymentWithDefinitions:
    """Data class of deployment with definitions as returned by the REST api of Camunda."""
    links: typing.List[pycamunda.resource.Link]
    id_: str
    name: str
    source: str
    deployed_process_definitions: typing.Dict[str, pycamunda.processdef.ProcessDefinition]
    deployed_case_definitions: typing.Dict[str, pycamunda.casedef.CaseDefinition]
    deployed_decision_definitions: typing.Dict[str, pycamunda.decisiondef.DecisionDefinition]
    deployed_decision_requirements_definitions: typing.Dict[
        str, pycamunda.decisionreqdef.DecisionRequirementsDefinition
    ]
    tenant_id: str = None
    deployment_time: dt.datetime = None

    @classmethod
    def load(cls, data: typing.Mapping[str, typing.Any]) -> DeploymentWithDefinitions:
        if data['deployedProcessDefinitions'] is not None:
            deployed_process_definitions = {
                name: pycamunda.processdef.ProcessDefinition.load(process_definition)
                for name, process_definition in data['deployedProcessDefinitions'].items()
            }
        else:
            deployed_process_definitions = None
        if data['deployedCaseDefinitions'] is not None:
            deployed_case_definitions = {
                name: pycamunda.casedef.CaseDefinition.load(case_definition)
                for name, case_definition in data['deployedCaseDefinitions'].items()
            }
        else:
            deployed_case_definitions = None
        if data['deployedDecisionDefinitions'] is not None:
            deployed_decision_definitions = {
                name: pycamunda.decisiondef.DecisionDefinition.load(decision_definition)
                for name, decision_definition in data['deployedDecisionDefinitions'].items()
            }
        else:
            deployed_decision_definitions = None
        if data['deployedDecisionRequirementsDefinitions'] is not None:
            deployed_decision_requirements_definitions = {
                name: pycamunda.decisionreqdef.DecisionRequirementsDefinition.load(dec_req_def)
                for name, dec_req_def in data['deployedDecisionRequirementsDefinitions'].items()
            }
        else:
            deployed_decision_requirements_definitions = None
        return cls(
            links=[pycamunda.resource.Link.load(link) for link in data['links']],
            id_=data['id'],
            name=data['name'],
            source=data['source'],
            deployed_process_definitions=deployed_process_definitions,
            deployed_case_definitions=deployed_case_definitions,
            deployed_decision_definitions=deployed_decision_definitions,
            deployed_decision_requirements_definitions=deployed_decision_requirements_definitions,
            tenant_id=data['tenantId'],
            deployment_time=pycamunda.base.from_isoformat(data['deploymentTime'])
        )


class PyCurlRequest:
    """Helper class to handle pycurl requests."""

    @staticmethod
    def send_request(url, method, headers=None, params=None, data=None, files=None):
        buffer = io.BytesIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, url)
        curl.setopt(curl.WRITEDATA, buffer)

        if headers:
            curl.setopt(curl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])

        if method == 'POST':
            curl.setopt(curl.POST, 1)
            if data:
                curl.setopt(curl.POSTFIELDS, json.dumps(data))
            if files:
                curl.setopt(curl.HTTPPOST, files)

        elif method == 'DELETE':
            curl.setopt(curl.CUSTOMREQUEST, 'DELETE')

        elif method == 'GET':
            curl.setopt(curl.HTTPGET, 1)

        try:
            curl.perform()
            curl.close()
        except pycurl.error as exc:
            raise pycamunda.PyCamundaException(exc)

        return buffer.getvalue().decode('utf-8')


class Create(pycamunda.base.CamundaRequest):

    name = BodyParameter('deployment-name')
    enable_duplicate_filtering = BodyParameter('enable-duplicate-filtering')
    deploy_changed_only = BodyParameter('deploy-changed-only')
    source = BodyParameter('deployment-source')
    tenant_id = BodyParameter('tenant-id')

    def __init__(
        self,
        url: str,
        name: str,
        source: str = None,
        enable_duplicate_filtering: bool = False,
        deploy_changed_only: bool = False,
        tenant_id: str = None
    ):
        """Create a deployment with one or multiple resources (e.g. bpmn diagrams).

        :param url: Camunda Rest engine url
        :param name: Name of the deployment.
        :param source: Source of the deployment.
        :param enable_duplicate_filtering: Whether to check if a deployment with the same name
                                           already exists. If one does, no new deployment is done.
        :param deploy_changed_only: Whether to check if already deployed resources that are also
                                    contained in this deployment have changed. The ones that do not
                                    will not created again.
        :param tenant_id: Id of the tenant to create the deployment for.
        """
        super().__init__(url=url + URL_SUFFIX + '/create')
        self.name = name
        self.source = source
        self.enable_duplicate_filtering = enable_duplicate_filtering
        self.deploy_changed_only = deploy_changed_only
        self.tenant_id = tenant_id

        self._files = []

    def add_resource(self, file) -> None:
        """Add a resource to the deployment.

        :param file: Binary data of the resource.
        """
        self._files.append(file)

    @property
    def files(self):
        return [(f'resource-{i}', (pycurl.FORM_FILE, resource)) for i, resource in enumerate(self._files)]

    def __call__(self, *args, **kwargs) -> DeploymentWithDefinitions:
        """Send the request."""
        assert bool(self.files), 'Cannot create deployment without resources.'
        try:
            response = PyCurlRequest.send_request(
                url=self.url,
                method='POST',
                params=self.query_parameters(),
                data=self.body_parameters(),
                files=self.files
            )
        except pycamunda.PyCamundaException as exc:
        except requests.exceptions.RequestException as exc:
            raise pycamunda.PyCamundaException(exc)
        if not response:
            pycamunda.base._raise_for_status(response)

        return DeploymentWithDefinitions.load(data=response.json())


class GetResources(pycamunda.base.CamundaRequest):

    id_ = PathParameter('id')

    def __init__(self, url: str, id_: str):
        """Get the resources of a deployment.

        :param url: Camunda Rest engine URL.
        :param id_: Id of the the deployment.
        """
        super().__init__(url=url + URL_SUFFIX + '/{id}/resources')
        self.id_ = id_

    def __call__(self, *args, **kwargs) -> typing.Tuple[Resource]:
        """Send the request."""
        response = super().__call__(pycamunda.base.RequestMethod.GET, *args, **kwargs)

        return tuple(Resource.load(resource_json) for resource_json in response.json())


class GetResource(pycamunda.base.CamundaRequest):

    id_ = PathParameter('id')
    resource_id = PathParameter('resourceId')

    def __init__(self, url: str, id_: str, resource_id: str, binary: bool = False):
        """Get a resource of a deployment.

        :param url: Camunda Rest engine URL.
        :param id_: Id of the the deployment.
        :param resource_id: Id of the resource.
        :param binary: Whether to request binary content of the resource.
        """
        super().__init__(url=url + URL_SUFFIX + '/{id}/resources/{resourceId}')
        self.id_ = id_
        self.resource_id = resource_id
        self.binary = binary

    @property
    def url(self):
        return super().url + ('/data' if self.binary else '')

    def __call__(self, *args, **kwargs) -> typing.Union[Resource, typing.ByteString]:
        """Send the request."""
        response = super().__call__(pycamunda.base.RequestMethod.GET, *args, **kwargs)

        if self.binary:
            return response.content
        return Resource.load(response.json())


class Delete(pycamunda.base.CamundaRequest):

    id_ = PathParameter('id')
    cascade = QueryParameter('cascade')
    skip_custom_listeners = QueryParameter('skipCustomListeners')
    skip_io_mappings = QueryParameter('skipIoMappings')

    def __init__(
        self,
        url: str,
        id_: str,
        cascade: bool = False,
        skip_custom_listeners: bool = False,
        skip_io_mappings: bool = False
    ):
        """Delete a deployment.

        :param url: Camunda Rest engine URL.
        :param id_: Id of the the deployment.
        :param cascade: Whether to cascade the action to all process instances (including historic).
        :param skip_custom_listeners: Whether to skip custom listeners and notify only builtin ones.
        :param skip_io_mappings: Whether to skip input/output mappings.
        """
        super().__init__(url=url + URL_SUFFIX + '/{id}')
        self.id_ = id_
        self.cascade = cascade
        self.skip_custom_listeners = skip_custom_listeners
        self.skip_io_mappings = skip_io_mappings

    def __call__(self, *args, **kwargs) -> None:
        """Send the request."""
        super().__call__(pycamunda.base.RequestMethod.DELETE, *args, **kwargs)
            raise exc

        return DeploymentWithDefinitions.load(data=json.loads(response))