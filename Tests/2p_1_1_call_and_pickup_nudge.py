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
4. Caller waits until callee joins a call
5. Callee waits until call notification appears
6. Callee joins call from the notification
7. Caller and callee check that both are on the same call
***********************************************************************
"""
    return flow_description


def test(context, caller, callee):

    mesg = "%s, may I call you?" % caller.generate_string(prefix="Hey ")

    caller_username = caller.get_test_account(0)['username']
    callee_username = caller.get_test_account(1)['username']

    caller.login(caller.get_test_account(0))
    callee.login(callee.get_test_account(1))

    # Caller and callee open same conversation
    caller.open_chat_with_person(callee_username)
    callee.open_chat_with_person(caller_username)

    # Caller calls
    caller.send_message_to_conversation(mesg)
    caller.verify_message_received_in_conversation(mesg)
    callee.send_message_to_conversation("OK.")
    caller.wait_and_click_at_start_1_1_call_button()

    callee.join_call_from_call_notification(is_meetup=False)

    caller.wait_for_participant_to_join_1_1_call(callee_username)
    caller.wait_for_seconds(10)

    caller.wait_for_participant_to_appear_in_call(participant_email=callee_username, group_call=True)
    callee.wait_for_participant_to_appear_in_call(participant_email=caller_username, group_call=True)


def teardown(context, caller, callee):
    pass