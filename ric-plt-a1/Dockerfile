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

# This builds an image for A1 based on ubuntu. The build takes between three and four
# minutes depending on what was previously cached, and results in an image that is
# roughly 260 MiB in size (as of May 2021)
#

FROM python:3.8 as build

# upgrade pip as root
RUN pip install --upgrade pip

# pick up things for gevent build
#
RUN apt-get update
RUN apt-get install -y gcc musl-dev make file libffi-dev g++

# --- all root operations must be above this line ------------------------------------


# create a simple user.  This is only really needed in stage 2,
# however this makes the copying easier and straighttforward;
# the 'pip option --user' command  doesn't do the same thing when
# run as root.
#
RUN addgroup a1user && adduser --ingroup a1user a1user

# switch to the non-root user for installing python things
USER a1user

# Speed hack; we install gevent before anything because when building repeatedly (eg during dev)
# and only changing a1 code, we do not need to keep compiling gevent which takes forever
RUN pip install --user gevent
RUN pip install --user requests

COPY setup.py /home/a1user/
COPY a1/ /home/a1user/a1
RUN pip install --user /home/a1user



# ----- stage 2  ---------------------------------------------------------------------------------

# It might be tempting to use python:3.8, but that image is more than
# 800 GiB to start, and the final image size if it is used is over
# 1 GiB!!  Using the plain ubuntu image, then installing py3, and taking
# things built in the first stage, the final image size isn't tiny, but should
# be well under the 800GiB start for the python image.
#
FROM ubuntu:20.04

# pick up reference to python so that we can get 3.8 and not the really old default

RUN    apt-get update \
	&& apt install -y software-properties-common \
	&& add-apt-repository ppa:deadsnakes/ppa \
	&& apt-get install -y python3.8 python3-pip wget \
	&& apt-get clean

# fetch and install RMR and any other needed libraries
#
ARG RMR_VER=4.8.0
ARG RMR_PKG_URL=https://packagecloud.io/o-ran-sc/release/packages/debian/stretch/

RUN wget -nv --content-disposition ${RMR_PKG_URL}/rmr_${RMR_VER}_amd64.deb/download.deb
RUN wget -nv --content-disposition ${RMR_PKG_URL}/rmr-dev_${RMR_VER}_amd64.deb/download.deb
RUN    dpkg -i rmr_${RMR_VER}_amd64.deb  \
	&& dpkg -i rmr-dev_${RMR_VER}_amd64.deb \
	&& ldconfig

# copy python modules; this makes the 2 stage python build work
#
COPY --from=build /home/a1user/.local /home/a1user/.local

# create mount point for dir with rmr routing file as named below
#
RUN mkdir -p /opt/route/

# create a non-root user, ensure it can access what it needs, and switch to it
#
RUN    addgroup a1user \
	&& adduser --disabled-password --disabled-login --gecos "image-user" --no-create-home --ingroup a1user a1user \
	&& chown -R a1user:a1user /home/a1user/.local \
	&& chown a1user:a1user /home/a1user


# ------------------ no root commands after this point -------------------------------------
USER a1user

# the maddening onsey-twosey install of pything crud...
#
RUN pip3 install  --user connexion

# misc
#
EXPOSE 10000
ENV LD_LIBRARY_PATH /usr/local/lib/:/usr/local/lib64
ENV RMR_SEED_RT /opt/route/local.rt

# Set "fake" to True to run standalone
#
ENV USE_FAKE_SDL False
ENV PYTHONUNBUFFERED 1

# pip installs executable script to $HOME/.local/bin so PATH vars are critical
#
ENV PATH /home/a1user/.local/bin:$PATH
ENV PYTHONPATH /home/a1user/.local/lib/python3.8/site-packages

# prometheus client gathers data here
#
ENV prometheus_multiproc_dir /tmp

# by defalt start the application
#
CMD [ "/usr/bin/python3.8", "/home/a1user/.local/bin/run-a1" ]
