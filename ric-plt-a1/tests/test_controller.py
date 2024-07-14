"""
tests for controller
"""
# ==================================================================================
#       Copyright (c) 2019-2020 Nokia
#       Copyright (c) 2018-2020 AT&T Intellectual Property.
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
import time
import json
from ricxappframe.rmr.rmr_mocks import rmr_mocks
from ricxappframe.xapp_sdl import SDLWrapper
from ricsdl.exceptions import RejectedByBackend, NotConnected, BackendError
from a1 import a1rmr, data

RCV_ID = "test_receiver"
ADM_CRTL_TID = 6660666
ADM_CTRL_IID = "admission_control_policy"
ADM_CTRL_POLICIES = "/a1-p/policytypes/{0}/policies".format(ADM_CRTL_TID)
ADM_CTRL_INSTANCE = ADM_CTRL_POLICIES + "/" + ADM_CTRL_IID
ADM_CTRL_INSTANCE_STATUS = ADM_CTRL_INSTANCE + "/status"
ADM_CTRL_TYPE = "/a1-p/policytypes/{0}".format(ADM_CRTL_TID)
ACK_MT = 20011


def _fake_dequeue():
    """for monkeypatching with a good status"""
    pay = json.dumps(
        {"policy_type_id": ADM_CRTL_TID, "policy_instance_id": ADM_CTRL_IID, "handler_id": RCV_ID, "status": "OK"}
    ).encode()
    fake_msg = {"payload": pay, "message type": ACK_MT}
    return [(fake_msg, None)]


def _fake_dequeue_none():
    """for monkeypatching with no waiting messages"""
    return []


def _fake_dequeue_deleted():
    """for monkeypatching  with a DELETED status"""
    new_msgs = []
    good_pay = json.dumps(
        {"policy_type_id": ADM_CRTL_TID, "policy_instance_id": ADM_CTRL_IID, "handler_id": RCV_ID, "status": "DELETED"}
    ).encode()

    # non existent type id
    pay = json.dumps(
        {"policy_type_id": 911, "policy_instance_id": ADM_CTRL_IID, "handler_id": RCV_ID, "status": "DELETED"}
    ).encode()
    fake_msg = {"payload": pay, "message type": ACK_MT}
    new_msgs.append((fake_msg, None))

    # bad instance id
    pay = json.dumps(
        {"policy_type_id": ADM_CRTL_TID, "policy_instance_id": "darkness", "handler_id": RCV_ID, "status": "DELETED"}
    ).encode()
    fake_msg = {"payload": pay, "message type": ACK_MT}
    new_msgs.append((fake_msg, None))

    # good body but bad message type
    fake_msg = {"payload": good_pay, "message type": ACK_MT * 3}
    new_msgs.append((fake_msg, None))

    # insert a bad one with a malformed body to make sure we keep going
    new_msgs.append(({"payload": "asdf", "message type": ACK_MT}, None))

    # not even a json
    new_msgs.append(("asdf", None))

    # good
    fake_msg = {"payload": good_pay, "message type": ACK_MT}
    new_msgs.append((fake_msg, None))

    return new_msgs


def _test_put_patch(monkeypatch):
    rmr_mocks.patch_rmr(monkeypatch)
    # assert that rmr bad states don't cause problems
    monkeypatch.setattr("ricxappframe.rmr.rmr.rmr_send_msg", rmr_mocks.send_mock_generator(10))


def _no_ac(client):
    # no type there yet
    res = client.get(ADM_CTRL_TYPE)
    assert res.status_code == 404

    # no types at all
    res = client.get("/a1-p/policytypes")
    assert res.status_code == 200
    assert res.json == []

    # instance 404 because type not there yet
    res = client.get(ADM_CTRL_POLICIES)
    assert res.status_code == 404


def _put_ac_type(client, typedef):
    _no_ac(client)

    # put the type
    res = client.put(ADM_CTRL_TYPE, json=typedef)
    assert res.status_code == 201

    # cant replace types
    res = client.put(ADM_CTRL_TYPE, json=typedef)
    assert res.status_code == 400

    # type there now
    res = client.get(ADM_CTRL_TYPE)
    assert res.status_code == 200
    assert res.json == typedef

    # type in type list
    res = client.get("/a1-p/policytypes")
    assert res.status_code == 200
    assert res.json == [ADM_CRTL_TID]

    # instance 200 but empty list
    res = client.get(ADM_CTRL_POLICIES)
    assert res.status_code == 200
    assert res.json == []


