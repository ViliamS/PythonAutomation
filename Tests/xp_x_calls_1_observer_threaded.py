# -*- coding: utf-8 -*-
from async_calls import async_call, async_call_daemon, wait_for_threads_to_finish


def setup(context, observer, *callers):
    observer.prepare_test_env(context['config'])


def create_test_flow_description():
    flow_description = """
***********************************************************************
TEST FLOW DESCRIPTION
***********************************************************************
1. Observer and caller users log in
2. Observer and callers open test team channel
3. Callers initiate calls in the same channel
4. Observer checks that all the calls are visible in the channel
***********************************************************************
"""
    return flow_description


def execute_observer(agent):
    accounts = agent.get_test_accounts()

    agent.login(accounts[0])
    agent.navigate_to_channel()
    for acc in accounts[1:]:
        agent.wait_for_jump_in_button(acc['username'])


def execute_caller(agent, config, agent_index, test_accounts, test_channel):
    #in_call_wait = 600
    agent.prepare_test_env(config, test_accounts, test_channel)

    agent.login(test_accounts[agent_index])
    agent.navigate_to_channel()
    agent.click_at_start_call_button()
    #agent.wait_for_seconds(in_call_wait)


def test(context, observer, *callers):

    t_callers = []

    test_accounts = observer.get_test_accounts()
    test_channel = observer.get_test_channel_data()

    # spawn observer worker
    t_observer = async_call_daemon(execute_observer, observer)

    # spawn caller workers and wait for them to finish
    for index, caller in enumerate(callers, start=1):
        t_callers.append(async_call_daemon(execute_caller, caller, context['config'], index, test_accounts, test_channel))

    # wait until child workers finish their jobs
    wait_for_threads_to_finish(threads=[t_observer] + t_callers, quit_on_1st_thread_finished=True)


def teardown(context, observer, *callers):
    pass