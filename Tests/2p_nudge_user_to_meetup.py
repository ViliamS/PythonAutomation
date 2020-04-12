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
2. Caller opens test team channel
3. Caller initiates a call
4. Caller invites callee to the call from add participant in-call pane
6. Callee waits for call notification to appear
7. Callee joins a call from call notification
7. Caller and callee check that both are on the same call
***********************************************************************
"""
    return flow_description


def test(context, caller, callee):

    caller_username = callee.get_test_account(0)['username']
    callee_username = callee.get_test_account(1)['username']

    callee.login(callee.get_test_account(1))
    caller.login(caller.get_test_account(0))

    # Caller opens testing channel
    caller.navigate_to_channel()

    # Caller calls
    caller.click_at_start_call_button()
    caller.add_participant_to_meetup(callee_username)

    callee.join_call_from_call_notification(is_meetup=True)

    caller.wait_for_participant_to_appear_in_call(participant_email=callee_username, group_call=False)
    callee.wait_for_participant_to_appear_in_call(participant_email=caller_username, group_call=False)

def teardown(context, caller, callee):
    pass