def _delete_ac_type(client):
    res = client.delete(ADM_CTRL_TYPE)
    assert res.status_code == 204

    # cant get
    res = client.get(ADM_CTRL_TYPE)
    assert res.status_code == 404

    # cant invoke delete on it again
    res = client.delete(ADM_CTRL_TYPE)
    assert res.status_code == 404

    _no_ac(client)


def _put_ac_instance(client, monkeypatch, instancedef):
    # no instance there yet
    res = client.get(ADM_CTRL_INSTANCE)
    assert res.status_code == 404
    res = client.get(ADM_CTRL_INSTANCE_STATUS)
    assert res.status_code == 404

    # create a good instance
    _test_put_patch(monkeypatch)
    res = client.put(ADM_CTRL_INSTANCE, json=instancedef)
    assert res.status_code == 202

    # replace is allowed on instances
    res = client.put(ADM_CTRL_INSTANCE, json=instancedef)
    assert res.status_code == 202

    # instance 200 and in list
    res = client.get(ADM_CTRL_POLICIES)
    assert res.status_code == 200
    assert res.json == [ADM_CTRL_IID]


def _delete_instance(client):
    # cant delete type until there are no instances
    res = client.delete(ADM_CTRL_TYPE)
    assert res.status_code == 400

    # delete it
    res = client.delete(ADM_CTRL_INSTANCE)
    assert res.status_code == 202

    # should be able to do multiple deletes until it's actually gone
    res = client.delete(ADM_CTRL_INSTANCE)
    assert res.status_code == 202


def _instance_is_gone(client, seconds_to_try=10):
    for _ in range(seconds_to_try):
        # idea here is that we have to wait for the seperate thread to process the event
        try:
            res = client.get(ADM_CTRL_INSTANCE_STATUS)
            assert res.status_code == 404
        except AssertionError:
            time.sleep(1)

    res = client.get(ADM_CTRL_INSTANCE_STATUS)
    assert res.status_code == 404

    # list still 200 but no instance
    res = client.get(ADM_CTRL_POLICIES)
    assert res.status_code == 200
    assert res.json == []

    # cant get instance
    res = client.get(ADM_CTRL_INSTANCE)
    assert res.status_code == 404


def _verify_instance_and_status(client, expected_instance, expected_status, expected_deleted, seconds_to_try=5):
    # get the instance
    res = client.get(ADM_CTRL_INSTANCE)
    assert res.status_code == 200
    assert res.json == expected_instance

    for _ in range(seconds_to_try):
        # idea here is that we have to wait for the seperate thread to process the event
        res = client.get(ADM_CTRL_INSTANCE_STATUS)
        assert res.status_code == 200
        assert res.json["has_been_deleted"] == expected_deleted
        try:
            assert res.json["instance_status"] == expected_status
            return
        except AssertionError:
            time.sleep(1)
    assert res.json["instance_status"] == expected_status


# Module level Hack


def setup_module():
    """module level setup"""

    # swap sdl for the fake backend
    data.SDL = SDLWrapper(use_fake_sdl=True)

    def noop():
        pass

    # launch the thread with a fake init func and a patched rcv func; we will "repatch" later
    a1rmr.start_rmr_thread(init_func_override=noop, rcv_func_override=_fake_dequeue_none)


# Actual Tests


def test_workflow(client, monkeypatch, adm_type_good, adm_instance_good):
    """
    test a full A1 workflow
    """

    # put type and instance
    _put_ac_type(client, adm_type_good)
    _put_ac_instance(client, monkeypatch, adm_instance_good)

    """
    we test the state transition diagram of all 5 states here;
    1. not in effect, not deleted
    2. in effect, not deleted
    3. in effect, deleted
    4. not in effect, deleted
    5. gone (timeout expires)
    """

    # try a status get but we didn't get any ACKs yet to test NOT IN EFFECT
    _verify_instance_and_status(client, adm_instance_good, "NOT IN EFFECT", False)

    # now pretend we did get a good ACK
    a1rmr.replace_rcv_func(_fake_dequeue)
    _verify_instance_and_status(client, adm_instance_good, "IN EFFECT", False)

    # delete the instance
    _delete_instance(client)

    # status after a delete, but there are no messages yet, should still return
    _verify_instance_and_status(client, adm_instance_good, "IN EFFECT", True)

    # now pretend we deleted successfully
    a1rmr.replace_rcv_func(_fake_dequeue_deleted)

    # status should be reflected first (before delete triggers)
    _verify_instance_and_status(client, adm_instance_good, "NOT IN EFFECT", True)

    # instance should be totally gone after a few seconds
    _instance_is_gone(client)

    # delete the type
    _delete_ac_type(client)


