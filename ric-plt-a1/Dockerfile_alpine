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

# This container uses a 2 stage build!
# Tips and tricks were learned from: https://pythonspeed.com/articles/multi-stage-docker-python/
FROM python:3.8-alpine AS compile-image
# upgrade pip as root
RUN pip install --upgrade pip
# Gevent needs gcc, make, file, ffi
RUN apk update && apk add gcc musl-dev make file libffi-dev g++
# create a non-root user.  Only really needed in stage 2,
# however this makes the copying easier and straighttforward;
# pip option --user doesn't do the same thing if run as root
RUN addgroup -S a1user && adduser -S -G a1user a1user
# switch to the non-root user for installing site packages
USER a1user
# Speed hack; we install gevent before a1 because when building repeatedly (eg during dev)
# and only changing a1 code, we do not need to keep compiling gevent which takes forever
RUN pip install --user gevent
COPY setup.py /home/a1user/
COPY a1/ /home/a1user/a1
RUN pip install --user /home/a1user

###########
# 2nd stage
FROM python:3.8-alpine

# copy rmr libraries from builder image in lieu of an Alpine package (10002 is the release portion of the repo)
COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.5.2 /usr/local/lib64/librmr* /usr/local/lib64/

# copy python modules; this makes the 2 stage python build work
COPY --from=compile-image /home/a1user/.local /home/a1user/.local
# create mount point for dir with rmr routing file as named below
RUN mkdir -p /opt/route/
# create a non-root user
RUN addgroup -S a1user && adduser -S -G a1user a1user
# ensure the non-root user can read python files
RUN chown -R a1user:a1user /home/a1user/.local
# switch to the non-root user for security reasons
USER a1user
# misc setups
EXPOSE 10000
ENV LD_LIBRARY_PATH /usr/local/lib/:/usr/local/lib64
ENV RMR_SEED_RT /opt/route/local.rt
# Set to True to run standalone
ENV USE_FAKE_SDL False
ENV PYTHONUNBUFFERED 1
# pip installs console script to ~/.local/bin so PATH is critical
ENV PATH /home/a1user/.local/bin:$PATH
# prometheus client gathers data here
ENV prometheus_multiproc_dir /tmp

# Run!
CMD run-a1
