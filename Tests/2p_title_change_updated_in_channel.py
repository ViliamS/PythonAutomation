# -*- coding: utf-8 -*-


def setup(context, caller, callee):
    caller.prepare_test_env(context['config'])
    callee.prepare_test_env(context['config'], caller.get_test_accounts(), caller.get_test_channel_data())


def create_test_flow_description():
    flow_description = """
***********************************************************************
TEST FLOW DESCRIPTION
***********************************************************************
1. Caller creates a call with title1
2. Observer opens channel where call is in the progress
3. Caller changes meetup title in calling screen to title2
4. Observer verifies that meetup title is updated to title2 in the channel
***********************************************************************
"""
    return flow_description


def test(context, caller, observer):

    caller_username = caller.get_test_account(0)['username']

    new_title = caller.generate_string()

    caller.login(caller.get_test_account(0))
    observer.login(observer.get_test_account(1))

    # Caller and callee open same conversation
    caller.navigate_to_channel()
    observer.navigate_to_channel()

    # Caller calls
    caller.click_at_start_call_button()
    call_id = caller.get_call_id()

    # Observer waits until meetup is seen in the channel
    #observer.wait_for_jump_in_button(caller_username)
    observer.wait_for_jump_in_button_by_call_id(call_id)

    # Caller changes meetup title in the calling screen
    caller.change_meetup_title_in_calling_header(new_title)

    # Observer verifies that meetup title in the channel was updated accordingly
    #observer.wait_for_meetup_title_update_in_channel(caller_username, new_title)
    observer.wait_for_meetup_title_update_in_channel_by_call_id(call_id, new_title)


def teardown(context, caller, callee):
    pass
