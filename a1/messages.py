# ==================================================================================
#       Copyright (c) 2019 Nokia
#       Copyright (c) 2018-2019 AT&T Intellectual Property.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
# ==================================================================================
"""
rmr messages
"""


def a1_to_handler(operation, policy_type_id, policy_instance_id, payload=None):
    """
    used to create the payloads that get sent to downstream policy handlers
    """
    return {
        "operation": operation,
        "policy_type_id": policy_type_id,
        "policy_instance_id": policy_instance_id,
        "payload": payload,
    }


def ei_to_handler(ei_job_id, payload=None):
    """
    used to create the payloads that get sent to downstream policy handlers
    """
    return {
        "ei_job_id": ei_job_id,
        "payload": payload,
    }
