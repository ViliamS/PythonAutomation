# -*- coding: utf-8 -*-


def setup(context, caller, callee):
    caller.prepare_test_env(context['config'])
    callee.prepare_test_env(context['config'], caller.get_test_accounts(), caller.get_test_channel_data())


def create_test_flow_description():
    flow_description = """
***********************************************************************
TEST FLOW DESCRIPTION
***********************************************************************
1. Caller and callee log in
2. Caller navigates to test channel
3. Callee opens 1:1 chat with caller
4. Caller clicks at New chat button in the left panel
4. Caller creates an 1:1 chat with callee
5. Caller sends a message
6. Callee verifies message received
7. Caller verifies call buttons are present and starts a call
8. Caller and callee verify that call is started successfully
***********************************************************************
"""
    return flow_description


def test(context, caller, callee):

    mesg = "%s, may I call you?" % caller.generate_string(prefix="Hey ")

    caller_username = caller.get_test_account(0)['username']
    callee_username = caller.get_test_account(1)['username']

    caller.login(caller.get_test_account(0))
    callee.login(callee.get_test_account(1))

    # Caller navigates to test channel
    caller.navigate_to_channel()
    callee.open_chat_with_person(caller_username)

    # Caller opens 1:1 chat with callee
    caller.open_chat_with_person(callee_username, from_channel=True)

    # Caller calls
    caller.send_message_to_conversation(mesg)
    callee.verify_message_received_in_conversation(mesg)
    callee.send_message_to_conversation("OK.")
    caller.wait_and_click_at_start_1_1_call_button()
    callee.wait_for_join_call_button_and_join_call()

    caller.wait_for_participant_to_join_1_1_call(callee_username)
    caller.wait_for_seconds(10)

    caller.wait_for_participant_to_appear_in_call(participant_email=callee_username, group_call=True)
    callee.wait_for_participant_to_appear_in_call(participant_email=caller_username, group_call=True)


def teardown(context, caller, callee):
    pass