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
4. Caller checks that calling screen is opened
5. Caller navigates to test team channel (multitasking)
6. Caller checks that in-app call monitor is displayed
7. Caller returns to the call by clicking on in-app call monitor
8. Caller checks that calling screen is opened
***********************************************************************
"""
    return flow_description

def test(context, caller):
    caller_username = caller.get_test_account(0)

    caller.login(caller_username)
    caller.navigate_to_channel()
    caller.click_at_start_call_button()
    caller.is_in_call()
    caller.navigate_from_call_to_channel()
    caller.check_in_app_call_monitor()
    caller.navigate_back_to_call()
    caller.is_in_call()
