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
Custom Exceptions
"""


class A1Error(Exception):
    """A base class for A1 exceptions."""

    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(A1Error, self).__init__(message)


class CantDeleteNonEmptyType(A1Error):
    """tried to delete a type that isn't empty"""


class PolicyInstanceNotFound(A1Error):
    """a policy instance cannot be found"""


class PolicyTypeNotFound(A1Error):
    """a policy type instance cannot be found"""


class PolicyTypeAlreadyExists(A1Error):
    """a policy type already exists and replace not supported at this time"""


class PolicyTypeIdMismatch(A1Error):
    """a policy type request path ID differs from its body ID"""
