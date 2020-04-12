# -*- coding: utf-8 -*-


def setup(context, caller, *callees):
    caller.prepare_test_env(context['config'])
    for agent in callees:
        agent.prepare_test_env(context['config'], caller.get_test_accounts(), caller.get_test_channel_data())


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
***********************************************************************
"""
    return flow_description


def test(context, caller, *callees):
    # Login caller and callees

    caller.login(caller.get_test_account(0))

    for index, agent in enumerate(callees, start=1):
        agent.login(agent.get_test_account(index))

    # Caller and callees open same conversation
    caller.navigate_to_channel()
    for agent in callees:
        agent.navigate_to_channel()

    # Caller calls
    caller.click_at_start_call_button()
    call_id = caller.get_call_id()
    for agent in callees:
        #agent.wait_for_jump_in_button_and_join_call(agent.get_test_account(0)['username'])
        agent.wait_for_join_button_and_join_call(call_id)

    for account in caller.get_test_accounts()[1:]:
        caller.wait_for_participant_to_appear_in_call(participant_email=account['username'], group_call=False)
    for agent in callees:
        agent.wait_for_participant_to_appear_in_call(participant_email=agent.get_test_account(0)['username'], group_call=False)

    # Check whether all the callees are visible in a call
    for account in caller.get_test_accounts()[1:]:
        caller.check_participant_in_call(account['username'])


def teardown(context, caller, *callees):
    pass