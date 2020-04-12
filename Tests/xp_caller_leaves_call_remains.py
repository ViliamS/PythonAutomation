# -*- coding: utf-8 -*-
from async_calls import async_call, async_call_daemon, wait_for_threads_to_finish

call_id = None
timeout = 300


def setup(context, caller, *callees):
    caller.prepare_test_env(context['config'])


def create_test_flow_description():
    flow_description = """
***********************************************************************
TEST FLOW DESCRIPTION
***********************************************************************
1. Caller and callees users log in
2. Caller and callees open test team channel
3. Caller initiates a call
4. Caller waits until callees join a call
5. Callees wait until ongoing call indication appears in the team channel chat pane
6. Callees click at join call button
7. Caller and callees check that both are on the same call
8. Caller leaves a call
9. Callees verify that call is still in progress
***********************************************************************
"""
    return flow_description


def execute_caller(agent, callees_count):
    global call_id
    accounts = agent.get_test_accounts()

    agent.login(accounts[0])
    agent.navigate_to_channel()
    agent.click_at_start_call_button()
    call_id = agent.get_call_id()
    agent.wait_until_number_of_participants_in_call(callees_count)
    for acc in accounts[1:]:
        agent.wait_for_participant_to_appear_in_call(participant_email=acc['username'], group_call=False)
        agent.wait_for_seconds(60)
    agent.hang_up_ongoing_call(by_js=True)


def execute_callee(agent, config, agent_index, test_accounts, test_channel):
    import time
    step = 0
    global call_id
    agent.prepare_test_env(config, test_accounts, test_channel)
    agent.logout_if_logged_in()
    agent.login(test_accounts[agent_index])
    agent.navigate_to_channel()
    while not call_id and step < timeout:
        agent.write_to_run_log("[Agent #%d] step #%d: Call ID not detected yet, waiting.." % (agent_index, step))
        step += 1
        time.sleep(1)
    try:
        agent.wait_for_join_button_and_join_call(call_id)
    except Exception:
        agent.wait_for_jump_in_button_and_join_call(initiator_email=test_accounts [0]['username'])

    agent.wait_for_participant_to_appear_in_call(participant_email=test_accounts[0]['username'], group_call=False)
    agent.wait_for_participant_to_leave_a_call(test_accounts[0]['username'])
    agent.wait_for_seconds(10)
    agent.check_if_in_call()


def test(context, caller, *callees):
    t_callees = []

    test_accounts = caller.get_test_accounts()
    test_channel = caller.get_test_channel_data()

    # spawn caller worker
    t_caller = async_call_daemon(execute_caller, caller, len(callees))

    # spawn callee workers and wait for them to finish
    for index, callee in enumerate(callees, start=1):
        t_callees.append(async_call_daemon(execute_callee, callee, context['config'], index, test_accounts, test_channel))

    # wait until child workers finish their jobs
    wait_for_threads_to_finish(threads=[t_caller] + t_callees, quit_on_1st_thread_finished=False, ignore_exceptions=False)


def teardown(context, caller, *callees):
    pass