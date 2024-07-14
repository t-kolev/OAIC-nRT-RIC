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
Represents A1s database and database access functions.
"""
import distutils.util
import os
import time
from threading import Thread
from mdclogpy import Logger
from ricxappframe.xapp_sdl import SDLWrapper
from a1.exceptions import PolicyTypeNotFound, PolicyInstanceNotFound, PolicyTypeAlreadyExists, PolicyTypeIdMismatch, CantDeleteNonEmptyType

# constants
INSTANCE_DELETE_NO_RESP_TTL = int(os.environ.get("INSTANCE_DELETE_NO_RESP_TTL", 5))
INSTANCE_DELETE_RESP_TTL = int(os.environ.get("INSTANCE_DELETE_RESP_TTL", 5))
USE_FAKE_SDL = bool(distutils.util.strtobool(os.environ.get("USE_FAKE_SDL", "False")))
A1NS = "A1m_ns"
TYPE_PREFIX = "a1.policy_type."
INSTANCE_PREFIX = "a1.policy_instance."
METADATA_PREFIX = "a1.policy_inst_metadata."
HANDLER_PREFIX = "a1.policy_handler."


mdc_logger = Logger(name=__name__)
mdc_logger.mdclog_format_init(configmap_monitor=True)
if USE_FAKE_SDL:
    mdc_logger.debug("Using fake SDL")
SDL = SDLWrapper(use_fake_sdl=USE_FAKE_SDL)

# Internal helpers


def _generate_type_key(policy_type_id):
    """
    generate a key for a policy type
    """
    return "{0}{1}".format(TYPE_PREFIX, policy_type_id)


def _generate_instance_key(policy_type_id, policy_instance_id):
    """
    generate a key for a policy instance
    """
    return "{0}{1}.{2}".format(INSTANCE_PREFIX, policy_type_id, policy_instance_id)


def _generate_instance_metadata_key(policy_type_id, policy_instance_id):
    """
    generate a key for a policy instance metadata
    """
    return "{0}{1}.{2}".format(METADATA_PREFIX, policy_type_id, policy_instance_id)


def _generate_handler_prefix(policy_type_id, policy_instance_id):
    """
    generate the prefix to a handler key
    """
    return "{0}{1}.{2}.".format(HANDLER_PREFIX, policy_type_id, policy_instance_id)


def _generate_handler_key(policy_type_id, policy_instance_id, handler_id):
    """
    generate a key for a policy handler
    """
    return "{0}{1}".format(_generate_handler_prefix(policy_type_id, policy_instance_id), handler_id)


def _type_is_valid(policy_type_id):
    """
    check that a type is valid
    """
    if SDL.get(A1NS, _generate_type_key(policy_type_id)) is None:
        raise PolicyTypeNotFound(policy_type_id)


def _instance_is_valid(policy_type_id, policy_instance_id):
    """
    check that an instance is valid
    """
    _type_is_valid(policy_type_id)
    if SDL.get(A1NS, _generate_instance_key(policy_type_id, policy_instance_id)) is None:
        raise PolicyInstanceNotFound(policy_type_id)


def _get_statuses(policy_type_id, policy_instance_id):
    """
    shared helper to get statuses for an instance
    """
    _instance_is_valid(policy_type_id, policy_instance_id)
    prefixes_for_handler = "{0}{1}.{2}.".format(HANDLER_PREFIX, policy_type_id, policy_instance_id)
    return list(SDL.find_and_get(A1NS, prefixes_for_handler).values())


def _get_instance_list(policy_type_id):
    """
    shared helper to get instance list for a type
    """
    _type_is_valid(policy_type_id)
    prefixes_for_type = "{0}{1}.".format(INSTANCE_PREFIX, policy_type_id)
    instancekeys = SDL.find_and_get(A1NS, prefixes_for_type).keys()
    return [k.split(prefixes_for_type)[1] for k in instancekeys]


def _clear_handlers(policy_type_id, policy_instance_id):
    """
    delete all the handlers for a policy instance
    """
    all_handlers_pref = _generate_handler_prefix(policy_type_id, policy_instance_id)
    keys = SDL.find_and_get(A1NS, all_handlers_pref)
    for k in keys:
        SDL.delete(A1NS, k)


def _get_metadata(policy_type_id, policy_instance_id):
    """
    get instance metadata
    """
    _instance_is_valid(policy_type_id, policy_instance_id)
    metadata_key = _generate_instance_metadata_key(policy_type_id, policy_instance_id)
    return SDL.get(A1NS, metadata_key)


def _delete_after(policy_type_id, policy_instance_id, ttl):
    """
    this is a blocking function, must call this in a thread to not block!
    waits ttl seconds, then deletes the instance
    """
    _instance_is_valid(policy_type_id, policy_instance_id)

    time.sleep(ttl)

    # ready to delete
    _clear_handlers(policy_type_id, policy_instance_id)  # delete all the handlers
    SDL.delete(A1NS, _generate_instance_key(policy_type_id, policy_instance_id))  # delete instance
    SDL.delete(A1NS, _generate_instance_metadata_key(policy_type_id, policy_instance_id))  # delete instance metadata
    mdc_logger.debug("type {0} instance {1} deleted".format(policy_type_id, policy_instance_id))


# Types


def get_type_list():
    """
    retrieve all type ids
    """
    typekeys = SDL.find_and_get(A1NS, TYPE_PREFIX).keys()
    # policy types are ints but they get butchered to strings in the KV
    return [int(k.split(TYPE_PREFIX)[1]) for k in typekeys]


def store_policy_type(policy_type_id, body):
    """
    store a policy type if it doesn't already exist
    """
    if policy_type_id != body['policy_type_id']:
        raise PolicyTypeIdMismatch("{0} vs. {1}".format(policy_type_id, body['policy_type_id']))
    key = _generate_type_key(policy_type_id)
    if SDL.get(A1NS, key) is not None:
        raise PolicyTypeAlreadyExists(policy_type_id)
    SDL.set(A1NS, key, body)


def delete_policy_type(policy_type_id):
    """
    delete a policy type; can only be done if there are no instances (business logic)
    """
    pil = get_instance_list(policy_type_id)
    if pil == []:  # empty, can delete
        SDL.delete(A1NS, _generate_type_key(policy_type_id))
    else:
        raise CantDeleteNonEmptyType(policy_type_id)


def get_policy_type(policy_type_id):
    """
    retrieve a type
    """
    _type_is_valid(policy_type_id)
    return SDL.get(A1NS, _generate_type_key(policy_type_id))


# Instances


def store_policy_instance(policy_type_id, policy_instance_id, instance):
    """
    Store a policy instance
    """
    _type_is_valid(policy_type_id)
    creation_timestamp = time.time()

    # store the instance
    operation = "CREATE"
    key = _generate_instance_key(policy_type_id, policy_instance_id)
    if SDL.get(A1NS, key) is not None:
        operation = "UPDATE"
        # Reset the statuses because this is a new policy instance, even if it was overwritten
        _clear_handlers(policy_type_id, policy_instance_id)  # delete all the handlers
    SDL.set(A1NS, key, instance)

    metadata_key = _generate_instance_metadata_key(policy_type_id, policy_instance_id)
    SDL.set(A1NS, metadata_key, {"created_at": creation_timestamp, "has_been_deleted": False})

    return operation


def get_policy_instance(policy_type_id, policy_instance_id):
    """
    Retrieve a policy instance
    """
    _instance_is_valid(policy_type_id, policy_instance_id)
    return SDL.get(A1NS, _generate_instance_key(policy_type_id, policy_instance_id))


def get_instance_list(policy_type_id):
    """
    retrieve all instance ids for a type
    """
    return _get_instance_list(policy_type_id)


def delete_policy_instance(policy_type_id, policy_instance_id):
    """
    initially sets has_been_deleted in the status
    then launches a thread that waits until the relevent timer expires, and finally deletes the instance
    """
    _instance_is_valid(policy_type_id, policy_instance_id)

    # set the metadata first
    deleted_timestamp = time.time()
    metadata_key = _generate_instance_metadata_key(policy_type_id, policy_instance_id)
    existing_metadata = _get_metadata(policy_type_id, policy_instance_id)
    SDL.set(
        A1NS,
        metadata_key,
        {"created_at": existing_metadata["created_at"], "has_been_deleted": True, "deleted_at": deleted_timestamp},
    )

    # wait, then delete
    vector = _get_statuses(policy_type_id, policy_instance_id)
    if vector == []:
        # handler is empty; we wait for t1 to expire then goodnight
        clos = lambda: _delete_after(policy_type_id, policy_instance_id, INSTANCE_DELETE_NO_RESP_TTL)
    else:
        # handler is not empty, we wait max t1,t2 to expire then goodnight
        clos = lambda: _delete_after(
            policy_type_id, policy_instance_id, max(INSTANCE_DELETE_RESP_TTL, INSTANCE_DELETE_NO_RESP_TTL)
        )
    Thread(target=clos).start()


# Statuses


def set_policy_instance_status(policy_type_id, policy_instance_id, handler_id, status):
    """
    update the database status for a handler
    called from a1's rmr thread
    """
    _type_is_valid(policy_type_id)
    _instance_is_valid(policy_type_id, policy_instance_id)
    SDL.set(A1NS, _generate_handler_key(policy_type_id, policy_instance_id, handler_id), status)


def get_policy_instance_status(policy_type_id, policy_instance_id):
    """
    Gets the status of an instance
    """
    _instance_is_valid(policy_type_id, policy_instance_id)
    metadata = _get_metadata(policy_type_id, policy_instance_id)
    metadata["instance_status"] = "NOT IN EFFECT"
    for i in _get_statuses(policy_type_id, policy_instance_id):
        if i == "OK":
            metadata["instance_status"] = "IN EFFECT"
            break
    return metadata
