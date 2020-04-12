# -*- coding: utf-8 -*-

def setup(context, rpcclient):
    rpcclient.prepare_test_env(context['config'])


def create_test_flow_description():
    flow_description = """
***********************************************************************
TEST FLOW DESCRIPTION
***********************************************************************
1. User launches SkypeSpaces app
2. If user logged in, then logout and log in again
3. Else if user not logged in, then log in
4. Check whether user is logged in successfully
***********************************************************************
"""
    return flow_description


def test(context, rpcclient):
    """
    User can log in to the application
    """

    rpcclient.login(rpcclient.get_test_account(0))
    rpcclient.wait_for_seconds(10)

    if rpcclient.is_user_logged_in():
        print("TEST PASSED.")
        pass
    else:
        raise Exception("TEST FAILED")


def teardown(context, rpcclient):
    #rpcclient.app_cleanup()
    #rpcclient.uninstall_skypespaces()
    pass
