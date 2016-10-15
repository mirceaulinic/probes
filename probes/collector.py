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

import time

from probes.tester import Tester


class Collector:

    _TIMEOUT = 1

    def __init__(self, server):
        self._server = server
        self._last_run = None
        self.run()

    def _prepare_probes_list(self):
        _execute_tests = {}
        _now = time.time()
        for probe, probe_tests in self._server.config.iteritems():
            for test, test_config in probe_tests.iteritems():
                if _now - test_config.get('last_run', 0) > int(test_config.get('interval', 1)):
                    if probe not in _execute_tests.keys():
                        _execute_tests[probe] = []
                    _execute_tests[probe].append(test)
        return _execute_tests

    def run(self):
        while True:
            if not self._last_run or time.time() - self._last_run > self._TIMEOUT:
                _exec_tests = self._prepare_probes_list()
                testers = []
                for probe, tests in _exec_tests.iteritems():
                    testers.extend([
                        Tester(self._server, probe, test)
                        for test in tests
                    ])
                for tester in testers:
                    tester.start()
                for tester in testers:
                    tester.join()  # wait all to finish
                for tester in testers:
                self._last_run = time.time()
                time.sleep(self._TIMEOUT)
