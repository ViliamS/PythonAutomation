# -*- coding: utf-8 -*-


def setup(context, caller, callee):
    caller.prepare_test_env(context['config'])
    callee.prepare_test_env(context['config'], caller.get_test_accounts(), caller.get_test_channel_data())


def create_test_flow_description():
    flow_description = """
***********************************************************************
TEST FLOW DESCRIPTION
***********************************************************************
1. Caller and callee users log in
2. Caller and callee open test team channel
3. Caller initiates a call
4. Caller waits until callee joins a call
5. Callee waits until ongoing call indication appears in the team channel chat pane
6. Callee clicks at join call button
7. Caller and callee check that both are on the same call
8. Callee quits a call
9. Callee joins a call again
10. Caller and callee verify that both are on the same call again
***********************************************************************
"""
    return flow_description


def test(context, caller, callee):

    caller_username = callee.get_test_account(0)['username']
    callee_username = callee.get_test_account(1)['username']

    caller.login(caller.get_test_account(0))
    callee.login(callee.get_test_account(1))

    # Caller and callee open same conversation
    caller.navigate_to_channel()
    callee.navigate_to_channel()

    # Caller calls
    caller.click_at_start_call_button()
    call_id = caller.get_call_id()

    #callee.wait_for_jump_in_button_and_join_call(caller_username)
    callee.wait_for_join_button_and_join_call(call_id)

    # Verify that both users are on the call
    caller.wait_for_participant_to_appear_in_call(participant_email=callee_username, group_call=False)
    callee.wait_for_participant_to_appear_in_call(participant_email=caller_username, group_call=False)

    # Callee hangs up
    callee.hang_up_ongoing_call()
    caller.wait_for_participant_to_leave_a_call(callee_username)

    # Callee rejoins call
    #callee.wait_for_jump_in_button_and_join_call(caller_username)
    callee.wait_for_join_button_and_join_call(call_id)

    # Verify that both users are on the call
    caller.wait_for_participant_to_appear_in_call(participant_email=callee_username, group_call=False)
    callee.wait_for_participant_to_appear_in_call(participant_email=caller_username, group_call=False)


def teardown(context, caller, callee):
    pass