#!/bin/bash
# Copyright (c) 2023 Huawei Device Co., Ltd.
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

set -e
cd $1
if [ -d "cups-2.4.0" ];then
    rm -rf cups-2.4.0
fi
tar xvf cups-2.4.0-source.tar.gz
cd $1/cups-2.4.0
patch -p1 < $1/backport-CVE-2022-26691.patch --fuzz=0 --no-backup-if-mismatch
patch -p1 < $1/backport-CVE-2023-32324.patch --fuzz=0 --no-backup-if-mismatch
patch -p1 < $1/backport-CVE-2023-34241.patch --fuzz=0 --no-backup-if-mismatch
patch -p1 < $1/cups_single_file.patch --fuzz=0 --no-backup-if-mismatch
patch -p1 < $1/pthread_cancel.patch --fuzz=0 --no-backup-if-mismatch
patch -p1 < $1/ohos-tls-opensource.patch --fuzz=0 --no-backup-if-mismatch
exit 0