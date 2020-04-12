# -*- coding: utf-8 -*-
from async_calls import async_call, async_call_daemon, wait_for_threads_to_finish


def setup(context, caller, *callees):
    caller.prepare_test_env(context['config'])


def create_test_flow_description():
    flow_description = """
***********************************************************************
TEST FLOW DESCRIPTION
***********************************************************************
1. Caller and callees users log in
2. Caller creates group chat with the callees
3. Caller initiates a call
4. Caller waits until callees join a call
6. Callees click at join call button by clicking at a join button in the group chat header
7. Caller and callees check that both are on the same call
***********************************************************************
"""
    return flow_description


def login_caller(agent):
    accounts = agent.get_test_accounts()

    agent.login(accounts[0])


def login_callee(agent, config, agent_index, test_accounts, test_channel):
    agent.prepare_test_env(config, test_accounts, test_channel)

    agent.login(test_accounts[agent_index])


def execute_caller(agent, mesg, callees_count):
    accounts = agent.get_test_accounts()
    usernames = []
    for account in accounts[1:]:
        usernames.append(account["username"])
    agent.open_chat_with_people(usernames)
    agent.wait_and_click_at_start_1_1_call_button()
    agent.wait_until_number_of_participants_in_call(callees_count, group_call=True)
    for acc in accounts[1:]:
        agent.wait_for_participant_to_appear_in_call(participant_email=acc['username'], group_call=True, timeout=30)
    agent.hang_up_ongoing_call(by_js=True)


def execute_callee(agent, agent_index, test_accounts):
    agent.wait_for_call_notification_to_be_opened()
    usernames = []
    for index, account in enumerate(test_accounts):
        if index == agent_index:
            continue
        usernames.append(account["username"])
    agent.open_chat_with_people(usernames)
    agent.wait_for_join_call_button_and_join_call()
    agent.wait_for_participant_to_appear_in_call(test_accounts[0]['username'])


def test(context, caller, *callees):
    mesg = "%s, may I call you?" % caller.generate_string(prefix="Hey ")

    test_accounts = caller.get_test_accounts()
    test_channel = caller.get_test_channel_data()

    t_callees = []

    # login caller
    t_caller = async_call_daemon(login_caller, caller)

    # login callees
    for index, callee in enumerate(callees, start=1):
        t_callees.append(async_call_daemon(login_callee, callee, context['config'], index, test_accounts, test_channel))

    # wait until all the agents are logged in
    wait_for_threads_to_finish(threads=[t_caller] + t_callees, quit_on_1st_thread_finished=False, ignore_exceptions=False)

    t_callees = []

    # spawn caller worker
    t_caller = async_call_daemon(execute_caller, caller, mesg, len(callees))

    # spawn callee workers and wait for them to finish
    for index, callee in enumerate(callees, start=1):
        t_callees.append(async_call_daemon(execute_callee, callee, index, test_accounts))

    # wait until child workers finish their jobs
    wait_for_threads_to_finish(threads=[t_caller] + t_callees, quit_on_1st_thread_finished=True, ignore_exceptions=False)


def teardown(context, caller, *callees):
    pass