# -*- coding: utf-8 -*-

"""This module provides access to the deployment REST api of Camunda."""

from __future__ import annotations
import datetime as dt
import dataclasses
import typing

from requests_futures.sessions import FuturesSession

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

# Create a FuturesSession object for asynchronous requests
session = FuturesSession()


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


class GetList(pycamunda.base.CamundaRequest):
    # No changes needed for this class as it uses the base request logic
    ...


class Get(pycamunda.base.CamundaRequest):
    # No changes needed for this class as it uses the base request logic
    ...


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
        return {f'resource-{i}': resource for i, resource in enumerate(self._files)}

    def __call__(self, *args, **kwargs) -> DeploymentWithDefinitions:
        """Send the request."""
        assert bool(self.files), 'Cannot create deployment without resources.'
        try:
            future = session.request(
                method=pycamunda.base.RequestMethod.POST.value,
                url=self.url,
                params=self.query_parameters(),
                data=self.body_parameters(),
                auth=self.auth,
                files=self.files
            )
            response = future.result()  # Wait for the response
        except Exception as exc:
            raise pycamunda.PyCamundaException(exc)
        if not response:
            pycamunda.base._raise_for_status(response)

        return DeploymentWithDefinitions.load(data=response.json())


class GetResources(pycamunda.base.CamundaRequest):
    # No changes needed for this class as it uses the base request logic
    ...


class GetResource(pycamunda.base.CamundaRequest):
    # No changes needed for this class as it uses the base request logic
    ...


class Delete(pycamunda.base.CamundaRequest):
    # No changes needed for this class as it uses the base request logic
    ...
