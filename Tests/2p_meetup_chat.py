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
3. Caller initiates a call in the channel
4. Callee joins a call
5. Caller opens in-call chat
6. Caller sends message to the in-call chat
7. Caller sees his message to appear in in-call chat pane
8. Callee sees incoming message in in-call chat pane
***********************************************************************
"""
    return flow_description


def test(context, caller, callee):

    caller_username = callee.get_test_account(0)['username']
    callee_username = callee.get_test_account(1)['username']

    message = "Hey have you heard about %s?" % caller.generate_string(prefix="incident ")

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

    caller.wait_for_participant_to_appear_in_call(participant_email=callee_username, group_call=False)
    callee.wait_for_participant_to_appear_in_call(participant_email=caller_username, group_call=False)

    # Caller opens in-call chat
    caller.open_in_call_chat()
    callee.open_in_call_chat()

    # Caller sends message to in-call chat and verifies it is visible in his chat pane
    caller.send_message_to_conversation(message)
    caller.verify_message_received_in_conversation(message)

    # Callee verifies message is received and visible in in-call chat
    callee.verify_message_received_in_conversation(message)


def teardown(context, caller, callee):
    pass