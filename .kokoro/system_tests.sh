#!/bin/bash

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -eo pipefail

export PATH=${PATH}:${HOME}/gcloud/google-cloud-sdk/bin

cd github/getting-started-python

# Unencrypt and extract secrets
SECRETS_PASSWORD=$(cat "${KOKORO_GFILE_DIR}/secrets-password.txt")
./decrypt-secrets.sh "${SECRETS_PASSWORD}"

# Setup environment variables
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/service-account.json"

# Run tests
pip install --upgrade nox-automation

nox -s run_tests
