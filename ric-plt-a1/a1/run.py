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
A1 entrypoint
"""
from os import environ
from gevent.pywsgi import WSGIServer
from mdclogpy import Logger
from a1 import app
from a1 import a1rmr


mdc_logger = Logger()
mdc_logger.mdclog_format_init(configmap_monitor=True)


def main():
    """Entrypoint"""
    mdc_logger.debug("A1Mediator starts")
    # start rmr thread
    mdc_logger.debug("Starting RMR thread with RMR_RTG_SVC {0}, RMR_SEED_RT {1}".format(environ.get('RMR_RTG_SVC'), environ.get('RMR_SEED_RT')))
    mdc_logger.debug("RMR initialization must complete before webserver can start")
    a1rmr.start_rmr_thread()
    mdc_logger.debug("RMR initialization complete")
    # start webserver
    port = 10000
    mdc_logger.debug("Starting gevent webserver on port {0}".format(port))
    http_server = WSGIServer(("", port), app)
    http_server.serve_forever()
