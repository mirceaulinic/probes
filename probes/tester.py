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


from threading import Thread

from probes.pinger import Pinger


class Tester(Thread):

    def __init__(self, server, probe_name, test_name):
        Thread.__init__(self)
        self._server = server
        self._probe = probe_name
        self._test = test_name

    def get_result(self):
        return self._result

    def run(self):
        test_config = self._server.config[self._probe][self._test]
        source = test_config.get('source')
        target = test_config.get('target')
        count = int(test_config.get('count', 1))
        pingers = []
        for _ in range(count):
            p = Pinger(target, source=source)
            pingers.append(p)
        for pinger in pingers:
            pinger.start()
        for pinger in pingers:
            pinger.join()  # wait all to finish
        loss_list = []
        rtt_list = []
        for pinger in pingers:
            res = pinger.get_results()
            if res and res.get('rtt'):
                rtt_list.append(res.get('rtt'))
            loss_list.append(res.get('loss') if res else 100.0)
        rtt_sum = sum(rtt_list)
        rtt_count = len(rtt_list)
        if rtt_count < 2:  # if 0 or 1
            stddev = 0.0
        else:
            square_rtt = sum([rtt**2 for rtt in rtt_list])
            stddev = ((count*square_rtt - rtt_sum**2)/(rtt_count**2 - rtt_count))**.5
        min_rtt = min(rtt_list) if rtt_list else None
        max_rtt = max(rtt_list) if rtt_list else None
        avg_rtt = rtt_sum / rtt_count if rtt_list else None
        avg_loss = sum(loss_list) / count
        del pinger  # free mem
        self._result = {
            'avg_rtt': avg_rtt,
            'max_rtt': max_rtt,
            'min_rtt': min_rtt,
            'stddev': stddev,
            'loss': avg_loss
        }
