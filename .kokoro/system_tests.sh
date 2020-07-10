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

cd "${PROJECT_ROOT:-github/getting-started-python}"


# Unencrypt and extract secrets
SECRETS_PASSWORD=$(cat "${KOKORO_GFILE_DIR}/secrets-password.txt")
./decrypt-secrets.sh "${SECRETS_PASSWORD}"

# Setup environment variables
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/service-account.json"

# This block is executed only with Trampoline V2.
if [[ -n "${TRAMPOLINE_VERSION:-}" ]]; then
    # Install nox as a user and add it to the PATH.
    python3 -m pip install --user nox
    export PATH="${PATH}:${HOME}/.local/bin"
fi

# Run tests
nox -s lint
nox -s run_tests

# If this is a nightly build, send the test log to the Build Cop Bot.
# See https://github.com/googleapis/repo-automation-bots/tree/master/packages/buildcop.
if [[ $KOKORO_BUILD_ARTIFACTS_SUBDIR = *"system_tests"* ]]; then
    chmod +x $KOKORO_GFILE_DIR/linux_amd64/buildcop
    $KOKORO_GFILE_DIR/linux_amd64/buildcop
fi
