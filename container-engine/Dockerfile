# Copyright 2016 Google Inc.
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
# limitations under the License

# The Google App Engine base image is debian (jessie) with ca-certificates
# installed.
FROM gcr.io/google_appengine/base

# Install Python, pip, and C dev libraries necessary to compile the most popular
# Python libraries.
RUN apt-get -q update && \
 apt-get install --no-install-recommends -y -q \
   python2.7 python3.4 python2.7-dev python3.4-dev python-pip build-essential git mercurial \
   libffi-dev libssl-dev libxml2-dev \
   libxslt1-dev libpq-dev libmysqlclient-dev libcurl4-openssl-dev \
   libjpeg-dev zlib1g-dev libpng12-dev \
   gfortran libblas-dev liblapack-dev libatlas-dev libquadmath0 \
   libfreetype6-dev pkg-config swig \
   && \
 apt-get clean && rm /var/lib/apt/lists/*_*

# Setup locale. This prevents Python 3 IO encoding issues.
ENV LANG C.UTF-8

# Upgrade pip (debian package version tends to run a few version behind) and
# install virtualenv system-wide.
RUN pip install --upgrade pip virtualenv

RUN ln -s /home/vmagent/app /app
WORKDIR /app

# Port 8080 is the port used by Google App Engine for serving HTTP traffic.
EXPOSE 8080
ENV PORT 8080

# Create a virtualenv for the application dependencies.
# If you want to use Python 3, add the -p python3.4 flag.
RUN virtualenv /env

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate. This ensures the application is executed within
# the context of the virtualenv and will have access to its dependencies.
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

# Install dependencies.
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Add application code.
ADD . /app

# Instead of using gunicorn directly, we'll use Honcho. Honcho is a python port
# of the Foreman process manager. $PROCESSES is set in the pod manifest
# to control which processes Honcho will start.
CMD honcho start -f /app/procfile $PROCESSES
