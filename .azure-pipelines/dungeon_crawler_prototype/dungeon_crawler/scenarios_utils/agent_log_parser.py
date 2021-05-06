from __future__ import print_function

import os
import re
from datetime import datetime


class AgentLogLine:
    # 2019-11-27T22:22:48.123985Z VERBOSE ExtHandler ExtHandler Report vm agent status
    LOG_PATTERN = r'(\S*)\s(\S*)\s(\S*)\s(\S*)\s(.*)'
    LOG_FILE = '/var/log/waagent.log'
    LOG_DATETIME_PATTERN = u'%Y-%m-%dT%H:%M:%S.%fZ'

    # Examples:
    # ProcessGoalState completed [Incarnation: 12; 23 ms]
    # ProcessGoalState completed [Incarnation: 12; 23 ms; Activity Id: 555e551c-600e-4fb4-90ba-8ab8ec28eccc]
    # ProcessGoalState completed [Incarnation: 12; 23 ms; Correlation Id: 555e551c-600e-4fb4-90ba-8ab8ec28eccc]
    # ProcessGoalState completed [Incarnation: 12; 23 ms; GS Creation Time: 2020-11-09T17:48:50.000000Z]
    GOAL_STATE_COMPLETED = r"ProcessGoalState completed\s\[Incarnation:\s(?P<incarnation>\d+);\s(?P<duration>\d+)\sms" \
                           r"(;\sActivity Id:\s(?P<activity_id>\S+))?(;\sCorrelation Id:\s(?P<correlation_id>\S+))?" \
                           r"(;\sGS Creation Time:\s(?P<gs_creation_time>\S+))?\]"

    when = None
    lvl = None
    thread_name = None
    who = None
    msg = None
    line = None
    matched = False

    def __init__(self, line):
        self.line = line
        msg_match = re.match(AgentLogLine.LOG_PATTERN, line)
        if msg_match:
            self.matched = True
            self.when = msg_match.groups()[0]
            self.lvl = msg_match.groups()[1]
            self.thread_name = msg_match.groups()[2]
            self.who = msg_match.groups()[3]
            self.msg = msg_match.groups()[4]

    def get_timestamp(self):
        if self.matched:
            return datetime.strptime(self.when, AgentLogLine.LOG_DATETIME_PATTERN)
        return None


def parse_agent_log_file(waagent_log_path=AgentLogLine.LOG_FILE):
    if not os.path.exists(waagent_log_path):
        raise IOError('{0} is not found'.format(waagent_log_path))

    with open(waagent_log_path) as fh:
        for line in fh:
            yield AgentLogLine(line=line)
