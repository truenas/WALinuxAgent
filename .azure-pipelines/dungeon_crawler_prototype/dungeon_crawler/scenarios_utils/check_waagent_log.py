from __future__ import print_function

import re
import sys

from dungeon_crawler.scenarios_utils.agent_log_parser import parse_agent_log_file, AgentLogLine
from dungeon_crawler.scenarios_utils.cgroups_helpers import is_systemd_distro
from dungeon_crawler.scenarios_utils.distro import get_distro


def check_waagent_log_for_errors(waagent_log=AgentLogLine.LOG_FILE, exit_on_completion=True, ignore=None):
    # Returns any ERROR messages from the log except transient ones.
    # Currently, the only transient one is /proc/net/route not being set up if it's being reported before
    # provisioning was completed. In that case, we ignore that error message.

    no_routes_error = None
    provisioning_complete = False
    exit_code = 0

    try:
        distro = "".join(get_distro())
        systemd_enabled = is_systemd_distro()

        error_tags = ['ERROR', 'Exception', 'Traceback', 'WARNING']

        #
        # NOTES:
        #     * 'message' is matched using re.search; be sure to escape any regex metacharacters
        #     * 'if' receives as parameter an AgentLogLine
        #
        ignore_list = [
            # This is a known issue (https://github.com/Azure/WALinuxAgent/pull/2016)
            # Please remove this message from ignored once this task is completed
            # - https://msazure.visualstudio.com/One/_workitems/edit/8733946
            {
                'message': r"need a bytes-like object, NoneType found"
            },
            # This warning is expected on CentOS/RedHat 7.8
            {
                'message': r"WARNING EnvHandler ExtHandler Move rules file 70-persistent-net.rules to /var/lib/waagent/70-persistent-net.rules",
                'if': lambda _: re.match(r"((centos7\.8)|(redhat7\.8))\D*", distro, flags=re.IGNORECASE) is not None
            },
            # This warning is expected on SUSE 12
            {
                'message': r"WARNING EnvHandler ExtHandler Move rules file 75-persistent-net-generator.rules to /var/lib/waagent/75-persistent-net-generator.rules",
                'if': lambda _: re.match(r"suse12\D*", distro, flags=re.IGNORECASE) is not None
            },
            # This warning is expected on when WireServer gives us the incomplete goalstate without roleinstance data
            # raise IncompleteGoalStateError("Fetched goal state without a RoleInstance [incarnation {inc}]".format(inc=self.incarnation))
            {
                'message': r"\[IncompleteGoalStateError\] Fetched goal state without a RoleInstance",
            },
            # The following message is expected to log an error if systemd is not enabled on it
            {
                'message': r"Unable to setup the persistent firewall rules: Did not detect Systemd",
                'if': lambda _: not systemd_enabled
            },
            # ResourceGone can happen if we are fetching one of the URIs in the goal state and a new goal state arrives
            {
                'message': r"Fetching the goal state failed: \[ResourceGoneError\] \[HTTP Failed\] \[410: Gone\] b'The page you requested was removed.'",
                'if': lambda log_line: log_line.lvl == "WARNING"
            },
            {
                'message': r"Daemon VM is provisioned, but the VM unique identifier has changed -- clearing cached state"
            }
        ]

        if ignore is not None:
            ignore_list.extend(ignore)

        def is_error(log_line):
            return any(err in log_line.line for err in error_tags)

        def can_be_ignored(log_line):
            return any(re.search(msg['message'], log_line.line) is not None and ('if' not in msg or msg['if'](log_line)) for msg in ignore_list)

        errors = []

        for agent_log_line in parse_agent_log_file(waagent_log):
            if is_error(agent_log_line) and not can_be_ignored(agent_log_line):
                # Handle "/proc/net/route contains no routes" as a special case since it can take time for the
                # primary interface to come up and we don't want to report transient errors as actual errors
                if "/proc/net/route contains no routes" in agent_log_line.line:
                    no_routes_error = agent_log_line.line
                    provisioning_complete = False
                else:
                    errors.append(agent_log_line.line)

            # currently this message is not reported as an error, but flag it.
            if "The agent's cgroup includes unexpected processes:" in agent_log_line.line:
                errors.append(agent_log_line.line)

            if "Provisioning complete" in agent_log_line.line:
                provisioning_complete = True

    except IOError as e:
        print(e)
        sys.exit(127)

    # Keep the "no routes found" as a genuine error message if it was never corrected
    if no_routes_error is not None and not provisioning_complete:
        errors.append(no_routes_error)

    if len(errors) > 0:
        print('waagent.log contains the following ERROR log(s): \n {0}'.format(errors))
        exit_code = 1

    if exit_on_completion:
        sys.exit(exit_code)

    return exit_code == 0


def is_data_in_waagent_log(data):
    """
    This function looks for the specified test data string in the WALinuxAgent logs and returns if found or not.
    :param data: The string to look for in the agent logs
    :return: True if test data string found in the agent log and False if not.
    """
    for agent_log_line in parse_agent_log_file():
        if data in agent_log_line.line:
            print("Found data: {0} in line: {1}".format(data, agent_log_line.line))
            return True

    print("waagent.log file did not have the data string: {0}".format(data))
    return False

