import logging
import re
import pycurl
import io
import json

from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex import utils


LOG = logging.getLogger(__name__)


class SnapshotDef(dict):
    """PowerFlex definition of snapshot to create.

    JSON-serializable, should be used as `snapshot_defs` list item
    in `System.snapshot_volumes` method.
    """

    def __init__(self, volume_id, name=None):
        """Initialize SnapshotDef object.

        :type volume_id: str
        :type name: str
        """

        params = utils.prepare_params(
            {
                'volumeId': volume_id,
                'snapshotName': name,
            },
            dump=False
        )
        super(SnapshotDef, self).__init__(**params)


class System(base_client.EntityRequest):
    def __init__(self, token, configuration):
        self.__api_version = None
        super(System, self).__init__(token, configuration)

    def send_get_request(self, url):
        """Send a GET request using pycurl."""
        buffer = io.BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, self.configuration['base_url'] + url)
        curl.setopt(pycurl.HTTPHEADER, [f"Authorization: Bearer {self.token}"])
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        curl.close()

        response = buffer.getvalue().decode('utf-8')
        return status_code, response

    def send_post_request(self, url, action=None, entity=None, entity_id=None, params=None):
        """Send a POST request using pycurl."""
        buffer = io.BytesIO()
        curl = pycurl.Curl()
        full_url = self.configuration['base_url'] + url
        if action:
            full_url += f"?action={action}"
        if entity and entity_id:
            full_url += f"&entity={entity}&entityId={entity_id}"

        curl.setopt(pycurl.URL, full_url)
        curl.setopt(pycurl.HTTPHEADER, [f"Authorization: Bearer {self.token}", "Content-Type: application/json"])
        curl.setopt(pycurl.POST, 1)
        if params:
            curl.setopt(pycurl.POSTFIELDS, json.dumps(params))
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        curl.close()

        response = buffer.getvalue().decode('utf-8')
        return status_code, response

    def api_version(self, cached=True):
        """Get PowerFlex API version.

        :param cached: get version from cache or send API response
        :type cached: bool
        :rtype: str
        """

        url = '/version'

        if not self.__api_version or not cached:
            status_code, response = self.send_get_request(url)
            if status_code != 200:
                exc = exceptions.PowerFlexFailQuerying('API version')
                LOG.error(exc.message)
                raise exc
            pattern = re.compile(r'^\d+(\.\d+)*$')
            if not pattern.match(response):
                msg = (
                    'Failed to query PowerFlex API version. Invalid version '
                    'format: {response}.'.format(response=response)
                )
                LOG.error(msg)
                raise exceptions.PowerFlexClientException(msg)
            self.__api_version = response
        return self.__api_version

    def remove_cg_snapshots(self, system_id, cg_id, allow_ext_managed=None):
        """Remove PowerFlex ConsistencyGroup snapshots.

        :type system_id: str
        :type cg_id: str
        :type allow_ext_managed: bool
        :rtype: dict
        """

        action = 'removeConsistencyGroupSnapshots'

        params = dict(
            snapGroupId=cg_id,
            allowOnExtManagedVol=allow_ext_managed
        )

        status_code, response = self.send_post_request(self.base_action_url,
                                                       action=action,
                                                       entity=self.entity,
                                                       entity_id=system_id,
                                                       params=params)
        if status_code != 200:
            msg = ('Failed to remove consistency group snapshots from '
                   'PowerFlex {entity} with id {_id}. '
                   'Error: {response}'.format(entity=self.entity,
                                              _id=system_id,
                                              response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return json.loads(response)

    def snapshot_volumes(self,
                         system_id,
                         snapshot_defs,
                         access_mode=None,
                         retention_period=None,
                         allow_ext_managed=None):
        """Create snapshots of PowerFlex volumes.

        :type retention_period: str
        :type access_mode: str
        :type system_id: str
        :type snapshot_defs: list[dict]
        :type allow_ext_managed: bool
        :rtype: dict
        """

        action = 'snapshotVolumes'

        params = dict(
            snapshotDefs=snapshot_defs,
            allowOnExtManagedVol=allow_ext_managed,
            accessModeLimit=access_mode,
            retentionPeriodInMin=retention_period
        )

        status_code, response = self.send_post_request(self.base_action_url,
                                                       action=action,
                                                       entity=self.entity,
                                                       entity_id=system_id,
                                                       params=params)
        if status_code != 200:
            msg = ('Failed to snapshot volumes on PowerFlex {entity} '
                   'with id {_id}.'
                   ' Error: {response}'.format(entity=self.entity,
                                               _id=system_id,
                                               response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return json.loads(response)
