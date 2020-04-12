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
2. Caller opens an 1:1 chat with the callee
3. Caller initiates a call
5. Callee waits until ongoing call indication appears in the team channel chat pane
6. Callee clicks at call decline button
7. Call is not started
***********************************************************************
"""
    return flow_description


def test(context, caller, callee):

    caller_username = caller.get_test_account(0)['username']
    callee_username = caller.get_test_account(1)['username']

    caller.login(caller.get_test_account(0))
    callee.login(callee.get_test_account(1))

    # Caller and callee open same conversation
    caller.open_chat_with_person(callee_username)
    callee.open_chat_with_person(caller_username)

    # Caller calls
    caller.wait_and_click_at_start_1_1_call_button()
    callee.wait_for_join_call_button_and_reject_call()

    caller.wait_for_seconds(10)

    caller.check_1_1_chat_opened_with_user(callee_username)
    callee.check_1_1_chat_opened_with_user(caller_username)


def teardown(context, caller, callee):
    pass