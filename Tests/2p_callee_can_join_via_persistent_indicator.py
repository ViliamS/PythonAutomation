# -*- coding: utf-8 -*-


def setup(context, caller, callee):
    caller.prepare_test_env(context['config'])

    callee.prepare_test_env(
                                context['config'],
                                caller.get_test_accounts(),
                                caller.get_test_channel_data()
                            )


def create_test_flow_description():
    flow_description = """
***********************************************************************
TEST FLOW DESCRIPTION
***********************************************************************
1. Caller and callee users log in
2. Caller and callee open test team channel
3. Caller initiates a call
4. Caller waits until callee joins a call
5. Callee scrolls up and wait until persistent indicator with Join button appears
6. Callee clicks at join call button
7. Caller and callee check that both are on the same call
***********************************************************************
"""
    return flow_description


def test(context, caller, callee):

    caller_username = callee.get_test_account(0)['username']
    callee_username = callee.get_test_account(1)['username']

    meetup_title = caller.generate_string()

    caller.login(caller.get_test_account(0))
    callee.login(callee.get_test_account(1))

    # Caller and callee open same conversation
    caller.navigate_to_channel()
    callee.navigate_to_channel()

    # Caller calls
    caller.click_at_start_call_button(meetup_title=meetup_title, wait_for_seconds_after_call_start = 60)

    # Callee scrolls up and waits until persistent indicator with Join button appears and joins meetup
    callee.wait_for_jump_in_button(initiator_email=caller_username, scroll_down=False)
    callee.wait_for_jump_in_button_persistent_and_join(meetup_title)

    # Caller and callee check that both are on the same call
    caller.wait_for_participant_to_appear_in_call(participant_email=callee_username, group_call=False)
    callee.wait_for_participant_to_appear_in_call(participant_email=caller_username, group_call=False)

def teardown(context, caller, callee):
    pass