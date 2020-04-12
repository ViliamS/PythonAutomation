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
6. Caller verifies call quality feedback request is displayed for hang up call
7. Caller rates call with 5 stars
8. Caller verifies that call quality feedback thank you confirmation is displayed
***********************************************************************************
"""
    return flow_description


def test(context, caller):

    # Login to the app and open test channel
    caller_username = caller.get_test_account(0)

    caller.login(caller_username)
    caller.navigate_to_channel()

    # Start a meetup then hang up
    caller.click_at_start_call_button()
    call_id = caller.get_call_id()
    caller.wait_for_seconds(10)
    caller.hang_up_ongoing_call()

    # Rate call quality with 5 stars
    caller.wait_for_call_quality_feedback_request_to_be_displayed_for_call_id(call_id)
    caller.rate_call_quality_feedback_for_call_id_with_n_stars(call_id, 5, scroll_to_elem=True)
    caller.wait_for_call_quality_feedback_thank_you_confirmation_for_call_id(call_id)
