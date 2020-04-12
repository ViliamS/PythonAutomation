# -*- coding: utf-8 -*-

def setup(context, caller):
    caller.prepare_test_env(context['config'])


def create_test_flow_description():
    flow_description = """
***********************************************************************
TEST FLOW DESCRIPTION
***********************************************************************
1. Caller user logs in
2. Caller navigates to test team channel
3. Caller initiates a call
4. Caller check that his video preview is displayed on stage
5. Caller toggles video and checks that his avatar is displayed
6. Caller toggles video again and checks that his video preview is back on stage
***********************************************************************
"""
    return flow_description

def test(context, caller):
    caller_username = caller.get_test_account(0)

    caller.login(caller_username)

    caller.navigate_to_channel()
    caller.click_at_start_call_button()

    #turn off the video
    caller.ongoing_call_turn_video()
    caller.check_myself_avatar(timeout=10, fail_on_not_found=False)

    #turn on the video
    caller.ongoing_call_turn_video()
    caller.check_myself_video(timeout=10, fail_on_not_found=False)
    caller.hang_up_ongoing_call()