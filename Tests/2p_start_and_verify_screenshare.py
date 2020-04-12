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
8. Callee will start screen share
9. Caller will check if screen share was properly displayed
***********************************************************************
"""
    return flow_description


def test(context, caller, callee):

    caller_username = callee.get_test_account(0)['username']
    callee_username = callee.get_test_account(1)['username']

    caller.login(caller.get_test_account(0))
    callee.login(callee.get_test_account(1))

    # Caller and callee open same conversation
    caller.open_chat_with_person(callee_username)
    callee.open_chat_with_person(caller_username)

    # Caller calls
    caller.wait_and_click_at_start_1_1_call_button()
    callee.wait_for_join_call_button_and_join_call()

    caller.wait_for_participant_to_join_1_1_call(callee_username)
    caller.wait_for_seconds(10)

    caller.wait_for_participant_to_appear_in_call(participant_email=callee_username, group_call=True)
    callee.wait_for_participant_to_appear_in_call(participant_email=caller_username, group_call=True)

    # Callee will start screen share
    callee.click_at_share_desktop_button()

    # Caller will check if screen share was properly displayed
    caller.wait_for_participant_to_start_screen_share(callee_username)


def teardown(context, caller, callee):
    pass