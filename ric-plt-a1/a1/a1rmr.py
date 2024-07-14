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
"""
A1 RMR functionality
"""
import os
import queue
import time
import json
import requests
from threading import Thread
from ricxappframe.rmr import rmr, helpers
from mdclogpy import Logger
from a1 import data, messages
from a1.exceptions import PolicyTypeNotFound, PolicyInstanceNotFound

mdc_logger = Logger()
mdc_logger.mdclog_format_init(configmap_monitor=True)


# With Nanomsg and NNG it was possible for a send attempt to have a "soft"
# failure which did warrant some retries if the status of the send is RMR_ERR_RETRY.
# Because of the way NNG worked, it sometimes required many tens of retries,
# and a retry state happened often for even moderately "verbose" applications.
# With SI95 there is still a possibility that a retry is necessary, but it is very rare.
RETRY_TIMES = int(os.environ.get("A1_RMR_RETRY_TIMES", 4))
A1_POLICY_REQUEST = 20010
A1_POLICY_RESPONSE = 20011
A1_POLICY_QUERY = 20012
A1_EI_QUERY_ALL = 20013
AI_EI_QUERY_ALL_RESP = 20014
A1_EI_CREATE_JOB = 20015
A1_EI_CREATE_JOB_RESP = 20016
A1_EI_DATA_DELIVERY = 20017
ECS_SERVICE_HOST = os.environ.get("ECS_SERVICE_HOST", "http://ecs-service:8083")
ESC_EI_TYPE_PATH = ECS_SERVICE_HOST + "/A1-EI/v1/eitypes"
ECS_EI_JOB_PATH = ECS_SERVICE_HOST + "/A1-EI/v1/eijobs/"


# Note; yes, globals are bad, but this is a private (to this module) global
# No other module can import/access this (well, python doesn't enforce this, but all linters will complain)
__RMR_LOOP__ = None


