from __future__ import print_function

from time import sleep

from dungeon_crawler.scenarios_utils.agent_log_parser import parse_agent_log_file


def check_agent_log(max_retry=3):
    retries = 0
    exit_code = 0
    verbose = False
    host_plugin_used = False
    errors = []
    warnings = []

    while not host_plugin_used and retries < max_retry:
        errors = []
        warnings = []
        for agent_log_line in parse_agent_log_file():

            if not agent_log_line.matched:
                continue

            if 'switching to host plugin' in agent_log_line.msg\
                    or 'InitializeHostPlugin' in agent_log_line.msg\
                    or 'status to host plugin' in agent_log_line.msg:
                host_plugin_used = True
            elif 'WARNING' == agent_log_line.lvl:
                if agent_log_line.msg not in warnings:
                    warnings.append(agent_log_line.msg)

            if 'VERBOSE' == agent_log_line.lvl:
                verbose = True
            elif 'ERROR' == agent_log_line.lvl:
                errors.append(agent_log_line.line)

            if 'TelemetryData' in agent_log_line.msg:
                continue

        retries += 1
        if not host_plugin_used and retries<max_retry:
            print('host plugin not used, sleeping for 30 seconds...')
            sleep(30)

    if len(errors) > 0:
        print('waagent.log contains the following errors:')
        for error in errors:
            print('  --> ' + error)
        exit_code += 1

    if not verbose:
        print('verbose logs not found')
        exit_code += 1

    if not host_plugin_used:
        print('host plugin was not used')
        exit_code += 1

    if len(warnings) > 0:
        print('waagent.log contains the following warnings:')
        for warning in warnings:
            print('  --> ' + warning)

    return exit_code
