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


class Config:

    _DELIMITER = '_'
    _PROBES_KEY = 'probes'
    _TESTS_PREFIX = 'tests'

    def __init__(self, redis):
        self._redis = redis
        self._config = {}
        self._pipe = self._redis.pipeline()
        self._buffered = False
        self._last_write = None

        self.read()

    def _get_test_key(self, probe_name, test_name):
        return '{probe}{delim}{test}'.format(probe=probe_name,
                                             delim=self._DELIMITER,
                                             test=test_name)

    def _get_probe_tests_key(self, probe_name):
        return '{pfx}{delim}{probe}'.format(pfx=self._TESTS_PREFIX,
                                            delim=self._DELIMITER,
                                            probe=probe_name)

    @property
    def probes(self):
        return self._config

    def read(self):
        """Reads the config from Redis
        and returns the configuration of the probes"""

        def _new_test(probe, t):
            """Helper that initiates the config of a test
            within a certain probe and returns the key."""
            # self._config[probe][t] = {}
            return self._get_test_key(probe, t)

        all_tests = []
        probes = self._redis.smembers(self._PROBES_KEY)
        for probe in probes:
            self._config[probe] = {}
            probe_tests_key = self._get_probe_tests_key(probe)
            probe_tests = self._redis.smembers(probe_tests_key)
            all_tests.extend([_new_test(probe, t) for t in probe_tests])

        # extraction of tests config is pipelined for better performances

        for test in all_tests:
            self._pipe.hgetall(test)
        config = self._pipe.execute()

        for test in all_tests:
            test_index = all_tests.index(test)
            test_config = config[test_index]
            probe, tst_name = test.split(self._DELIMITER)
            if test_config:
                self._config[probe][tst_name] = test_config

        return self._config

    def write_bulk(self):
        """Writes the whole config in Redis"""
        return True

    def set_test(self, probe_name, test_name, target_addr, **options):
        if probe_name not in self._config.keys():
            self._config[probe_name] = {}
        if test_name not in self._config[probe_name].keys():
            self._config[probe_name][test_name] = {}
        self._config[probe_name][test_name]['target'] = target_addr
        for opt, val in options.iteritems():
            self._config[probe_name][test_name][opt] = val
        test_key = self._get_test_key(probe_name, test_name)
        probe_tests_key = self._get_probe_tests_key(probe_name)
        options['target'] = target_addr
        self._pipe.sadd(self._PROBES_KEY, probe_name)
        self._pipe.hmset(test_key, options)
        self._pipe.sadd(probe_tests_key, test_name)
        self._pipe.execute()
        return True

    def delete_test(self, probe_name, test_name):
        if probe_name not in self._config.keys():
            return False
        if test_name not in self._config[probe_name].keys():
            return False
        self._config[probe_name].pop(test_name)
        test_key = self._get_test_key(probe_name, test_name)
        probe_tests_key = self._get_probe_tests_key(probe_name)
        self._pipe.delete(test_key)
        self._pipe.srem(probe_tests_key, test_name)
        self._pipe.execute()
        return True

    def _delete_probe_redis(self, probe_name, execute=True):
        probe_tests = self._config[probe_name].keys()
        probe_tests_key = self._get_probe_tests_key(probe_name)
        for test in probe_tests:
            test_key = self._get_test_key(probe_name, test_name)
            self._pipe.delete(test_key)
            self._pipe.srem(probe_tests_key, test_name)
        self._pipe.srem(self._PROBES_KEY, probe_name)
        if execute:
            self._pipe.execute()

    def delete_probe(self, probe_name):
        if probe_name not in self._config.keys():
            return False
        self._delete_probe_redis()
        self._config.pop(probe_name)
        return True

    def erase(self):
        for probe in self._config.keys():
            self._delete_probe_redis(probe, execute=False)
        self._config = {}
        self._pipe.execute()
