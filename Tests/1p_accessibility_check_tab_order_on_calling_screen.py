# -*- coding: utf-8 -*-

def setup(context, caller):
    caller.prepare_test_env(context['config'])


def create_test_flow_description():
    flow_description = """
*****************************************************************************************
TEST FLOW DESCRIPTION
*****************************************************************************************
1. Caller user logs in
2. Caller navigates to test team channel
3. Caller initiates a call
4. Caller navigates through the calling screen with TAB key and checks the desired order
*****************************************************************************************
"""
    return flow_description

def test(context, caller):
    caller_username = caller.get_test_account(0)

    caller.login(caller_username)
    caller.navigate_to_channel()
    caller.click_at_start_call_button()

    #turn off the video
    caller.check_tab_order_calling_screen(click_to_start_elem=True)
