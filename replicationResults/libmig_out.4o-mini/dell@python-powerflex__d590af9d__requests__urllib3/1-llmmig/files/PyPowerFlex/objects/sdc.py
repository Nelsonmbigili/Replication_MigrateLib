# Copyright (c) 2024 Dell Inc. or its subsidiaries.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import urllib3
from PyPowerFlex import base_client
from PyPowerFlex import exceptions

LOG = logging.getLogger(__name__)

http = urllib3.PoolManager()

class Sdc(base_client.EntityRequest):
    def delete(self, sdc_id):
        """Remove PowerFlex SDC.

        :type sdc_id: str
        :rtype: None
        """
        url = f"http://your.api.endpoint/sdc/{sdc_id}"  # Replace with actual endpoint
        response = http.request('DELETE', url)
        return response.status

    def get_mapped_volumes(self, sdc_id, filter_fields=None, fields=None):
        """Get PowerFlex volumes mapped to SDC.

        :type sdc_id: str
        :type filter_fields: dict
        :type fields: list|tuple
        :rtype: list[dict]
        """
        url = f"http://your.api.endpoint/sdc/{sdc_id}/volumes"  # Replace with actual endpoint
        response = http.request('GET', url)
        return response.data  # Adjust as necessary to parse the response

    def rename(self, sdc_id, name):
        """Rename PowerFlex SDC.

        :type sdc_id: str
        :type name: str
        :rtype: dict
        """
        action = 'setSdcName'
        params = dict(
            sdcName=name
        )
        url = f"http://your.api.endpoint/sdc/{sdc_id}/rename"  # Replace with actual endpoint
        response = http.request('POST', url, fields=params)
        return response.data  # Adjust as necessary to parse the response

    def set_performance_profile(self, sdc_id, perf_profile):
        """Apply a performance profile to the specified SDC.

        :type sdc_id: str
        :type perf_profile: str
        :rtype: dict
        """
        action = 'setSdcPerformanceParameters'
        params = dict(
            perfProfile=perf_profile
        )
        url = f"http://your.api.endpoint/sdc/{sdc_id}/performance"  # Replace with actual endpoint
        response = http.request('POST', url, fields=params)
        return response.data  # Adjust as necessary to parse the response

    def query_selected_statistics(self, properties, ids=None):
        """Query PowerFlex SDC statistics.

        :type properties: list
        :type ids: list of SDC IDs or None for all SDC
        :rtype: dict
        """
        action = "querySelectedStatistics"
        params = dict(properties=properties)

        if ids:
            params["ids"] = ids
        else:
            params["allIds"] = ""

        url = "http://your.api.endpoint/sdc/statistics"  # Replace with actual endpoint
        response = http.request('POST', url, fields=params)
        return response.data  # Adjust as necessary to parse the response
