# -*- coding: utf-8 -*-
import time

import logging

from async_calls import async_call_daemon, wait_for_threads_to_finish

number_of_call_participants = 4
one_leave_update_start = None


def setup(context, caller, *agents):
    caller.prepare_test_env(context['config'])


def create_test_flow_description():
    flow_description = """
***********************************************************************
TEST FLOW DESCRIPTION
***********************************************************************
1. Caller, callees and observers users log in
2. Caller, callees and observers open test team channel
3. Caller initiate a call in the same channel
4. Caller waits until callees join the call
5. Callees wait until ongoing call indication appears in the team channel chat pane
6. Callees click on join call button
7. Caller verifies that all callees are in the call
8. All observers check that the call is visible in the channel and can see number of participants in that call
9. One callee leaves the call
10. All observes check that the number of participants in that call is updated accordingly
11. One callee joins the call again
12. All observes check that the number of participants in that call is updated accordingly
***********************************************************************
"""


def execute_caller(agent, callees_count):
    accounts = agent.get_test_accounts()

    agent.login(accounts[0])
    agent.navigate_to_channel()
    agent.click_at_start_call_button()
    agent.wait_until_number_of_participants_in_call(callees_count)


def execute_callee(agent, config, agent_index, test_accounts, test_channel):
    agent.prepare_test_env(config, test_accounts, test_channel)

    agent.login(test_accounts[agent_index])
    agent.navigate_to_channel()
    agent.wait_for_jump_in_button_and_join_call(test_accounts[0]['username'])
    agent.wait_for_participant_to_appear_in_call(participant_email=test_accounts[0]['username'], group_call=False)


def execute_observer(agent, config, agent_index, number_of_participants, test_accounts):
    agent.prepare_test_env(config, test_accounts)

    agent.login(test_accounts[agent_index])
    agent.navigate_to_channel()
    agent.wait_until_number_of_participants_in_channel_calling_header(test_accounts[0]['username'],
                                                                      number_of_participants)


def execute_observer_live_roster_check(agent, caller_username, number_of_participants):
    agent.wait_until_number_of_participants_in_channel_calling_header(caller_username,
                                                                      number_of_participants, step=0.1)

    # Stop counter to measure the time until observer gets update about call participant hang up
    measure_stop = time.time()

    # Print measured time to the test agent logs
    agent.compute_measurement(one_leave_update_start, measure_stop, "Live roster update received after: ")


def test(context, caller, *agents):
    t_callees = []
    t_observers = []

    if len(agents) + 1 <= number_of_call_participants:
        raise Exception("Not enough call agents used to be able to create %d-party call" % number_of_call_participants)

    callees = agents[1:number_of_call_participants]
    logging.info("callees = agents[1:number_of_call_participants] is '{0}'".format(str(callees)))

    observers = agents[number_of_call_participants:]
    logging.info("observers = agents[number_of_call_participants:] is '{0}'".format(str(observers)))

    number_of_participants = len(callees) + 1  # plus caller
    logging.info("number_of_participants = len(callees) + 1  # plus caller is '{0}'".format(str(number_of_participants)))

    test_accounts = caller.get_test_accounts()
    test_channel = caller.get_test_channel_data()

    # spawn caller worker
    t_caller = async_call_daemon(execute_caller, caller, len(callees))

    # spawn callee workers and wait for them to finish
    for index, callee in enumerate(callees, start=1):
        t_callees.append(async_call_daemon(execute_callee, callee, context['config'], index, test_accounts, test_channel))

    # spawn observers workers and wait for them to finish
    for index, observer in enumerate(observers, start=number_of_call_participants):
        t_observers.append(async_call_daemon(execute_observer, observer, context['config'], index, number_of_participants, test_accounts))

    # wait until child workers finish their jobs
    wait_for_threads_to_finish(threads=[t_caller] + t_callees + t_observers, quit_on_1st_thread_finished=False, ignore_exceptions=False)

    # Verify that observers see update in call live roster (one call participant less)
    t_observers = []
    for index, observer in enumerate(observers, start=number_of_call_participants):
        t_observers.append(async_call_daemon(execute_observer_live_roster_check, observer, test_accounts[0]['username'], number_of_participants - 1))

    # Start counter to measure the time until observer gets update about call participant hang up
    global one_leave_update_start
    one_leave_update_start = time.time()

    # One call participant leaves a call
    t_leaver = async_call_daemon(callees[0].hang_up_ongoing_call, by_js=True)

    # wait until child workers finish their jobs
    wait_for_threads_to_finish(threads=[t_leaver] + t_observers, quit_on_1st_thread_finished=False, ignore_exceptions=False)