class _RmrLoop:
    """
    Class represents an rmr loop that constantly reads from rmr and performs operations
    based on waiting messages.  This launches a thread, it should probably only be called
    once; the public facing method to access these ensures this.

    TODO: the xapp frame has a version of this looping structure. See if A1 can switch to that.
    """

    def __init__(self, init_func_override=None, rcv_func_override=None):
        """
        Init

        Parameters
        ----------
        init_func_override: function (optional)
            Function that initializes RMR and answers an RMR context.
            Supply an empty function to skip initializing RMR.

        rcv_func_override: function (optional)
            Function that receives messages from RMR and answers a list.
            Supply a trivial function to skip reading from RMR.
        """
        self.keep_going = True
        self.rcv_func = None
        self.last_ran = time.time()

        # see docs/overview#resiliency for a discussion of this
        self.instance_send_queue = queue.Queue()  # thread safe queue https://docs.python.org/3/library/queue.html
        # queue for data delivery item
        self.ei_job_result_queue = queue.Queue()

        # intialize rmr context
        if init_func_override:
            self.mrc = init_func_override()
        else:
            mdc_logger.debug("Waiting for rmr to initialize..")
            # rmr.RMRFL_MTCALL puts RMR into a multithreaded mode, where a receiving thread
            # populates an internal ring of messages, and receive calls read from that.
            # currently the size is 2048 messages, so this is fine for the foreseeable future
            self.mrc = rmr.rmr_init(b"4562", rmr.RMR_MAX_RCV_BYTES, rmr.RMRFL_MTCALL)
            while rmr.rmr_ready(self.mrc) == 0:
                time.sleep(0.5)

        # set the receive function
        self.rcv_func = (
            rcv_func_override
            if rcv_func_override
            else lambda: helpers.rmr_rcvall_msgs_raw(self.mrc, [A1_POLICY_RESPONSE, A1_POLICY_QUERY, A1_EI_QUERY_ALL, A1_EI_CREATE_JOB])
        )

        # start the work loop
        self.thread = Thread(target=self.loop)
        self.thread.start()

    def _assert_good_send(self, sbuf, pre_send_summary):
        """
        Extracts the send result and logs a detailed warning if the send failed.
        Returns the message state, an integer that indicates the result.
        """
        post_send_summary = rmr.message_summary(sbuf)
        if post_send_summary[rmr.RMR_MS_MSG_STATE] != rmr.RMR_OK:
            mdc_logger.warning("RMR send failed; pre-send summary: {0}, post-send summary: {1}".format(pre_send_summary, post_send_summary))
        return post_send_summary[rmr.RMR_MS_MSG_STATE]

    def _send_msg(self, pay, mtype, subid):
        """
        Creates and sends a message via RMR's send-message feature with the specified payload
        using the specified message type and subscription ID.
        """
        sbuf = rmr.rmr_alloc_msg(self.mrc, len(pay), payload=pay, gen_transaction_id=True, mtype=mtype, sub_id=subid)
        sbuf.contents.sub_id = subid
        pre_send_summary = rmr.message_summary(sbuf)
        for _ in range(0, RETRY_TIMES):
            mdc_logger.debug("_send_msg: sending: {}".format(pre_send_summary))
            sbuf = rmr.rmr_send_msg(self.mrc, sbuf)
            msg_state = self._assert_good_send(sbuf, pre_send_summary)
            mdc_logger.debug("_send_msg: result message state: {}".format(msg_state))
            if msg_state != rmr.RMR_ERR_RETRY:
                break

        rmr.rmr_free_msg(sbuf)
        if msg_state != rmr.RMR_OK:
            mdc_logger.warning("_send_msg: failed after {} retries".format(RETRY_TIMES))

    def _rts_msg(self, pay, sbuf_rts, mtype):
        """
        Sends a message via RMR's return-to-sender feature.
        This neither allocates nor frees a message buffer because we may rts many times.
        Returns the message buffer from the RTS function, which may reallocate it.
        """
        pre_send_summary = rmr.message_summary(sbuf_rts)
        for _ in range(0, RETRY_TIMES):
            mdc_logger.debug("_rts_msg: sending: {}".format(pre_send_summary))
            sbuf_rts = rmr.rmr_rts_msg(self.mrc, sbuf_rts, payload=pay, mtype=mtype)
            msg_state = self._assert_good_send(sbuf_rts, pre_send_summary)
            mdc_logger.debug("_rts_msg: result message state: {}".format(msg_state))
            if msg_state != rmr.RMR_ERR_RETRY:
                break

        if msg_state != rmr.RMR_OK:
            mdc_logger.warning("_rts_msg: failed after {} retries".format(RETRY_TIMES))
        return sbuf_rts  # in some cases rts may return a new sbuf

    def _handle_sends(self):
        # send out all messages waiting for us
        while not self.instance_send_queue.empty():
            work_item = self.instance_send_queue.get(block=False, timeout=None)
            payload = json.dumps(messages.a1_to_handler(*work_item)).encode("utf-8")
            self._send_msg(payload, A1_POLICY_REQUEST, work_item[1])

        # now send all the ei-job related data
        while not self.ei_job_result_queue.empty():
            mdc_logger.debug("perform data delivery to consumer")

            work_item = self.ei_job_result_queue.get(block=False, timeout=None)
            payload = json.dumps(messages.ei_to_handler(*work_item)).encode("utf-8")
            ei_job_id = int(work_item[0])
            mdc_logger.debug("data-delivery: {}".format(payload))

            # send the payload to consumer subscribed for ei_job_id
            self._send_msg(payload, A1_EI_DATA_DELIVERY, ei_job_id)

    def loop(self):
        """
        This loop runs forever, and has 3 jobs:
        - send out any messages that have to go out (create instance, delete instance)
        - read a1s mailbox and update the status of all instances based on acks from downstream policy handlers
        - clean up the database (eg delete the instance) under certain conditions based on those statuses (NOT DONE YET)
        """
        # loop forever
        mdc_logger.debug("Work loop starting")
        while self.keep_going:

            # Update 3/20/2020
            # We now handle our sends in a thread (that will just exit when it's done) because there is a difference between how send works in SI95 vs NNG.
            # Send_msg via NNG formerly never blocked.
            # However under SI95 this send may block for some arbitrary period of time on the first send to an endpoint for which a connection is not established
            # If this send takes too long, this loop blocks, and the healthcheck will fail, which will cause A1s healthcheck to fail, which will cause Kubernetes to whack A1 and all kinds of horrible things happen.
            # Therefore, now under SI95, we thread this.
            Thread(target=self._handle_sends).start()

            # read our mailbox
            for (msg, sbuf) in self.rcv_func():
                # TODO: in the future we may also have to catch SDL errors
                try:
                    mtype = msg[rmr.RMR_MS_MSG_TYPE]
                except (KeyError, TypeError, json.decoder.JSONDecodeError):
                    mdc_logger.warning("Dropping malformed message: {0}".format(msg))

                if mtype == A1_POLICY_RESPONSE:
                    try:
                        # got a policy response, update status
                        pay = json.loads(msg[rmr.RMR_MS_PAYLOAD])
                        data.set_policy_instance_status(
                            pay["policy_type_id"], pay["policy_instance_id"], pay["handler_id"], pay["status"]
                        )
                        mdc_logger.debug("Successfully received status update: {0}".format(pay))
                    except (PolicyTypeNotFound, PolicyInstanceNotFound):
                        mdc_logger.warning("Received a response for a non-existent type/instance: {0}".format(msg))
                    except (KeyError, TypeError, json.decoder.JSONDecodeError):
                        mdc_logger.warning("Dropping malformed policy response: {0}".format(msg))

                elif mtype == A1_POLICY_QUERY:
                    try:
                        # got a query, do a lookup and send out all instances
                        pti = json.loads(msg[rmr.RMR_MS_PAYLOAD])["policy_type_id"]
                        instance_list = data.get_instance_list(pti)  # will raise if a bad type
                        mdc_logger.debug("Received a query for a known policy type: {0}".format(msg))
                        for pii in instance_list:
                            instance = data.get_policy_instance(pti, pii)
                            payload = json.dumps(messages.a1_to_handler("CREATE", pti, pii, instance)).encode("utf-8")
                            sbuf = self._rts_msg(payload, sbuf, A1_POLICY_REQUEST)
                    except (PolicyTypeNotFound):
                        mdc_logger.warning("Received a policy query for a non-existent type: {0}".format(msg))
                    except (KeyError, TypeError, json.decoder.JSONDecodeError):
                        mdc_logger.warning("Dropping malformed policy query: {0}".format(msg))

                elif mtype == A1_EI_QUERY_ALL:
                    mdc_logger.debug("Received messaage {0}".format(msg))

                    # query A1-EI co-ordinator service to get the EI-types
                    resp = requests.get(ESC_EI_TYPE_PATH)
                    if resp.status_code != 200:
                        mdc_logger.warning("Received no reponse from A1-EI service")

                    mdc_logger.debug("response from A1-EI service : {0}".format(resp.json()))

                    # send the complete list of EI-types to xApp
                    sbuf = self._rts_msg(resp.content, sbuf, AI_EI_QUERY_ALL_RESP)

                elif mtype == A1_EI_CREATE_JOB:
                    mdc_logger.debug("Received message {0}".format(msg))
                    payload = json.loads(msg[rmr.RMR_MS_PAYLOAD])
                    mdc_logger.debug("Payload: {0}".format(payload))

                    uuidStr = payload["job-id"]
                    del payload["job-id"]

                    mdc_logger.debug("Payload after removing job-id: {0}".format(payload))

                    # 1. send request to A1-EI Service to create A1-EI JOB
                    headers = {'Content-type': 'application/json'}
                    r = requests.put(ECS_EI_JOB_PATH + uuidStr, data=json.dumps(payload), headers=headers)
                    if (r.status_code != 201) and (r.status_code != 200):
                        mdc_logger.warning("failed to create EIJOB : {0}".format(r))
                    else:
                        # 2. inform xApp for Job status
                        mdc_logger.debug("received successful response (ei-job-id) :{0}".format(uuidStr))
                        rmr_data = """{{
                                "ei_job_id": "{id}"
                                }}""".format(id=uuidStr)
                        mdc_logger.debug("rmr_Data to send: {0}".format(rmr_data))
                        sbuf = self._rts_msg(str.encode(rmr_data), sbuf, A1_EI_CREATE_JOB_RESP)

                else:
                    mdc_logger.warning("Received message type {0} but A1 does not handle this".format(mtype))

                # we must free each sbuf
                rmr.rmr_free_msg(sbuf)
            self.last_ran = time.time()
            time.sleep(1)

        mdc_logger.debug("RMR Thread Ending!")