def test_cleanup_via_t1(client, monkeypatch, adm_type_good, adm_instance_good):
    """
    create a type, create an instance, but no acks ever come in, delete instance
    """
    _put_ac_type(client, adm_type_good)

    a1rmr.replace_rcv_func(_fake_dequeue_none)

    _put_ac_instance(client, monkeypatch, adm_instance_good)

    """
    here we test the state transition diagram when it never goes into effect:
    1. not in effect, not deleted
    2. not in effect, deleted
    3. gone (timeout expires)
    """

    _verify_instance_and_status(client, adm_instance_good, "NOT IN EFFECT", False)

    # delete the instance
    _delete_instance(client)

    _verify_instance_and_status(client, adm_instance_good, "NOT IN EFFECT", True)

    # instance should be totally gone after a few seconds
    _instance_is_gone(client)

    # delete the type
    _delete_ac_type(client)


def test_bad_instances(client, monkeypatch, adm_type_good):
    """
    test various failure modes
    """
    # put the type (needed for some of the tests below)
    rmr_mocks.patch_rmr(monkeypatch)
    res = client.put(ADM_CTRL_TYPE, json=adm_type_good)
    assert res.status_code == 201

    # bad body
    res = client.put(ADM_CTRL_INSTANCE, json={"not": "expected"})
    assert res.status_code == 400

    # bad media type
    res = client.put(ADM_CTRL_INSTANCE, data="notajson")
    assert res.status_code == 415

    # delete a non existent instance
    res = client.delete(ADM_CTRL_INSTANCE + "DARKNESS")
    assert res.status_code == 404

    # get a non existent instance
    a1rmr.replace_rcv_func(_fake_dequeue)
    res = client.get(ADM_CTRL_INSTANCE + "DARKNESS")
    assert res.status_code == 404

    # delete the type (as cleanup)
    res = client.delete(ADM_CTRL_TYPE)
    assert res.status_code == 204

    # test 503 handlers

    def monkey_set(ns, key, value):
        # set a key override function that throws sdl errors on certain keys
        if key == "a1.policy_type.111":
            raise RejectedByBackend()
        if key == "a1.policy_type.112":
            raise NotConnected()
        if key == "a1.policy_type.113":
            raise BackendError()

    monkeypatch.setattr("a1.data.SDL.set", monkey_set)

    def create_alt_id(json, id):
        """
        Overwrites the json's policy type ID, attempts create and tests for 503
        """
        json['policy_type_id'] = id
        url = "/a1-p/policytypes/{0}".format(id)
        res = client.put(url, json=json)
        assert res.status_code == 503

    create_alt_id(adm_type_good, 111)
    create_alt_id(adm_type_good, 112)
    create_alt_id(adm_type_good, 113)


def test_illegal_types(client, adm_type_good):
    """
    Test illegal types
    """
    # below valid range
    res = client.put("/a1-p/policytypes/0", json=adm_type_good)
    assert res.status_code == 400
    # ID mismatch
    res = client.put("/a1-p/policytypes/1", json=adm_type_good)
    assert res.status_code == 400
    # above valid range
    res = client.put("/a1-p/policytypes/2147483648", json=adm_type_good)
    assert res.status_code == 400


def test_healthcheck(client):
    """
    test healthcheck
    """
    res = client.get("/a1-p/healthcheck")
    assert res.status_code == 200


def test_metrics(client):
    """
    test Prometheus metrics
    """
    res = client.get("/a1-p/metrics")
    assert res.status_code == 200


def teardown_module():
    """module teardown"""
    a1rmr.stop_rmr_thread()
