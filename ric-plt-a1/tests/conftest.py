"""
pytest conftest
"""
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
import tempfile
import os
import pytest
from a1 import app


@pytest.fixture
def client():
    """
    http://flask.pocoo.org/docs/1.0/testing/
    """

    db_fd, app.app.config["DATABASE"] = tempfile.mkstemp()
    app.app.config["TESTING"] = True
    cl = app.app.test_client()

    yield cl

    os.close(db_fd)
    os.unlink(app.app.config["DATABASE"])


@pytest.fixture
def adm_type_good():
    """
    represents a good put for adm control type
    """
    return {
        "name": "Policy for Rate Control",
        "policy_type_id": 6660666,
        "description": "This policy is associated with rate control. An instance of the policy specifies the traffic class to which it applies and parameters to use to control how much it must be throttled in case of an overload. Each instance of the policy that is created MUST be associated with a unique class ID (identifyed by the key 'class', which is used by the xAPP to differentiate traffic. If an agent tries to create a policy with the SAME class id, it will be rejected by the xAPP, even if it has a unique policy instance id. ",
        "create_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "class": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 256,
                    "description": "integer id representing class to which we are applying policy",
                },
                "enforce": {
                    "type": "boolean",
                    "description": "Whether to enable or disable enforcement of policy on this class",
                },
                "window_length": {
                    "type": "integer",
                    "minimum": 15,
                    "maximum": 300,
                    "description": "Sliding window length in seconds",
                },
                "trigger_threshold": {"type": "integer", "minimum": 1},
                "blocking_rate": {"type": "number", "minimum": 0, "maximum": 100},
            },
            "required": ["class", "enforce", "blocking_rate", "trigger_threshold", "window_length"],
        },
    }


@pytest.fixture
def adm_instance_good():
    """
    represents a good put for adm control instance
    """
    return {"class": 12, "enforce": True, "window_length": 20, "blocking_rate": 20, "trigger_threshold": 10}
