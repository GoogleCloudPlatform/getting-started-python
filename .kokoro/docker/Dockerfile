# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM gcr.io/cloud-devrel-kokoro-resources/python-base:latest

# Install libraries needed by third-party python packages that we depend on.
RUN apt update \
  && apt install -y \
    graphviz \
    libcurl4-openssl-dev \
    libffi-dev \
    libjpeg-dev \
    libmagickwand-dev \
    libmemcached-dev \
    libmysqlclient-dev \
    libpng-dev \
    libpq-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    openssl \
    portaudio19-dev \
    python-pyaudio \
    zlib1g-dev \
 && apt clean

RUN python --version
RUN which python

# Setup Cloud SDK
ENV CLOUD_SDK_VERSION 324.0.0
# Use system python for cloud sdk.
ENV CLOUDSDK_PYTHON /usr/bin/python
RUN wget https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-$CLOUD_SDK_VERSION-linux-x86_64.tar.gz
RUN tar xzf google-cloud-sdk-$CLOUD_SDK_VERSION-linux-x86_64.tar.gz
RUN /google-cloud-sdk/install.sh
ENV PATH /google-cloud-sdk/bin:$PATH

# Setup the user profile for pip
ENV PATH ~/.local/bin:/root/.local/bin:$PATH

# Install the current version of nox.
RUN python3 -m pip install --user --no-cache-dir nox==2020.12.31

CMD ["nox"]
