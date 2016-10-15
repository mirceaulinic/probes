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

import re

from threading import Thread
from subprocess import Popen, PIPE


class Pinger(Thread):

    _COUNT_ARG = '-c'
    _SOURCE_ARG = '-I'
    _PING_COUNT = 1

    _RTT_RGX = (
        '^(rtt|round-trip)\smin/avg/max/(mdev|stddev)\s'
        '=\s([-+]?\d*\.\d+|\d+)/([-+]?\d*\.\d+|\d+)/'
        '([-+]?\d*\.\d+|\d+)/([-+]?\d*\.\d+|\d+)\s+ms$'
    )
    _LOSS_RGX = (
        '^\d*\s+packets\s+transmitted,\s+\d*\s+'
        '(packets\s+)?received,\s+(\d*\.\d+|\d+)%'
        '\s+packet\s+loss(.*)$'
    )

    def __init__(self, target, source=None):
        Thread.__init__(self)
        self._source = source
        self._target = target
        self._result = None

    def _parse(self, out):
        if not out:
            return
        out_lines = out.splitlines()
        if len(out_lines) == 1 and 'unknown host' in out_lines[0]:
            return
        dev = None
        avg_rtt = None
        loss = None
        for line in out_lines:
            if 'min/avg/max/' in line:
                rtt_rgx = re.search(self._RTT_RGX, line, re.I)
                if rtt_rgx:
                    _, _, _, avg_rtt, _, dev = rtt_rgx.groups()
                    avg_rtt, dev = float(avg_rtt), float(dev)
            elif 'packets transmitted' in line:
                loss_rgx = re.search(self._LOSS_RGX, line, re.I)
                if loss_rgx:
                    _, loss, _ = loss_rgx.groups()
                    loss = float(loss)
        return {
            'rtt': avg_rtt,
            'dev': dev,
            'loss': loss
        }

    def get_results(self):
        return self._result

    def run(self):
        _ping_cmd_args = [
            'ping',
            self._COUNT_ARG,  # count
            str(self._PING_COUNT),  # just one ping
            self._target
        ]
        if self._source:
            _ping_cmd_args.extend([
                self._SOURCE_ARG,
                self._source
            ])
        cmd = ' '.join(_ping_cmd_args)
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if err:
            return
        self._result = self._parse(out)
