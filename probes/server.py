# -*- coding: utf-8 -*-
# Copyright 2016 Mircea Ulinic. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# Import python stdlib
import time
import thread
from threading import Lock

# Import third party lib
import redis

# Import local modules
from probes.config import Config
from probes.collector import Collector
# from probes.collector import Collector


class Server:

    def __init__(self, host=None, port=None):

        opts = {}
        if host:
            opts['host'] = host
        if port:
            opts['port'] = port
        self._server = redis.Redis(**opts)

        self._config = Config(self._server)
        self._collector = Collector(self)

    @property
    def config(self):
        return self._config.probes

    def get_config(self):
        return self._config.read()

    def set_test(self, probe_name, test_name, target_addr, **options):
        return self._config.set_test(probe_name, test_name, target_addr, **options)

    def delete_test(self, probe_name, test_name, **options):
        return self._config.delete_test(probe_name, test_name, **options)

    def delete_probe(self, probe_name):
        return self._config.delete_probe(probe_name)

    def remove_probes(self):
        return self._config.erase()
