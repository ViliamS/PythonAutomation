# -*- coding: utf-8 -*-

def setup(context, caller):
    caller.prepare_test_env(context['config'])

def create_test_flow_description():
    flow_description = """
***********************************************************************************
TEST FLOW DESCRIPTION
***********************************************************************************
1. Caller user logs in
2. Caller navigates to test team channel
3. Caller initiates a call
4. Call runs for 10 seconds
5. Caller hangs up a call
6. Call quality feedback request is displayed for the call
7. Caller traverses the whole call quality form by the tab enter and arrow keys
8. Caller submits the CQF form
***********************************************************************************
"""
    return flow_description

def test(context, caller):
    caller_username = caller.get_test_account(0)

    caller.login(caller_username)
    caller.navigate_to_channel()

    # create a call then hang up
    caller.click_at_start_call_button()
    call_id = caller.get_call_id()
    caller.wait_for_seconds(10)
    caller.hang_up_ongoing_call()
    
    # CQF related actions
    caller.wait_for_call_quality_feedback_request_to_be_displayed_for_call_id(call_id)
    caller.traverse_call_quality_feedback_for_call_id(call_id, 2)

def teardown(context, caller):
    pass