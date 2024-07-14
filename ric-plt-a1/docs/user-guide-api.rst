.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0

User Guide and APIs
===================

.. contents::
   :depth: 3
   :local:

This document explains how to communicate with the A1 Mediator.
Information for maintainers of this platform component is in the Developer Guide.

Example Messages
----------------

Send the following JSON to create policy type 20008, which supports instances with
a single integer value:

.. code-block:: yaml

    {
      "name": "tsapolicy",
      "description": "tsa parameters",
      "policy_type_id": 20008,
      "create_schema": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
          "threshold": {
            "type": "integer",
            "default": 0
          }
        },
        "additionalProperties": false
      }
    }


For example, if you put the JSON above into a file called "create.json" you can use
the curl command-line tool to send the request::

    curl -X PUT --header "Content-Type: application/json" --data-raw @create.json http://localhost/a1-p/policytypes/20008


Send the following JSON to create an instance of policy type 20008:

.. code-block:: yaml

    {
      "threshold" : 5
    }


For example, you can use the curl command-line tool to send this request::

    curl -X PUT --header "Content-Type: application/json" --data '{"threshold" : 5}' http://localhost/a1-p/policytypes/20008/policies/tsapolicy145


Integrating Xapps with A1
-------------------------

The schema for messages sent by A1 to Xapps is labeled ``downstream_message_schema``
in the Southbound API Specification section below. A1 sends policy instance requests
using message type 20010.

The schemas for messages sent by Xapps to A1 appear in the Southbound API
Specification section below. Xapps must use a message type and content appropriate
for the scenario:

#. When an Xapp receives a CREATE message for a policy instance, the Xapp
   must respond by sending a message of type 20011 to A1. The content is
   defined by schema ``downstream_notification_schema``.  The most convenient
   way is to use RMR's return-to-sender (RTS) feature after setting the
   message type appropriately.
#. Since policy instances can "deprecate" other instances, there are
   times when Xapps need to asynchronously tell A1 that a policy is no
   longer active. Use the same message type and schema as above.
#. Xapps can request A1 to re-send all instances of policy type T using a
   query, message type 20012.  The schema for that message is defined by
   ``policy_query_schema`` (just a body with ``{policy_type_id: ... }``).
   When A1 receives this, A1 will send the Xapp a CREATE message N times,
   where N is the number of policy instances for type T. The Xapp should reply
   normally to each of those as the first item above. That is, after the Xapp
   performs the query, the N CREATE messages sent and the N replies
   are "as normal".  The query just kicks off this process rather than
   an external caller to A1.


Northbound API Specification
----------------------------

This section shows the Open API specification for the A1 Mediator's
northbound interface, which accepts policy type and policy instance requests.
Alternately, if you have checked out the code and are running the server,
you can see a formatted version at this URL: ``http://localhost:10000/ui/``.


.. literalinclude:: ../a1/openapi.yaml
   :language: yaml
   :linenos:


Southbound API Specification
----------------------------

This section shows Open API schemas for the A1 Mediator's southbound interface,
which communicates with Xapps via RMR. A1 sends policy instance requests using
message type 20010. Xapps may send requests to A1 using message types 20011 and
20012.


.. literalinclude:: a1_xapp_contract_openapi.yaml
   :language: yaml
   :linenos:
