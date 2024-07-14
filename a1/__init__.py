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
contains the app; broken out here for ease of unit testing
"""
import connexion
from prometheus_client import CollectorRegistry, generate_latest, multiprocess


app = connexion.App(__name__, specification_dir=".")
app.add_api("openapi.yaml", arguments={"title": "My Title"})


# python decorators feel like black magic to me
@app.app.route('/a1-p/metrics', methods=['GET'])
def metrics():  # pylint: disable=unused-variable
    # /metrics API shouldn't be visible in the API documentation,
    # hence it's added here in the create_app step
    # requires environment variable prometheus_multiproc_dir
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return generate_latest(registry)
