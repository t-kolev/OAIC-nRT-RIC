.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. Copyright (C) 2019 AT&T Intellectual Property

Installation Guide
==================

.. contents::
   :depth: 3
   :local:

Environment Variables
---------------------

You can set the following environment variables when launching a container to change the A1 behavior:

1. ``A1_RMR_RETRY_TIMES``: the number of times failed rmr operations such as timeouts and send failures should be retried before A1 gives up and returns a 503. The default is ``4``.

2. ``INSTANCE_DELETE_NO_RESP_TTL``: Please refer to the delete flowchart in docs/; this is ``T1`` there. The default is 5 (seconds). Basically, the number of seconds that a1 waits to remove an instance from the database after a delete is called in the case that no downstream apps responded.

3. ``INSTANCE_DELETE_RESP_TTL``: Please refer to the delete flowchart in docs/; this is ``T2`` there. The default is 5 (seconds). Basically, the number of seconds that a1 waits to remove an instance from the database after a delete is called in the case that downstream apps responded.

4. ``USE_FAKE_SDL``: This allows testing of the A1 feature without a DBaaS SDL container.  The default is False.

5. ``prometheus_multiproc_dir``: The directory where Prometheus gathers metrics.  The default is /tmp.


Kubernetes Deployment
---------------------
The official Helm chart for the A1 Mediator is in a deployment repository, which holds all of the Helm charts 
for the RIC platform. There is a helm chart in `integration_tests` here for running the integration tests as
discussed above.

Local Deployment
----------------

Build and run the A1 mediator locally using the docker CLI as follows.

Build the image
~~~~~~~~~~~~~~~
::

   docker build --no-cache -t a1:latest .

.. _running-1:

Start the container
~~~~~~~~~~~~~~~~~~~

The A1 container depends on a companion DBaaS (SDL) container, but if that is not convenient set
an environment variable as shown below to mock that service.  Also a sample RMR routing table is
supplied in file `local.rt` for mounting as a volume.  The following command uses both:

::

   docker run -e USE_FAKE_SDL=True -p 10000:10000 -v /path/to/local.rt:/opt/route/local.rt a1:latest

View container API
~~~~~~~~~~~~~~~~~~

A web user interface generated from the OpenAPI specification can be accessed at this URL:

::

    http://docker-host-name-or-ip:10000/ui

Check container health
~~~~~~~~~~~~~~~~~~~~~~

The following command requests the container health.  Expect an internal server error if the
Storage Data Layer (SDL) service is not available or has not been mocked as shown above.

::

    curl docker-host-name-or-ip:10000/a1-p/healthcheck