# Public


def start_rmr_thread(init_func_override=None, rcv_func_override=None):
    """
    Start a1s rmr thread

    Parameters
    ----------
    init_func_override: function (optional)
        Function that initializes RMR and answers an RMR context.
        Supply an empty function to skip initializing RMR.

    rcv_func_override: function (optional)
        Function that receives messages from RMR and answers a list.
        Supply a trivial function to skip reading from RMR.
    """
    global __RMR_LOOP__
    if __RMR_LOOP__ is None:
        __RMR_LOOP__ = _RmrLoop(init_func_override, rcv_func_override)


def stop_rmr_thread():
    """
    stops the rmr thread
    """
    __RMR_LOOP__.keep_going = False


def queue_instance_send(item):
    """
    push an item into the work queue
    currently the only type of work is to send out messages
    """
    __RMR_LOOP__.instance_send_queue.put(item)


def queue_ei_job_result(item):
    """
    push an item into the ei_job_queue
    """
    mdc_logger.debug("queuing data delivery item {0}".format(item))
    __RMR_LOOP__.ei_job_result_queue.put(item)


def healthcheck_rmr_thread(seconds=30):
    """
    returns a boolean representing whether the rmr loop is healthy, by checking two attributes:
    1. is it running?,
    2. is it stuck in a long (> seconds) loop?
    """
    return __RMR_LOOP__.thread.is_alive() and ((time.time() - __RMR_LOOP__.last_ran) < seconds)


def replace_rcv_func(rcv_func):
    """purely for the ease of unit testing to test different rcv scenarios"""
    __RMR_LOOP__.rcv_func = rcv_func
