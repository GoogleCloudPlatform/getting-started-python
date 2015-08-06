# Copyright 2015 Google Inc.
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

FROM debian:jessie

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update -y && \
    apt-get install --no-install-recommends -y -q \
        build-essential python python-dev python-pip \
        git libffi-dev ca-certificates openssl libssl-dev && \
    apt-get clean && \
    rm /var/lib/apt/lists/*_*

RUN pip install -U pip && pip install virtualenv

WORKDIR /app
RUN virtualenv /env
ADD requirements.txt /app/requirements.txt
RUN /env/bin/pip install -r /app/requirements.txt
ADD . /app

EXPOSE 8080
CMD []

# ENTRYPOINT . /env/bin/activate; python main.py

# [START entrypoint]
# Instead of the default entry point, we'll use Honcho. Honcho is a python port
# of the Foreman process manager. $PROCESSES is set by app.yaml / worker.yaml
# to control which processes Honcho will start.
ENTRYPOINT . /env/bin/activate; /env/bin/honcho start -f /app/procfile $PROCESSES
# [END entrypoint]
