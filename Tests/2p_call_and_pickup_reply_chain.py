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
4. Caller hangs up after 10 seconds
5. Caller sends a message to the meetup's reply chain
6. Caller starts a new meetup in reply chain of the original call
5. Callee waits until ongoing reply chain call indication appears in the team channel chat pane
6. Callee clicks at join call button
7. Caller and callee check that both are on the same call
***********************************************************************
"""
    return flow_description


def test(context, caller, callee):

    message = "Replying to you with %s" % caller.generate_string(prefix="message ")

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
    caller.wait_for_seconds(10)
    caller.hang_up_ongoing_call()

    caller.wait_for_meetup_ended_msg_in_channel(call_id=call_id)
    caller.reply_message_to_conversation_by_call_id(call_id=call_id, mesg=message)

    caller.click_at_start_call_button(reply_chain_call_id=call_id)
    call_id_reply_chain = caller.get_call_id()
    caller.wait_for_seconds(10)

    callee.wait_for_join_button_and_join_call(call_id_reply_chain)

    caller.wait_for_participant_to_appear_in_call(participant_email=callee_username, group_call=False)
    callee.wait_for_participant_to_appear_in_call(participant_email=caller_username, group_call=False)


def teardown(context, caller, callee):
    pass