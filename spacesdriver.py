# -*- coding: utf-8 -*-

import os
import pdb
import string
import time
import random
import logging
import sys

from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains

from spaces_webdriver import SpacesWebDriver
from test_config_loader import TestConfigLoader
from platform_lib import PlatformLib
from xpath import XPathBuilder
from accessibility import Accessibility


try:
    from castro import Castro
except ImportError:
    import datetime

    print("[%s] %s" % (datetime.datetime.now(), "Video recording library not installed."))


class NotSupportedPlatformException(Exception):
    pass


class SkypeSpaces(object):

    UNINSTALL_APP_BEFORE_SETUP = True
    ENABLE_SLIMCORE = True
    ENABLE_CALLING_IN_BROWSER = True

    CSS = "css"
    XPATH = "xpath"
    ID = "id"

    LOADING_TIMEOUT = 90
    CALLING_TIMEOUT = 300
    LEAVE_TIMEOUT = 900

    CQF_SEARCH_LIMIT = 15
    CQF_DEFAULT_STARS = 3
    CQF_MAX_STARS = 5

    FORCE_WEB_URL_LOAD = False
    CONTAINER_ARG = "container"
    RING_ARG = "ring"

    ################
    # Element data #
    ################

    ELECTRON_APP_HANDLER_XPATH = "//body"

    CHANNEL_LOADING_SPINNER_DISPAYED = "//message-list//div[contains(@class,'vr-loadmore')][not(contains(@class,'hide-spinner'))]//busy-animation"
    CHANNEL_LOADING_SPINNER_NOT_DISPAYED = "//message-list//div[contains(@class,'vr-loadmore hide-spinner')]//busy-animation"

    WELCOME_TO_MICROSOFT_TEAMS_LETS_GO_BUTTON = "//button[@data-tid='routingSettingsInformational-letsGoBtn']"
    TEAMS_LOGIN_REDIRECTING_IS_VISIBLE = "//div[@id='redirect_cta_text'][contains(@style,'display: block')]"

    CHANNEL_MESSAGE_LIST_XPATH = "//virtual-repeat[contains(@class, 'ts-message-list')]"
    LOGIN_AREA = "//div[@id='loginArea']"
    MSFT_LOGIN_PAGE = "login.microsoftonline.com"
    SPACES_LOGIN_USE_ANOTHER_ACCOUNT_ID = "use_another_account"
    SPACES_LOGIN_USE_ANOTHER_ACCOUNT_LINK_ID = "use_another_account_link"
    USE_ANOTHER_ACCOUNT_ELEMENTS_LIST = "//*[@id='" + SPACES_LOGIN_USE_ANOTHER_ACCOUNT_ID + "' or @id='" + SPACES_LOGIN_USE_ANOTHER_ACCOUNT_LINK_ID + "']"
    SPACES_LOGIN_USERNAME_ID = "cred_userid_inputtext"
    SPACES_LOGIN_USERNAME_INPUT = "//input[@id='" + SPACES_LOGIN_USERNAME_ID + "']"
    SPACES_LOGIN_PASSWORD_ID = "cred_password_inputtext"
    SPACES_LOGIN_PASSWORD_INPUT = "//input[@id='" + SPACES_LOGIN_PASSWORD_ID + "']"
    SPACES_LOGIN_SUBMIT_ID = "cred_sign_in_button"
    SPACES_LOGIN_SUBMIT_BUTTON_XPATH = "//button[@id='" + SPACES_LOGIN_SUBMIT_ID + "']"
    SPACES_USER_INFO_ELEM_XPATH = "//div[@data-tid = 'userInformation']"
    SPACES_OPTIONS_DROPDOWN_BUTTON_ID = "personDropdown"
    SPACES_OPTIONS_DROPDOWN_BUTTON_XPATH = "//footer/button[@id='personDropdown']"
    SPACES_LOGOUT_BUTTON_ID = "logout-button"

    CALLING_NOT_SUPPORTED_MESG = "//div[contains(text(),'This feature is coming and will be available real soon')]"
    PLEASE_REFRESH_MSG = "Please refresh to try again"
    REFRESH_BTN_XPATH = "//button[.= 'Refresh']"

    MSFT_LOG_IN_WITH_USERNAME_AND_PASSWORD_LINK_XPATH = "//p[.='Sign in with a username and password instead']"

    MSFT_LOGIN_PASSWORD_ID = "passwordInput"
    MSFT_LOGIN_BUTTON_ID = "submitButton"

    SHOW_MORE_TEAMS_BUTTON_XPATH = "//a[@data-tid='team-overflow-moreBtn']"
    CALL_NOTIFICATION_WINDOW_XPATH = "//div[contains(@class,'notification')]"
    CALL_NOTIFICATION_WINDOW_IS_CALLING_MESG_XPATH = "//div[contains(@class, 'subtitle') and contains(., 'is calling you')]"
    CALL_NOTIFICATION_WINDOW_IS_NUDGING_MESG_XPATH = "//div[contains(@class, 'subtitle') and contains(., 'wants you to join a meeting')]"
    CALL_NOTIFICATION_ACCEPT_CALL_VIDEO_BUTTON_XPATH = "//button[contains(@class, 'call-video')]"
    CALL_NOTIFICATION_ACCEPT_CALL_AUDIO_BUTTON_XPATH = "//button[contains(@class, 'call-audio')]"
    CALL_NOTIFICATION_REJECT_CALL_BUTTON_XPATH = "//button[contains(@class, 'call-reject')]"
    CALL_NOTIFICATION_JUMP_IN_CALL_BUTTON_XPATH = "//button[contains(@class, 'jumpin')]"
    CALL_NOTIFICATION_CHAT_CALL_BUTTON_XPATH = "//button[contains(@class, 'chat')]"

    CHAT_SEARCH_INPUT_XPATH = "//div[@data-tid = 'left-rail-2']//input[@id = 'searchInput']"
    CHAT_SEARCH_BUTTON_XPATH = "//div[@data-tid = 'left-rail-2']//button[@data-tid = 'searchBtn']"
    CHAT_COMMON_COMMON_BTN_XPATH = "//button[(@data-tid = 'lr-create-chat-2') or (@data-tid = 'lr-create-chat-4') or (@data-tid = 'lr-create-chat') or contains(@data-tid , 'lr-create-chat')]"
    CHAT_COMMON_CREATE_CHAT_BTN_XPATH = CHAT_COMMON_COMMON_BTN_XPATH
    CHAT_CREATE_CHAT_BTN_XPATH = CHAT_COMMON_COMMON_BTN_XPATH
    TEAMS_CREATE_CHAT_BTN_XPATH = CHAT_COMMON_COMMON_BTN_XPATH
    CHAT_SEARCH_PEOPLE_TAB_XPATH = "//search//span[. = 'People']"
    CHAT_LINK_XPATH_TEMPLATE = "//individual-search-category-people//div/div[. = '%s']/.."
    CHAT_USERNAME_HEADER_XPATH_TEMPLATE = "//chat-header//img[@pl-upn = '%s']"
    CHAT_VIDEO_CALL_START_BUTTON_XPATH = "//calling-start-button[@with-video = 'true']/button"
    CHAT_AUDIO_CALL_START_BUTTON_XPATH = "//calling-start-button[not(@with-video) or @with-video = 'false']/button"
    CHAT_VIDEO_CALL_JOIN_BUTTON_XPATH = "//calling-join-button[not(@audio-only) or @audio-only = 'false']/button"
    CHAT_AUDIO_CALL_JOIN_BUTTON_XPATH = "//calling-join-button[@audio-only = 'true']/button"
    CHAT_VIDEO_CALL_REJECT_BUTTON_XPATH = "//calling-reject-button/button"
    CALL_1_1_PARTICIPANT_ANIMATION_XPATH_TEMPLATE = "//calling-animation-outgoing//img[@pl-upn = '%s']"
    CALL_1_1_JOIN_ERROR_STATE_XPATH = "//div[contains(@class, 'state-description-title')]"
    CHAT_ADD_PARTICIPANT_BUTTON_XPATH = "//chat-header//button[@data-tid = 'lr-create-group-chat']"
    CHAT_PEOPLE_PICKER_INPUT_XPATH = "//div[@data-tid = 'createNewChat']//chat-people-picker//input"
    CHAT_CREATE_NEW_INPUT_XPATH = "//chat-people-picker[@data-tid = 'mp-to-line']//input"
    CHAT_USER_CHOOSER_XPATH = "//div[@data-tid = 'peoplepicker-dropdown']//div[contains(@class, 'result-image')]"
    CHAT_ADD_USER_BUTTON_XPATH = "//div[@data-tid = 'createNewChat']//button[@data-tid = 'createChat-AddMembers']"
    CHAT_GROUP_HEADER_XPATH_TEMPLATE = "//chat-header//span[@pl-upn = '%s']"
    CHAT_RECENTS_ACTIVE_CALL_XPATH = "//div[@data-tid = 'left-rail-2']//active-calls-counter/span"
    CHAT_MESSAGE_TEMPLATE_XPATH = "//div[@data-tid='messageThreadBody']//div[@data-tid='messageBodyContent']/div[text()='%s']"

    CHANNEL_CONVERSATION_URL_TEMPLATE = "channel/%(team_name)s/%(channel_name)s/%(channel_thread_id)s/conversations?ctx=channel"
    CHANNEL_CONVERSATION_TITLE_TEMPLATE = "//h2[@data-tid = 'messagesHeader-Title' and . = '%s']"
    CHANNEL_CONVERSATION_CALL_START_BUTTON_XPATH = "//div[@id = 'add-new-message']//button[contains(@class, 'icons-call')][.//ng-include[contains(@src,'icons-call-meetup-line')]]"
    CHANNEL_CONVERSATION_CALL_TITLE_INPUT_XPATH = "//div[contains(@class, 'title-container')]/input[contains(@class, 'title')]"
    CHANNEL_CONVERSATION_NEW_CALL_START_BUTTON_XPATH = "//calling-start-button-rectangular/button"
    CHANNEL_CONVERSATION_JUMP_IN_BUTTON_MOST_RECENT_XPATH = "//calling-thread-header//calling-join-button[last()]/button"
    CHANNEL_CONVERSATION_JUMP_IN_BUTTON_FOR_INITIATOR_SPECIFIED_XPATH_TEMPLATE = "//div[contains(@class,'ts-calling-thread-header')][img[@pl-upn='%s']]//calling-join-button/button"
    CHANNEL_CONVERSATION_JOIN_BUTTON_BY_CALL_ID_TEMPLATE = "//button[@data-tid = 'join-btn-%s']"
    CHANNEL_CONVERSATION_CALL_STARTED_IN_PROGRESS_MESSAGE_TEMPLATE = "//div[@data-tid = 'in-progress-%s']"
    CHANNEL_CONVERSATION_MEETUP_TITLE_FOR_INITIATOR_SPECIFIED_XPATH_TEMPLATE = "//calling-thread-header[.//img[@pl-upn ='%s']]//div[contains(@class, 'title')]"
    CHANNEL_CONVERSATION_MEETUP_TITLE_FOR_CALL_ID_XPATH_TEMPLATE = "//calling-thread-header[.//button[contains(@data-tid , 'join-btn-%s')]]//div[contains(@class, 'title')]"
    CHANNEL_CONVERSATION_MEETUP_TITLE_FOR_ONGOING_MEETUP_TEMPLATE = "//calling-thread-header[.//button[contains(@data-tid,'join-btn-')]]"
    CHANNEL_CONVERSATION_MEETUP_TITLE_GETS_CHANGED_FOR_CALL_ID_XPATH_TEMPLATE = "//calling-thread-header[.//button[contains(@data-tid , 'join-btn-')]]//div[@title = '%s']"
    CHANNEL_PERSISTENT_INDICATOR_JUMP_IN_BUTTON_XPATH = "//calling-persistent-indicator//div[@title = '%s']/../..//calling-join-button/button"
    CHANNEL_CONVERSATION_AVATAR_IN_CALLING_HEADER_ROSTER_XPATH_TEMPLATE = "//calling-thread-header//calling-live-roster//img[@pl-upn = '%s']/../../img[@pl-upn]"
    CHANNEL_CALLING_LIVE_ROSTER_FOR_MEETUP_XPATH_TEMPLATE = "//calling-live-roster"

    CHANNEL_CONVERSATION_CALL_MONITOR_XPATH = "//calling-monitor/div[contains(@class, 'ts-show-cursor')]"
    CHANNEL_CONVERSATION_MEETUP_ENDED_XPATH_TEMPLATE = "(//div[contains(@class, 'ts-message-list-item')]//img[@pl-upn = '%s'])[last()]/../../../div[contains(., '%s')]"
    CHANNEL_CONVERSATION_MEETUP_ENDED_XPATH_DTID_TEMPLATE = "//div[@data-tid = 'call-ended-%s']"
    CHANNEL_CONVERSATION_MEETUP_IN_PROGRESS_XPATH_DTID_TEMPLATE = "//div[@data-tid = 'in-progress-%s']"
    CHANNEL_CONVERSATION_MEETUP_ENDED_MESG = "ended:"
    CHANNEL_PERSISTENT_INDICATOR_MORE_BUTTON_XPATH = "//calling-persistent-indicator//a[contains(@class, 'toggle-button')]"

    CQF_RATING_ELEM_XPATH_TEMPLATE = "//calling-thread-body[." + CHANNEL_CONVERSATION_MEETUP_ENDED_XPATH_DTID_TEMPLATE + "]//star-rating"
    CQF_NTH_STAR_XPATH_TEMPLATE = CQF_RATING_ELEM_XPATH_TEMPLATE + "//div[contains(@class, 'stars')]/a[%d]"
    CQF_THANKS_FOR_FEEDBACK_XPATH_TEMPLATE = "//calling-thread-body[." + CHANNEL_CONVERSATION_MEETUP_ENDED_XPATH_DTID_TEMPLATE + "]//thanks-for-feedback"
    CQF_THANKS_FOR_FEEDBACK_IN_PROGRESS_XPATH_TEMPLATE = "//calling-thread-body[." + CHANNEL_CONVERSATION_MEETUP_IN_PROGRESS_XPATH_DTID_TEMPLATE + "]//thanks-for-feedback"
    CQF_QUESTIONNAIRE_ITEMS_XPATH_TEMPLATE = "//calling-thread-body[." + CHANNEL_CONVERSATION_MEETUP_ENDED_XPATH_DTID_TEMPLATE + "]//calling-quality-feedback//div[contains(@class, 'questionnaire-items')]"
    CQF_QUESTIONNAIRE_BUTTONS_XPATH_TEMPLATE = "//calling-thread-body[." + CHANNEL_CONVERSATION_MEETUP_ENDED_XPATH_DTID_TEMPLATE + "]//calling-quality-feedback//div[contains(@class, 'questionnaire-buttons')]"
    CQF_QUESTIONNAIRE_ITEM_CALLING_XPATH_TEMPLATE = CQF_QUESTIONNAIRE_ITEMS_XPATH_TEMPLATE + "//div[contains(@class, 'type') and not(contains(@class, 'types'))][1]"
    CQF_QUESTIONNAIRE_ITEM_VIDEO_XPATH_TEMPLATE = CQF_QUESTIONNAIRE_ITEMS_XPATH_TEMPLATE + "//div[contains(@class, 'type') and not(contains(@class, 'types'))][2]"
    CQF_QUESTIONNAIRE_ITEM_PRESENTING_XPATH_TEMPLATE = CQF_QUESTIONNAIRE_ITEMS_XPATH_TEMPLATE + "//div[contains(@class, 'type') and not(contains(@class, 'types'))][3]"
    CQF_QUESTIONNAIRE_SUBMIT_BUTTON_XPATH_TEMPLATE = CQF_QUESTIONNAIRE_BUTTONS_XPATH_TEMPLATE + "//button[1]"
    CQF_QUESTIONNAIRE_CANCEL_BUTTON_XPATH_TEMPLATE = CQF_QUESTIONNAIRE_BUTTONS_XPATH_TEMPLATE + "//button[2]"

    CALLING_SCREEN_XPATH = "//calling-screen"
    CALL_COUNTER_XPATH = "//calling-duration"
    CALLING_SCREEN_PARTICIPANT_AVATAR_XPATH_TEMPLATE = "//calling-participant-stream//img[@pl-upn = '%s']"
    CALLING_SCREEN_SPECIFIC_PARTICIPANT_VISIBLE_STREAM_XPATH = "//calling-participant-stream/div[contains(@class,'ts-calling-participant-stream')][.//img[@pl-upn = '%s']]"
    CALLING_SCREEN_NONSPECIFIC_PARTICIPANT_VISIBLE_STREAM_XPATH = "//calling-participant-stream/div[contains(@class,'ts-calling-participant-stream')][.//img[contains(@pl-upn , '%s')]]"
    CALLING_SCREEN_GROUP_CALL_PARTICIPANT_AVATAR_XPATH_TEMPLATE = "//calling-stage//calling-participant-stream//img[@pl-upn = '%s']"
    CALLING_SCREEN_PARTICIPANT_AVATAR_XPATH_ENTRY = "//calling-participant-stream//img[@pl-upn]"
    CALLING_SCREEN_GROUP_CALL_PARTICIPANT_AVATAR_XPATH_ENTRY = "//calling-stage//calling-participant-stream//img[@pl-upn]"
    CALLING_SCREEN_PARTICIPANT_SHARING_SCREEN_AVATAR_XPATH_TEMPLATE = "//div[contains(@class, 'PRESENTATION')]//calling-stage//calling-participant-stream//img[@pl-upn = '%s']"
    CALLING_SCREEN_SHARE_DESKTOP_PANEL_XPATH = "//div[contains(@class, 'ts-calling-screensharing-panel')]"
    CALLING_SCREEN_SHARE_DESKTOP_PANEL_SCREEN_XPATH = "//div[contains(@class, 'ts-calling-screensharing-panel')]//div[contains(@class, 'screen')]"
    CALLING_SCREEN_HANGUP_BUTTON_XPATH = "//button[contains(@class, 'ts-hangup')]"
    CALLING_SCREEN_SHARE_DESKTOP_BUTTON_XPATH = "//button[contains(@class, 'share-desktop')]"
    CALLING_SCREEN_TOGGLE_MIC_BUTTON_XPATH = "//button[contains(@ng-click, 'toggleMuteAudio')]"
    CALLING_SCREEN_PARTICIPANT_STREAM_XPATH = "//calling-participant-stream"
    #CALLING_SCREEN_TOGGLE_VIDEO_BUTTON_XPATH = "//button[contains(@title, 'video')]"
    CALLING_SCREEN_TOGGLE_VIDEO_BUTTON_XPATH = "//button[@calling-screen-focus='toggle-video-button']"
    CALLING_SCREEN_TURN_OFF_VIDEO_BUTTON_XPATH = CALLING_SCREEN_TOGGLE_VIDEO_BUTTON_XPATH + "[@common-tooltip='Stop my video' or @title = 'Stop my video']"
    CALLING_SCREEN_TURN_ON_VIDEO_BUTTON_XPATH = CALLING_SCREEN_TOGGLE_VIDEO_BUTTON_XPATH + "[@common-tooltip='Start my video' or @title = 'Start my video']"

    CALLING_SCREEN_MEETUP_TITLE_XPATH = "//editable-text//div[contains(@class, 'inputContainer')]/input[@readonly='readonly']"
    CALLING_SCREEN_MEETUP_TITLE_INPUT_XPATH = "//editable-text//input[not(@readonly='readonly')]"
    CALLING_SCREEN_MEETUP_TITLE_INPUT_SAVED_XPATH = "//editable-text[@title-text='%s']//input[@readonly='readonly']"
    CALLING_SCREEN_MEETUP_TITLE_SAVE_XPATH = "//span[@title = 'Save title']"

    CALLING_SCREEN_DURATION_TIMER = "//calling-duration/span[contains(@class,'calling-duration')][contains(@class,'timer')]"
    CALLING_MYSELF_VIDEO_XPATH_EXPANDED = "//calling-myself-video/div[contains(@class,'calling-myself-video')][contains(@class,'expanded')]/canvas"
    CALLING_MYSELF_VIDEO_XPATH_COLLAPSED = "//calling-myself-video/div[contains(@class,'calling-myself-video')][not(contains(@class,'expanded'))]/canvas"

    VIDEO_TOGGLE_XPATH = "//button[@calling-screen-focus='toggle-video-button']"
    VIDEO_TURN_ON_XPATH = "//button[@calling-screen-focus='toggle-video-button'][@aria-label='Your video is off. Start video']"
    VIDEO_TURN_OFF_XPATH = "//button[@calling-screen-focus='toggle-video-button'][@aria-label='Your video is on. Stop video']"

    # When experimental setting use pepper renderer is enabled then on calling screen is not present canvas elemnt containing video stream but embed is there instead so this will works in both cases in the same way as previously without need to change anything else
    CALLING_MYSELF_VIDEO_XPATH = "//calling-myself-video//div[contains(@class,'video-stream-container')][//embed or //canvas]"

    CALLING_MYSELF_AVATAR_XPATH = "//calling-myself-video/div[contains(@class, 'audioOnly')]"
    CALLING_SCREEN_TOGGLE_FULLSCREEN = "//calling-header//button[@ngsf-toggle-fullscreen]"
    CALLING_SCREEN_TOGGLE_CHAT_ENABLED_XPATH = "//button[not(@disabled) and contains(@class, 'toggle-chat')]"
    CALLING_SCREEN_TOGGLE_CHAT_ENABLED_NOT_ACTIVE_XPATH = "//button[not(@disabled) and contains(@class, 'toggle-chat') and not(contains(@class, 'active'))]"
    CALLING_SCREEN_TOGGLE_CHAT_ENABLED_ACTIVE_XPATH = "//button[not(@disabled) and contains(@class, 'toggle-chat') and contains(@class, 'active')]"
    CALLING_SCREEN_ADD_PARTICIPANT_BUTTON_XPATH = "//button[not(@disabled) and contains(@class, 'toggle-roster') and not(contains(@class, 'active'))]"
    CALLING_SCREEN_DEVICE_SETTINGS_BUTTON_XPATH = "//calling-header//button[contains(@class, 'toggle-device-settings')]"
    CALLING_SCREEN_IN_CHAT_PANE_XPATH = "//context-message-pane"
    CALLING_SCREEN_MESSAGE_EDITOR_XPATH = "//div[@data-tid = 'messageEditor']"
    CALLING_SCREEN_MESSAGES_PANE_TEXT_XPATH_TEMPLATE = "//div[@data-tid = 'messageBodyContent']//div[contains(., '%s')]"

    TEAM_CHANNEL_NEW_MESSAGE_INPUT_XPATH = "//div[@data-tid='messageEditor']//div[contains(@class,'cke_editor')]//div[@data-tid='ckeditor-newConversation']"
    TEAM_CHANNEL_NEW_MESSAGE_INPUT_FOCUSED_XPATH = "//div[@data-tid='messageEditor']//div[contains(@class,'cke_editor')][contains(@class,'cke_focus')]//div[@data-tid='ckeditor-newConversation']"

    CHAT_NEW_MESSAGE_INPUT = "//div[@data-tid='ckeditor-newP2PMessage']"
    CHAT_NEW_MESSAGE_INPUT_COMMON = "//div[@data-tid='messageEditor']" + CHAT_NEW_MESSAGE_INPUT
    CHAT_NEW_MESSAGE_INPUT_FOCUSED = "//div[@data-tid='messageEditor']//div[contains(@class,'cke_focus')]" + CHAT_NEW_MESSAGE_INPUT
    CHAT_NEW_MESSAGE_INPUT_NOT_FOCUSED = "//div[@data-tid='messageEditor']//div[not(contains(@class,'cke_focus'))]" + CHAT_NEW_MESSAGE_INPUT
    CALLING_SCREEN_NEW_MESSAGE_INPUT = "//calling-chat[contains(@class,'active') and not(contains(@class,'ng-hide'))]//div[@data-tid='messageEditor']" + CHAT_NEW_MESSAGE_INPUT
    CALLING_SCREEN_NEW_MESSAGE_INPUT_FOCUSED = "//calling-chat[contains(@class,'active') and not(contains(@class,'ng-hide'))]//div[@data-tid='messageEditor'][.//div[contains(@class,'cke_focus')]]" + CHAT_NEW_MESSAGE_INPUT

    CALLING_SCREEN_ADD_PARTICIPANT_PANE_XPATH = "//calling-roster"
    CALLING_SCREEN_INVITE_INPUT_XPATH = "//calling-roster-search//input[@id = 'searchInput']"
    CALLING_SCREEN_CURRENTLY_IN_MEETING_LABEL_XPATH = "//calling-roster-section[@data-tid = 'participantsInCall']//div[contains(@class, 'roster_list_title')]"
    CALLING_SCREEN_FROM_THREAD_LABEL_XPATH = "//calling-roster-section[@data-tid = 'participantsFromThread']//div[contains(@class, 'roster_list_title')]"
    CALLING_SCREEN_ROSTER_LIST_LABEL_XPATH = "//calling-roster-section[@data-tid = 'participantsFromTeam']//div[contains(@class, 'roster_list_title')]"
    CALLING_SCREEN_FROM_MEETING_LABEL_XPATH = "//calling-roster-section[@data-tid = 'participantsFromMeeting']//div[contains(@class, 'roster_list_title')]"
    CALLING_SCREEN_SEARCH_RESULT_USER_XPATH_TEMPLATE = "//calling-roster-search-results//li[contains(@class,'item')][.//img[@pl-upn='%s']]"
    CALLING_SCREEN_USER_CONNECTING_XPATH_TEMPLATE = "//calling-roster-section//div[contains(@class, 'roster_list_title')]/..//img[@pl-upn = '%s']"
    CHANNEL_CONVERSATION_MEETUP_ENDED_XPATH_PARTICIPANT_LIST = "//calling-thread-body[.//div[contains(text(), '%s')]]//calling-live-roster"
    CALLING_SCREEN_ADD_PARTICIPANT_INVITE_OTHERS_FROM_CONV_ALL_ENTRIES = "//calling-roster-section[@data-tid='participantsFromThread']//ul[@class='items']/li"
    IMAGE_CONTAINS_EMAIL_ADDRESS = "[.//img[@pl-upn = '%s']]"

    CHANNEL_REPLY_BTN_FOR_CALL_ID_TEMPLATE = "//thread[." + CHANNEL_CONVERSATION_MEETUP_ENDED_XPATH_DTID_TEMPLATE + "]//button[@data-tid = 'replyMessageButtonShort']"
    CHANNEL_REPLY_MESSAGE_INPUT_XPATH_TEMPLATE = "//thread[." + CHANNEL_CONVERSATION_MEETUP_ENDED_XPATH_DTID_TEMPLATE + "]//div[@data-tid = 'ckeditor-replyConversation']"
    CHANNEL_REPLY_CHAIN_MESSAGE_CONTENT_CALL_ID_XPATH_TEMPLATE = "//thread[." + CHANNEL_CONVERSATION_MEETUP_ENDED_XPATH_DTID_TEMPLATE + "]//div[@data-tid = 'messageBodyContent']//div[. = '%s']"
    CHANNEL_REPLY_CHAIN_CALL_START_BUTTON_XPATH_TEMPLATE = "//thread[." + CHANNEL_CONVERSATION_MEETUP_ENDED_XPATH_DTID_TEMPLATE + "]//button[contains(@class, 'icons-call')]"
    CHANNEL_REPLY_CHAIN_JOIN_BUTTON_BY_CALL_ID_TEMPLATE = "//button[@data-tid = 'join-btn-%s']"

    CHANNEL_LIST_XPATH = "//div[@data-tid = 'team-channel-list']"
    CHANNEL_LIST_TEAM_NAMED_XPATH = CHANNEL_LIST_XPATH + "[.//span[contains(text(),'%s')]]"
    TEAM_CHANNEL_NAMED_XPATH = CHANNEL_LIST_TEAM_NAMED_XPATH + "/..//li[contains(@id,'@thread.skype')][.//span[contains(text(),'%s')]]"
    CHAT_LIST_XPATH = "//chat-list"
    APP_BAR_CHAT_BUTTON_XPATH = "//app-bar//button[@data-tid = 'app-bar-2']"
    APP_BAR_TEAMS_BUTTON_XPATH = "//app-bar//button[@data-tid = 'app-bar-4']"

    CALLING_HEADER_MENU_XPATH = "//calling-header//button[contains(@title, 'Toggle sidebar')]"
    LEFT_RAIL_USER_INFO_XPATH = "//user-information/div[contains(@class, 'app-user-information')]"
    CALL_HANGING_UP_XPATH = "//div[contains(@class, 'call-state-layer')]"

    FIND_ELEMENT_BY_XPATH_JS_TEMPLATE = "var %s = document.evaluate(\"%s\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
    SCROLL_DOWN_ELEMENT_JS = "elem.scrollTop = elem.scrollHeight;"
    SCROLL_UP_ELEMENT_JS = "elem.scrollTop = 0;"
    CHECK_IF_IN_VIEWPORT_JS = """
                    function isInViewport(element) {
                      var rect = element.getBoundingClientRect();
                      var html = document.documentElement;
                      return (
                        rect.top >= 0 &&
                        rect.left >= 0 &&
                        rect.bottom <= (window.innerHeight || html.clientHeight) &&
                        rect.right <= (window.innerWidth || html.clientWidth)
                      );
                    }
    """
    # SCROLL_TO_ELEMENT_JS_TEMPLATE = CHECK_IF_IN_VIEWPORT_JS + "myElem = %s; if (myElem) { if (!isInViewport(myElem)) { myElem.scrollIntoView();}; };"
    SCROLL_TO_ELEMENT_JS_TEMPLATE = "myElem = %s; if (myElem) { myElem.scrollIntoView();};"
    LOGOUT_EXE_ANGULAR_JS = "angular.element(document.body).injector().get('authenticationService').logOut();"
    CALL_HANGUP_EXE_ANGULAR_JS = "angular.element(document.body).injector().get('callingService').callRegistry.calls[0].stop();"
    CALL_STOP_VIDEO_EXE_ANGULAR_JS = "angular.element(document.body).injector().get('callingService').callRegistry.calls[0].stopVideo();"
    CALL_START_VIDEO_EXE_ANGULAR_JS = "angular.element(document.body).injector().get('callingService').callRegistry.calls[0].startVideo();"
    GET_CALL_ID_ANGULAR_JS = "return angular.element(document.body).injector().get('callingService').callRegistry.calls[0].callId"
    TOGGLE_CALLING_HEADER_MENU_JS = "document.evaluate(\"%s\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();"
    TYPE_TEXT_TO_XPATH_ELEMENT_JS_TEMPLATE = "document.evaluate(\"%s\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.value = '%s';"
    GET_ALL_LOG_EVENTS_JS = "var logs = angular.element(document.body).injector().get('diagnosticsService').getAllEvents(); var result = ''; _.orderBy(logs, ['timeStamp'], ['desc']).forEach((value) => { var date = moment(value.timeStamp).toISOString(); result += angular.element(document.body).injector().get('utilityService').format('{0} {1}\\t{2}\\r\\n', date, value.levelName.substring(0, 3), value.message); }); return result;"

    TAB_ORDERS = {
        "calling_screen": [
            CALLING_SCREEN_TOGGLE_FULLSCREEN,
            CALLING_SCREEN_TOGGLE_CHAT_ENABLED_XPATH,
            CALLING_SCREEN_ADD_PARTICIPANT_BUTTON_XPATH,
            CALLING_SCREEN_DEVICE_SETTINGS_BUTTON_XPATH,
            CALLING_SCREEN_INVITE_INPUT_XPATH,
            CALLING_SCREEN_CURRENTLY_IN_MEETING_LABEL_XPATH,
            CALLING_SCREEN_FROM_THREAD_LABEL_XPATH,
            CALLING_SCREEN_ROSTER_LIST_LABEL_XPATH,
            CALLING_SCREEN_FROM_MEETING_LABEL_XPATH,
            CALLING_SCREEN_TOGGLE_VIDEO_BUTTON_XPATH,
            CALLING_SCREEN_TOGGLE_MIC_BUTTON_XPATH,
            CALLING_SCREEN_SHARE_DESKTOP_BUTTON_XPATH,
            CALLING_SCREEN_HANGUP_BUTTON_XPATH
        ]
    }

    ####################
    # Element data end #
    ####################

    def __init__(self, env_id, build_name, build_path):
        # logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO, stream=sys.stdout)
        logging.basicConfig(format='%(levelname)s || %(asctime)s || %(funcName)s || %(message)s', datefmt='%I:%M:%S', level=logging.INFO, stream=sys.stdout)

        self.is_local = False
        self.run_mode = None
        self.test_config = None
        self.build_name = build_name
        self.build_path = build_path
        self.env_id = env_id
        self.experimental_setting = None
        self.spaces_driver = None
        self.webdriver_bin = None
        self.show_console_logs = True
        self.sys = PlatformLib(env_id, build_name, build_path)
        self.accessibility = None
        self.video_recorder = None
        self.recording_in_progress = False
        try:
            if Castro:
                os.environ['CASTRO_DATA_DIR'] = "."
                self.video_recorder = Castro()
        except NameError:
            pass

    @staticmethod
    def start_debugger():
        pdb.set_trace()

    @staticmethod
    def wait_for_seconds(seconds):
        logging.info("Static Pause for : {0} seconds".format(seconds))
        time.sleep(seconds)

    def prepare_test_env(self, config, user_accounts=None, test_channel_data=None, uninstall_app_before_preparation=UNINSTALL_APP_BEFORE_SETUP):
        logging.info("Started prepearing test environment...")

        self.test_config = TestConfigLoader(config)

        self.run_mode = self.test_config.get_run_mode()
        logging.info("Current run mode is: {}".format(self.run_mode))

        self.webdriver_bin = self.sys.lib.get_driver_bin(self.run_mode)

        if self.test_config.is_local_run():
            self.is_local = True

        if self.is_teams_desktop_app_run():

            if self.test_config.enable_slimcore():
                self.ENABLE_SLIMCORE = True
            if self.is_local:
                self.sys.lib.kill_chromedriver()
            else:
                if uninstall_app_before_preparation:
                    self.sys.lib.uninstall_skypespaces()
                self.sys.lib.kill_chromedriver()
                self.sys.lib.install_skypespaces()

        self.initialize(test_channel_data)
        self.load_test_accounts(user_accounts)

    def is_teams_desktop_app_run(self):
        logging.info("is_desktop_run")
        if self.run_mode == "electron":
            return True
        elif self.run_mode == "chrome" or "edge":
            return False
        else:
            logging.info("Unknown run_mode = '{0}'".format(self.run_mode))
            return False

    def initialize(self, test_channel_data=None):
        """
        Sets up test environment on system - launches chromedriver, launches SkypeSpaces app and hooks to it
        :return:
        """
        logging.info("Microsoft Teams::initialize environment")
        self.start_video_recording()

        if test_channel_data and len(test_channel_data) == 3:
            self.test_config.load_test_data_from_config(team=test_channel_data[0], channel=test_channel_data[1], channel_id=test_channel_data[2])
        else:
            self.test_config.load_test_data_from_config()

        if self.is_teams_desktop_app_run():
            logging.info("Running desktop app....")

            if not os.path.isfile(self.sys.lib.skypespaces_bin):
                logging.error("Cannot find SkypeSpaces binary: {}".format(self.sys.lib.skypespaces_bin))
                raise Exception("Cannot find SkypeSpaces binary: {}".format(self.sys.lib.skypespaces_bin))
            # Make sure app is not running before we try to attach to it
            logging.info("Terminating the app in case if it is currently running...")
            self.sys.lib.terminate_app()
        else:
            # TODO: Browser webdriver init (if needed)
            self.wait_for_seconds(1)
        # Web Driver Initialization
        self.spaces_driver = SpacesWebDriver(skypespaces_bin=self.sys.lib.skypespaces_bin, driver_bin=self.sys.lib.get_driver_bin(self.run_mode), run_mode=self.run_mode, system_lib=self.sys, enable_slimcore=self.ENABLE_SLIMCORE)
        self.wait_for_seconds(30)
        self.accessibility = Accessibility(self.spaces_driver, self.sys)
        self.focus_spaces_app()

        if self.is_teams_desktop_app_run():
            self.open_teams_app()
        else:
            if self.run_mode is "edge" or "chrome":
                self.enable_calling_in_browser()
        self.open_teams_web_app()
        return

    def is_msteams_app_opened(self):
        logging.info("is_msteams_app_opened")
        logging.info("Waiting for app to start..")
        self.spaces_driver.wait_for_element(locator=self.ELECTRON_APP_HANDLER_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT, fail_on_not_found=False)
        if self.spaces_driver.is_element_present(locator=self.ELECTRON_APP_HANDLER_XPATH, locator_type=self.XPATH):
            logging.info("SUCCESS - MS Teams App Handler XPath found")
            return True
        else:
            logging.info("WARNING - MS Teams App Handler XPath not found \n Waiting for 20s and re-attempting to focus MS Teams app")
            self.wait_for_seconds(20)
            self.focus_spaces_app()
            logging.info("App window focused checking if MSTeams App handler Xpath is present timeout = 20s")
            if self.spaces_driver.is_element_present(locator=self.ELECTRON_APP_HANDLER_XPATH, locator_type=self.XPATH, timeout=20):
                return True
            else:
                logging.info("ERROR - MS Teams app handler xpath not found !!!")
                return False

    def enable_experimental_setting_in_url(self, setting):
        if not setting:
            return
        logging.info("Enabling experimental setting '%s'" % setting)
        if "?" in self.test_config.base_url:
            self.test_config.base_url = self.test_config.base_url.replace("?", str("?setting=%s:true&") % setting, 1)
        elif "#" in self.test_config.base_url:
            self.test_config.base_url = self.test_config.base_url.replace("#", str("?setting=%s:true#") % setting, 1)

    def open_teams_app(self):
        logging.info("open_teams_app")
        try:
            logging.info("Obtain opened URL")
            loaded_url = self.spaces_driver.driver.current_url
        except Exception, e:
            logging.info("Exception {0}".format(e))

        logging.info("If block reached")
        if self.MSFT_LOGIN_PAGE in loaded_url or self.test_config.base_url in loaded_url:
            logging.info("Web container initialized successfully")
            self.spaces_driver.take_screen_shot("used_web_container")
            return True
        else:
            logging.info("Seems web container not opened correctly.")
            logging.info("Url loaded: {0}".format(self.spaces_driver.driver.current_url))
            return False

    def enable_calling_in_browser(self):
        logging.info("enable_calling_in_browser")
        if self.run_mode == "edge":
            logging.info("Enabling calling in the Edge browser")
            self.enable_experimental_setting_in_url("callingEnabledEdge")
        if self.run_mode == "chrome":
            logging.info("Enabling calling in the Edge browser")
            # todo: enable calling in chrome experimental settings enable
            # self.enable_experimental_setting_in_url("nameOfSettingForChrome")

    def open_teams_web_app(self, enable_calling_in_browser=ENABLE_CALLING_IN_BROWSER, retries=10):
        logging.info("open_teams_web_app(enable_calling_in_browser = '{0}', retries = '{1}')".format(enable_calling_in_browser, retries))

        if not self.is_teams_desktop_app_run() or self.FORCE_WEB_URL_LOAD or (self.CONTAINER_ARG in self.test_config.base_url) or (self.RING_ARG in self.test_config.base_url):

            if enable_calling_in_browser:
                self.enable_calling_in_browser()
            else:
                logging.info("Enabling calling in browser is disabled via PARAMETER 'enable_calling_in_browser' = '{0}'".format(enable_calling_in_browser))

            for attempt in range(0, retries):
                logging.info("Attempt #{0} of {2}: \n Navigating to MSTeams web_app URL: {1} ".format(attempt, self.test_config.base_url, retries))
                try:
                    self.spaces_driver.driver.get(self.test_config.base_url)
                    self.spaces_driver.wait_for_page_to_load()
                    loaded_url = self.spaces_driver.driver.current_url
                except Exception, e:
                    logging.info("Exception {0}".format(e))

                if self.MSFT_LOGIN_PAGE in loaded_url or self.test_config.base_url in loaded_url:
                    logging.info("Teams web app Loaded and matching passed against known URLs")
                    self.wait_for_seconds(1)
                    self.spaces_driver.take_screen_shot("opened_teams_web_app")
                    return
                else:
                    logging.info("ERROR while loading TEAMS web app [wasn't loaded yet tries {0} from {1} or matching against known URLs was unsuccessful]".format(attempt, retries))
                    logging.info("\n Condition not met 'self.MSFT_LOGIN_PAGE in loaded_url or self.test_config.base_url in loaded_url' \n")
                    logging.info("self.MSFT_LOGIN_PAGE = {0}".format(self.MSFT_LOGIN_PAGE))
                    logging.info("self.test_config.base_url = {0}".format(self.test_config.base_url))
                    logging.info("loaded_url = {0} \n WARNING !!! ".format(self.spaces_driver.driver.current_url))
                    self.wait_for_seconds(1)
                    continue

            raise Exception("Could not navigate to web container {0}".format(self.test_config.base_url))

    def get_test_account(self, index):
        logging.info("Getting test account #" + str(index))
        return self.test_config.test_accounts [index]

    def get_test_accounts(self):
        return self.test_config.test_accounts

    def get_test_channel_data(self):
        return [self.test_config.test_team, self.test_config.test_channel, self.test_config.test_channel_thread_id]

    def login_viliams(self, user_account_tuple, retries=6):
        logging.info("login_viliams")

        username = user_account_tuple ['username']
        password = user_account_tuple ['password']
        logging.info("Starting login in process for User : {0} with password : {1}".format(username, password))
        self.focus_spaces_app(retries=retries)

        counter = 0
        while not self.spaces_driver.wait_for_page_to_load() and counter <= retries:
            logging.info("Attempt number : '{0}'".format(counter))
            counter += 1
            logging.info("Page not loaded yet waiting for 10 seconds")
            self.wait_for_seconds(10)
        logging.info("Page Loaded document.readyState == Complete")

        another_account_common_presence = self.spaces_driver.is_element_present(locator=self.USE_ANOTHER_ACCOUNT_ELEMENTS_LIST, locator_type=self.XPATH, timeout=0)
        another_account_id_is_present = self.spaces_driver.is_element_present(locator=self.SPACES_LOGIN_USE_ANOTHER_ACCOUNT_ID, locator_type=self.ID, timeout=0)
        another_account_link_id_is_present = self.spaces_driver.is_element_present(locator=self.SPACES_LOGIN_USE_ANOTHER_ACCOUNT_LINK_ID, locator_type=self.ID, timeout=0)

        if another_account_common_presence:
            logging.info("Another account screen was detected")
            logging.info("another_account_common_presence is True =?= {0}".format(another_account_common_presence))
            if another_account_id_is_present:
                logging.info("another_account_id_is_present is True =?= {0}".format(another_account_id_is_present))
                element = self.spaces_driver.wait_for_element(locator=self.SPACES_LOGIN_USE_ANOTHER_ACCOUNT_ID, locator_type=self.ID, timeout=self.LOADING_TIMEOUT)
                element.click()
            elif another_account_link_id_is_present:
                logging.info("another_account_link_id_is_present is True =?= {0}".format(another_account_link_id_is_present))
                element = self.spaces_driver.wait_for_element(locator=self.SPACES_LOGIN_USE_ANOTHER_ACCOUNT_LINK_ID, locator_type=self.ID, timeout=self.LOADING_TIMEOUT)
                element.click()
            logging.info("Another account screen was proceeded successfully")

        username_input = self.spaces_driver.wait_for_element(locator=self.SPACES_LOGIN_USERNAME_INPUT, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        username_input.send_keys(username)
        username_input.send_keys(self.spaces_driver.keys.TAB)

        password_input = self.spaces_driver.wait_for_element(locator=self.SPACES_LOGIN_PASSWORD_INPUT, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        logging.info("Going to Fill in Password : '{0}'".format(password))
        password_input.send_keys(password)
        submit = self.spaces_driver.wait_for_element(locator=self.SPACES_LOGIN_SUBMIT_BUTTON_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        submit.click()

    def login(self, user_account):
        logging.info("login")

        self.logout_if_logged_in()

        self.focus_spaces_app()
        self.spaces_driver.wait_for_page_to_load()
        logging.info("Logging in user {0}".format(str(user_account)))
        self.spaces_driver.take_screen_shot("going_to_login")
        another_account_elem_id = None
        need_to_use_another_account = False

        if self.spaces_driver.is_element_present(self.SPACES_LOGIN_USE_ANOTHER_ACCOUNT_ID, self.ID, 0):
            another_account_elem_id = self.SPACES_LOGIN_USE_ANOTHER_ACCOUNT_ID
            need_to_use_another_account = True

        elif self.spaces_driver.is_element_present(self.SPACES_LOGIN_USE_ANOTHER_ACCOUNT_LINK_ID, self.ID, 0):
            another_account_elem_id = self.SPACES_LOGIN_USE_ANOTHER_ACCOUNT_LINK_ID
            need_to_use_another_account = True

        if need_to_use_another_account:
            logging.info("Clicking at 'Use another account' link on login page.")
            use_another_account = self.spaces_driver.driver.find_element_by_id(another_account_elem_id)
            use_another_account.click()

        username = self.spaces_driver.wait_for_element(locator=self.SPACES_LOGIN_USERNAME_INPUT, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        username.send_keys(user_account ['username'])
        username.send_keys(self.spaces_driver.keys.TAB)


        self.login_page_redirection_detection_and_handling()
        #self.un_focus_spaces_app()
        #self.spaces_driver.take_screen_shot("logging_in")
        #self.focus_spaces_app()

        if self.spaces_driver.is_element_present(self.SPACES_LOGIN_PASSWORD_INPUT, self.XPATH, 5):
            logging.info("User is non-corporate account")
            self.spaces_driver.take_screen_shot("non-corp_login")
            self.spaces_driver.wait_for_element(self.SPACES_LOGIN_PASSWORD_INPUT, self.XPATH)
            password = self.spaces_driver.driver.find_element_by_id(self.SPACES_LOGIN_PASSWORD_ID)
            password.send_keys(user_account ['password'])
            submit = self.spaces_driver.driver.find_element_by_id(self.SPACES_LOGIN_SUBMIT_ID)
            self.spaces_driver.take_screen_shot("going_click_at_login")
            submit.click()
            # self.spaces_driver.click_js(submit)
            self.un_focus_spaces_app()
            self.wait_for_seconds(30)
            self.spaces_driver.wait_for_page_to_load()
            logging.info("User '" + user_account ['username'] + "' is being logged in..")
            return

        elif self.spaces_driver.is_element_present(locator=self.MSFT_LOGIN_PASSWORD_ID, locator_type=self.ID, timeout=5) or self.spaces_driver.is_element_present(locator=self.MSFT_LOG_IN_WITH_USERNAME_AND_PASSWORD_LINK_XPATH, locator_type=self.XPATH, timeout=5):
            logging.info("User is corporate account")
            self.spaces_driver.take_screen_shot("corp_login")
            self.login_msftcorp(user_account ['password'])
            return

        raise Exception("ERROR - something went wrong while logging in.....")

    def is_login_page_redirecting(self):
        logging.info("is_login_page_redirecting")
        if self.spaces_driver.is_element_visible(locator=self.TEAMS_LOGIN_REDIRECTING_IS_VISIBLE, locator_type=self.XPATH, timeout=1):
            logging.info("Redirecting detected @!!!")
            return True
        else:
            logging.info("Redirecting wasn't to be visible on page")
            return False

    def login_page_redirection_detection_and_handling(self):
        logging.info("login_page_redirection_detection_and_handling")
        for i in range(1, 30):
            self.wait_for_seconds(0.5)
            logging.info("Detection attempt i = '{0}'".format(i))
            if self.is_login_page_redirecting():
                logging.info("Redirecting Detected now handling wait till its disappearance")
                while self.is_login_page_redirecting():
                    logging.info("waiting for Redirecting disappearance")
                    self.wait_for_seconds(1)
                logging.info("waiting finished redirecting is not longer detected")
                return
        logging.info("Exiting 'login_page_redirection_detection_and_handling'")

    def login_msftcorp(self, msft_password):
        logging.info("login_msftcorp")
        self.spaces_driver.wait_for_element(self.MSFT_LOGIN_PASSWORD_ID, self.ID)

        if self.spaces_driver.is_element_present(self.MSFT_LOG_IN_WITH_USERNAME_AND_PASSWORD_LINK_XPATH, self.XPATH, 10):
            login_username_pass = self.spaces_driver.wait_for_element(locator=self.MSFT_LOG_IN_WITH_USERNAME_AND_PASSWORD_LINK_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
            login_username_pass.click()
            self.wait_for_seconds(5)

        password = self.spaces_driver.driver.find_element_by_id(self.MSFT_LOGIN_PASSWORD_ID)
        submit_button = self.spaces_driver.driver.find_element_by_id(self.MSFT_LOGIN_BUTTON_ID)
        password.send_keys(msft_password)
        submit_button.click()
        self.un_focus_spaces_app()
        self.wait_for_seconds(30)
        logging.info("User is being logged in..")

    def is_channel_loading_spinner_visible(self):
        logging.info("is_channel_loading_spinner_visible")
        self.spaces_driver.wait_for_element(locator=self.SPACES_USER_INFO_ELEM_XPATH, locator_type=self.XPATH, timeout=90, fail_on_not_found=False)
        if self.spaces_driver.is_element_visible(locator=self.CHANNEL_LOADING_SPINNER_DISPAYED, locator_type=self.XPATH, timeout=0):
            logging.info("TRUE - is_channel_loading_spinner_visible --> returns True")
            return True
        else:
            logging.info("FALSE - is_channel_loading_spinner_visible --> returns False")
            return False

    def loading_spinner_detection_and_wait_to_dissappear(self):
        logging.info("loading_spinner_detection_and_wait_to_dissappear")
        if self.is_channel_loading_spinner_visible():
            logging.info("Detected Loading Spinner")
            self.spaces_driver.take_screen_shot("Channel_Loading_Detected")
            self.spaces_driver.wait_for_not_visible(self.CHANNEL_LOADING_SPINNER_DISPAYED, self.XPATH, 120)
        self.spaces_driver.wait_for_element(locator=self.CHANNEL_LOADING_SPINNER_NOT_DISPAYED, locator_type=self.XPATH, timeout=15, fail_on_not_found=False)
        logging.info("Loading Not Present anymore")
        return

    def is_refresh_button_present(self):
        logging.info("is_refresh_button_present")
        if self.spaces_driver.is_element_present(locator=self.REFRESH_BTN_XPATH, locator_type=self.XPATH, timeout=5):
            logging.info("TRUE - is_refresh_button_present --> returns True")
            return True
        else:
            logging.info("FALSE - is_refresh_button_present --> returns False")
            return False

    def refresh_button_detection_and_close(self):
        logging.info("refresh_button_detection")
        if self.is_refresh_button_present():
            logging.info("Refresh button detected")
            self.spaces_driver.take_screen_shot("refresh_content_button")
            btn = self.spaces_driver.wait_for_element(locator=self.REFRESH_BTN_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
            btn.click()
            self.spaces_driver.wait_for_page_to_load()
            self.wait_for_seconds(10)

    def lets_go_window_detection_and_close(self):
        logging.info("lets_go_window_detection")
        if self.is_lets_go_window_present():
            logging.info("lets go button is present")
            button = self.spaces_driver.wait_for_element(locator=self.WELCOME_TO_MICROSOFT_TEAMS_LETS_GO_BUTTON, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
            self.spaces_driver.take_screen_shot("LETS_GO_BTN_BEFORE_CLICK")
            button.click()
            self.spaces_driver.take_screen_shot("LETS_GO_BTN_AFTER_CLICK")
            self.spaces_driver.wait_for_not_visible(locator=self.WELCOME_TO_MICROSOFT_TEAMS_LETS_GO_BUTTON, locator_type=self.XPATH, timeout=15)

    def is_lets_go_window_present(self):
        logging.info("is_lets_go_window_present")
        if self.spaces_driver.is_element_present(locator=self.WELCOME_TO_MICROSOFT_TEAMS_LETS_GO_BUTTON, locator_type=self.XPATH, timeout=5):
            logging.info("TRUE - is_lets_go_window_present --> returns True")
            return True
        else:
            logging.info("FALSE - is_lets_go_window_present --> returns False")
            return False

    def wait_for_channel_to_be_ready(self):
        logging.info("wait_for_channel_to_be_ready")
        if self.is_channel_loading_spinner_visible() or self.is_refresh_button_present() or self.is_lets_go_window_present():
            logging.info("Detected Loading Spinner or Refresh Button or Welcome Window")
            self.lets_go_window_detection_and_close()
            self.refresh_button_detection_and_close()
            self.loading_spinner_detection_and_wait_to_dissappear()
            return
        else:
            if not self.spaces_driver.is_element_present(locator=self.CHANNEL_LOADING_SPINNER_NOT_DISPAYED, locator_type=self.XPATH, timeout=10):
                logging.info("Loading not detected at all")
                return
            else:
                self.spaces_driver.take_screen_shot("WARNING_New_channel_layout_is_used")
                logging.info("Warning - Probably new channel layout is being used")
                return

    def is_user_logged_in(self):
        logging.info("is_user_logged_in")
        """
        Checks if user is logged in to the SkypeSpaces app
        :return:
        """
        logging.info("Checking whether user is already logged in..")
        self.spaces_driver.take_screen_shot("login_check")
        for i in range(1, 30):
            self.wait_for_seconds(1)
            if self.spaces_driver.is_element_present(locator=self.WELCOME_TO_MICROSOFT_TEAMS_LETS_GO_BUTTON, locator_type=self.XPATH, timeout=0.33):
                logging.info("Lets go teams welcome window detected means user is logged in")
                self.spaces_driver.take_screen_shot("teams_welcome_window_is_logged_in")
                return True
            elif self.spaces_driver.is_element_present(locator=self.SPACES_USER_INFO_ELEM_XPATH, locator_type=self.XPATH, timeout=0.33):
                logging.info("User is logged in.")
                self.spaces_driver.take_screen_shot("is_logged_in")
                return True
            elif self.spaces_driver.is_element_present(locator=self.SPACES_LOGIN_USERNAME_INPUT, locator_type=self.XPATH, timeout=0.33):
                logging.info("User is NOT logged in we detected presence of '{0}'".format(self.SPACES_LOGIN_USERNAME_INPUT))
                self.spaces_driver.take_screen_shot("not_logged_in")
                return False
            elif self.spaces_driver.is_element_present(locator=XPathBuilder.xpath_body_contains_text("Sign in to your Microsoft corporate account"), locator_type=self.XPATH, timeout=0.33):
                logging.info("User is NOT logged we detected : '{0}'".format(XPathBuilder.xpath_body_contains_text("Sign in to your Microsoft corporate account")))
                self.spaces_driver.take_screen_shot("not_logged_in_corporate_account")
                return False
            else:
                logging.error("Error detecting whether user is logged in or not.")
                self.spaces_driver.dump_html_for_actual_page("user_not_logged_in.html")
                return Exception("Error detecting whether user is logged in or not.")

    def logout_if_logged_in(self):
        logging.info("logout_if_logged_in")
        self.focus_spaces_app()
        if self.is_user_logged_in():
            logging.info("Logout is required")
            self.spaces_driver.driver.execute_script(self.LOGOUT_EXE_ANGULAR_JS)
            self.wait_for_seconds(3)
            logging.info("Logout Finished")

    def logout(self):
        logging.info("logout")
        self.logout_if_logged_in()

    def load_test_accounts(self, accounts=None):
        logging.info("load_test_accounts")
        """
        Loads test users credentials from test configuration
        :param accounts: If specified, just fills up test users credentials to test context (when test accounts already loaded on 2nd party agent)
        :return:
        """
        self.test_config.load_test_accounts(accounts)

    def focus_spaces_app(self, retries=50):
        logging.info("focus_spaces_app")
        step = 0
        while not self.is_focused_spaces_app() and step < retries:
            logging.info("attempt {0} - to focus teams app window".format(step))
            step += 1
            self.wait_for_seconds(1)
        if self.is_focused_spaces_app():
            return
        else:
            self.spaces_driver.take_screen_shot("Teams_window_not_focused")
            logging.error("Teams window not focused")
            raise Exception("Teams window not focused")

    def is_focused_spaces_app(self):
        logging.info("is_focused_spaces_app")
        i = 0
        for window_handle in self.spaces_driver.driver.window_handles:
            self.spaces_driver.driver.switch_to.window(window_handle)
            logging.info("switching to window handle '{0}' from possible'{1}'".format(i, len(self.spaces_driver.driver.window_handles)))
            i += 1
            for elem in [self.SPACES_LOGIN_USERNAME_INPUT, self.SPACES_USER_INFO_ELEM_XPATH, self.LOGIN_AREA]:
                logging.info("Trying presence of element '{0}'".format(elem))
                if self.spaces_driver.is_element_present(locator=elem, locator_type=self.XPATH, timeout=0):
                    logging.info("Element detected in Window so Teams app window is focused")
                    return True
        return False

    def un_focus_spaces_app(self):
        logging.info("un_focus_spaces_app")
        i = 0
        for i in range(i, len(self.spaces_driver.driver.window_handles)):
            logging.info("for i = {0} from {1} window handles".format(i, len(self.spaces_driver.driver.window_handles)))
            logging.info("window_handle = {0}".format(str(self.spaces_driver.driver.current_window_handle)))
            if self.spaces_driver.driver.current_window_handle != self.spaces_driver.driver.window_handles[i]:
                logging.info("current handle is not same as window handle so getting unfocused")
                self.spaces_driver.driver.switch_to.window(self.spaces_driver.driver.window_handles[i])
                return
            i += 1
        try:
            self.unfocus_spaces_app()
        except Exception, e:
            logging.error("Couldn't unfocus Teams app window {0}".format(e))
            raise Exception("Couldn't unfocus Teams app window")

    def unfocus_spaces_app(self, wait=0):
        logging.info("unfocus_spaces_app")
        """
        Hack for make Chrome driver to work with electron during 302 redirects
        """
        logging.info("if self.spaces_driver.driver.current_window_handle != self.spaces_driver.driver.window_handles[0]")
        logging.info("if current handle = '{0}' != {1} all window handles[0]".format(str(self.spaces_driver.driver.current_window_handle), str(self.spaces_driver.driver.window_handles[0])))

        if self.spaces_driver.driver.current_window_handle != self.spaces_driver.driver.window_handles[0]:
            self.spaces_driver.driver.switch_to.window(self.spaces_driver.driver.window_handles[0])
            logging.info("Switched to window #0")
        else :
            logging.info("elif len(self.spaces_driver.driver.window_handles) > 1:")
            logging.info("elif {%d} > 1" % len(self.spaces_driver.driver.window_handles))

            if len(self.spaces_driver.driver.window_handles) > 1:
                self.spaces_driver.driver.switch_to.window(self.spaces_driver.driver.window_handles[1])
                logging.info("Switched to window #1")
            else:
                logging.info("Nothing to unfocus. Seems this is browser run.")
            self.wait_for_seconds(wait)
            logging.info("App window unfocused")

    def is_focused_call_notification_window(self):
        logging.info("is_focused_call_notification_window")
        i = 0
        for window_handle in self.spaces_driver.driver.window_handles:
            self.spaces_driver.driver.switch_to.window(window_handle)
            logging.info("switching to window handle '{0}' from possible'{1}'".format(i, len(self.spaces_driver.driver.window_handles)))
            i += 1
            for elem in [self.CALL_NOTIFICATION_WINDOW_IS_NUDGING_MESG_XPATH, self.CALL_NOTIFICATION_WINDOW_IS_CALLING_MESG_XPATH]:
                logging.info("Trying presence of element '{0}'".format(elem))
                if self.spaces_driver.is_element_present(elem, self.XPATH, 0):
                    logging.info("Element detected in Window so Call notification window is focused")
                    return True
        return False

    def focus_call_notification_window(self):
        logging.info("focus_call_notification_window")
        retry = 60
        step = 0
        while not self.is_focused_call_notification_window() and step < retry:
            logging.info("attempt {0} - call notification not found".format(step))
            step += 1
            self.wait_for_seconds(1)
        if self.is_focused_call_notification_window():
            return
        else:
            self.spaces_driver.take_screen_shot("Call_notification_not_shown")
            logging.error("Call notification not shown")
            raise Exception("Call notification not shown")

    def print_notification_source(self):
        logging.info("print_notification_source")
        while True:
            self.focus_call_notification_window()
            print("================================")
            print(self.spaces_driver.driver.page_source.encode('utf-8').strip())

    def wait_for_call_notification_to_be_opened(self, is_meetup=False):
        logging.info("wait_for_call_notification_to_be_opened")
        retry = 60
        step = 0
        while not self.is_focused_call_notification_window() and step < retry:
            logging.info("#%d   - not opened" % step)
            step += 1
            self.wait_for_seconds(1)

        if self.is_focused_call_notification_window():
            logging.info("#%d   - opened" % step)
            self.spaces_driver.take_screen_shot("call_notification_opened")
            return
        else:
            logging.info("#%d   - not opened" % step)
            self.spaces_driver.take_screen_shot("call_notification_not_opened")
            return

    def start_video_recording(self):
        logging.info("start_video_recording")
        if self.video_recorder:
            try:
                self.video_recorder.start()
                self.recording_in_progress = True
                logging.info("Video recording started.")
            except Exception, e:
                logging.info("Could not start screen video recording. VNC server not running... exception was : %s" %e)

    def stop_video_recording(self):
        logging.info("stop_video_recording")
        if self.video_recorder and self.recording_in_progress:
            self.video_recorder.stop()
            self.recording_in_progress = False
            logging.info("Video recording stopped.")



    def show_more_channels(self, fail_on_not_present=False):
        logging.info("show_more_channels")
        try:
            more_button = self.spaces_driver.wait_for_element(handler=self.SHOW_MORE_TEAMS_BUTTON_XPATH, method=self.XPATH, timeout=5, fail_on_not_found=fail_on_not_present)
            more_button.click()
            self.spaces_driver.take_screen_shot("more_channels")
        except TimeoutException:
            if fail_on_not_present:
                logging.info("More channels button not found TimeoutException")
                raise TimeoutException("More channels button not found TimeoutException")
            else:
                logging.info("More channels button not found TimeoutException")

    def navigate_to_channel(self, team_name=None, channel_name=None, channel_thread_id=None, wait_for_load=True, attempts=3):
        logging.info("navigate_to_channel")

        self.wait_for_seconds(15)

        for attempt in range(0, attempts):

            if not team_name:
                team_name = self.test_config.test_team

            if not channel_name:
                channel_name = self.test_config.test_channel

            if not channel_thread_id:
                channel_thread_id = self.test_config.test_channel_thread_id

            channel_url = str(str(self.test_config.base_url) + "channel/{0}/{1}/{2}/conversations?ctx=channel".format(str(team_name), str(channel_name).replace(" ", "%20"), str(channel_thread_id)))
            logging.info("Navigating to: {0}".format(channel_url))
            self.focus_spaces_app()
            self.spaces_driver.driver.get(channel_url)
            logging.info("Navigated to url: {0}".format(self.spaces_driver.driver.current_url))

            if wait_for_load:
                logging.info("wait for page to load")
                self.spaces_driver.wait_for_page_to_load()
                self.wait_for_channel_to_be_ready()

            self.spaces_driver.take_screen_shot("navigating_to_channel")
            channel_xpath = str("//h2[@data-tid = 'messagesHeader-Title' and . = '{0}']".format(str(self.test_config.test_channel)))
            self.spaces_driver.wait_for_element(locator=channel_xpath, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)

            if self.spaces_driver.is_element_present(self.REFRESH_BTN_XPATH, self.XPATH, 5):
                self.spaces_driver.take_screen_shot("refresh_content_button")
                btn = self.spaces_driver.wait_for_element(locator=self.REFRESH_BTN_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
                btn.click()
                self.spaces_driver.wait_for_page_to_load()
                self.spaces_driver.wait_for_element(locator=channel_xpath, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
                self.wait_for_channel_to_be_ready()
            break

    def channel_scroll_up_down(self, scroll_down=True):
        logging.info("channel_scroll_up_down")
        self.wait_for_channel_to_be_ready()
        self.spaces_driver.take_screen_shot("before_scroll")
        scroll_js = "%s %s" % (self.FIND_ELEMENT_BY_XPATH_JS_TEMPLATE % ("elem", self.CHANNEL_MESSAGE_LIST_XPATH), self.SCROLL_DOWN_ELEMENT_JS if scroll_down else self.SCROLL_UP_ELEMENT_JS)
        self.spaces_driver.driver.execute_script(scroll_js)
        self.wait_for_seconds(0.3)
        self.spaces_driver.take_screen_shot("after_scroll")
        logging.info("Scrolling done.")

    def scroll_channel_to_specified_element_by_xpath(self, xpath):
        logging.info("scroll_channel_to_specified_element_by_xpath")
        """
        Scrolls to specified element by xpath
        :return:
        """
        self.wait_for_channel_to_be_ready()
        logging.info("Going to scroll to specified element (xpath)...")
        self.spaces_driver.take_screen_shot("before_scroll_to_elem")
        scroll_js = "%s %s" % (self.FIND_ELEMENT_BY_XPATH_JS_TEMPLATE % ("elemToScroll", xpath), self.SCROLL_TO_ELEMENT_JS_TEMPLATE % "elemToScroll")
        logging.info("Executing scroll script: %s" % scroll_js)
        self.spaces_driver.driver.execute_script(scroll_js)
        self.wait_for_seconds(3)
        self.spaces_driver.take_screen_shot("after_scroll_to_elem")
        logging.info("Scrolling to element done.")

    def check_if_calling_supported(self, error_on_fail=True):
        logging.info("check_if_calling_supported")
        logging.info("if is found : '{0}'".format(self.CALLING_NOT_SUPPORTED_MESG))
        if self.spaces_driver.is_element_visible(locator=self.CALLING_NOT_SUPPORTED_MESG, locator_type=self.XPATH, timeout=5):
            logging.info("Calling not supported dialog shown!")
            self.spaces_driver.take_screen_shot("calling_not_supported_dlg")
            if error_on_fail:
                logging.error("Calling not supported dialog shown!")
                raise Exception("Calling not supported dialog shown!")
            return
        else:
            logging.info("Calling not supported dialog not shown.")
            return

    def wait_for_call_quality_feedback_request_to_be_displayed_for_call_id(self, call_id, timeout=20):
        logging.info("wait_for_call_quality_feedback_request_to_be_displayed_for_call_id")
        """
        Wait for call quality feedback request to be shown in the channel for specified call ID
        :param timeout: 
        :param call_id: call ID of checked meetup
        """
        logging.info("Waiting for call quality feedback request to be displayed for call ID %s" % call_id)
        self.spaces_driver.wait_for_visible(self.CQF_RATING_ELEM_XPATH_TEMPLATE % call_id, self.XPATH, timeout=timeout)
        self.wait_for_seconds(1)
        self.spaces_driver.take_screen_shot("call_quality_feedback_displayed")

    def rate_call_quality_feedback_for_call_id_with_n_stars(self, call_id, n, scroll_to_elem=True):
        logging.info("rate_call_quality_feedback_for_call_id_with_n_stars")
        """
        Rate call with specified call ID with n stars
        :type scroll_to_elem: object
        :param call_id: call ID for rating call
        :param n: how many stars to set
        :return:
        """
        logging.info("Going to rate call with %d star(s)" % n)
        self.spaces_driver.wait_for_visible(self.CQF_NTH_STAR_XPATH_TEMPLATE % (call_id, n), self.XPATH, timeout=5)
        star_elem = self.spaces_driver.wait_for_element(locator=self.CQF_NTH_STAR_XPATH_TEMPLATE % (call_id, n), locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)

        if scroll_to_elem:
            star_elem = self.scroll_channel_to_specified_element_by_xpath(self.CQF_NTH_STAR_XPATH_TEMPLATE % (call_id, n))
        self.wait_for_seconds(1)
        star_elem.click()
        logging.info("Call rated successfully")

    def wait_for_quality_feedback_questionnaire_for_call_id(self, call_id, timeout=5):
        logging.info("wait_for_quality_feedback_questionnaire_for_call_id")
        """
        Wait for call quality feedback questionnaire to appear
        :param timeout: 
        :param call_id: call ID under check
        :return:
        """
        logging.info("Waiting for call quality feedback questionnaire to be displayed for call ID %s" % call_id)
        self.spaces_driver.wait_for_visible(self.CQF_QUESTIONNAIRE_ITEMS_XPATH_TEMPLATE % call_id, self.XPATH, timeout=timeout)
        self.wait_for_seconds(1)
        self.spaces_driver.take_screen_shot("call_quality_feedback_questionnaire_displayed")

    def select_calling_issue_in_call_quality_feedback_questionnaire_for_call_id(self, call_id):
        logging.info("select_calling_issue_in_call_quality_feedback_questionnaire_for_call_id")

        """
        Click at Calling issue in CQF questionnaire form
        :return:
        """
        logging.info("Going to choose calling issue in call quality feedback questionnaire")
        self.spaces_driver.wait_for_visible(self.CQF_QUESTIONNAIRE_ITEM_CALLING_XPATH_TEMPLATE % call_id, self.XPATH, timeout=5)
        self.scroll_channel_to_specified_element_by_xpath(self.CQF_QUESTIONNAIRE_ITEM_CALLING_XPATH_TEMPLATE % call_id)
        star_elem = self.spaces_driver.wait_for_element(locator=self.CQF_QUESTIONNAIRE_ITEM_CALLING_XPATH_TEMPLATE % call_id, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.wait_for_seconds(1)
        star_elem.click()
        logging.info("Call issue selected successfully")

    def select_video_issue_in_call_quality_feedback_questionnaire_for_call_id(self, call_id):
        logging.info("select_video_issue_in_call_quality_feedback_questionnaire_for_call_id")

        """
        Click at Video issue in CQF questionnaire form
        :return:
        """
        logging.info("Going to choose video issue in call quality feedback questionnaire")
        self.spaces_driver.wait_for_visible(self.CQF_QUESTIONNAIRE_ITEM_VIDEO_XPATH_TEMPLATE % call_id, self.XPATH, timeout=5)
        self.scroll_channel_to_specified_element_by_xpath(self.CQF_QUESTIONNAIRE_ITEM_VIDEO_XPATH_TEMPLATE % call_id)
        star_elem = self.spaces_driver.wait_for_element(locator=self.CQF_QUESTIONNAIRE_ITEM_VIDEO_XPATH_TEMPLATE % call_id, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.wait_for_seconds(1)
        star_elem.click()
        logging.info("Video issue selected successfully")

    def select_presenting_issue_in_call_quality_feedback_questionnaire_for_call_id(self, call_id):
        logging.info("select_presenting_issue_in_call_quality_feedback_questionnaire_for_call_id")

        """
        Click at Presenting issue in CQF questionnaire form
        :return:
        """
        logging.info("Going to choose presenting issue in call quality feedback questionnaire")
        self.spaces_driver.wait_for_visible(self.CQF_QUESTIONNAIRE_ITEM_PRESENTING_XPATH_TEMPLATE % call_id, self.XPATH, timeout=5)
        self.scroll_channel_to_specified_element_by_xpath(self.CQF_QUESTIONNAIRE_ITEM_PRESENTING_XPATH_TEMPLATE % call_id)
        star_elem = self.spaces_driver.wait_for_element(locator=self.CQF_QUESTIONNAIRE_ITEM_PRESENTING_XPATH_TEMPLATE % call_id, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.wait_for_seconds(1)
        star_elem.click()
        logging.info("Presenting issue issue selected successfully")

    def submit_call_quality_feedback_questionnaire_for_call_id(self, call_id):
        logging.info("submit_call_quality_feedback_questionnaire_for_call_id")

        """
        Submits CQF questionnaire
        :param call_id:
        :return:
        """
        logging.info("Going to submit call quality feedback questionnaire")
        self.spaces_driver.wait_for_visible(self.CQF_QUESTIONNAIRE_SUBMIT_BUTTON_XPATH_TEMPLATE % call_id, self.XPATH, timeout=5)
        star_elem = self.spaces_driver.wait_for_visible(locator=self.CQF_QUESTIONNAIRE_SUBMIT_BUTTON_XPATH_TEMPLATE % call_id, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.wait_for_seconds(1)
        star_elem.click()
        logging.info("Call quality feedback questionnaire submitted successfully")

    def wait_for_call_quality_feedback_thank_you_confirmation_for_call_id(self, call_id, timeout=5):
        logging.info("wait_for_call_quality_feedback_thank_you_confirmation_for_call_id")

        """
        Wait for CQF thank you confirmation to be displayed for specified call ID
        :param timeout: 
        :param call_id: Call ID to check
        :return:
        """
        logging.info("Waiting for call quality feedback thank you confirmation to be displayed for call ID %s" % call_id)
        self.spaces_driver.wait_for_visible(self.CQF_THANKS_FOR_FEEDBACK_XPATH_TEMPLATE % call_id, self.XPATH, timeout=timeout)
        logging.info("Call quality feedback thank you confirmation displayed successfully")
        self.wait_for_seconds(1)
        self.spaces_driver.take_screen_shot("call_quality_feedback_thank_you_displayed")

    def focus_cqf_for_call_id(self, call_id):
        logging.info("focus_cqf_for_call_id || call id = '{0}'".format(call_id))

        elem = self.spaces_driver.wait_for_element(locator=self.TEAM_CHANNEL_NEW_MESSAGE_INPUT_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        elem.click()

        try:
            elem.find_element_by_xpath(xpath=self.TEAM_CHANNEL_NEW_MESSAGE_INPUT_XPATH)
            elem.send_keys(value=self.spaces_driver.keys.ESCAPE)
            elem = self.spaces_driver.driver.switch_to.active_element
        except Exception, e:
            logging.info("WARNING - FALL BACK TO OLD GET FOCUSED ELEMENT APPROACH due to {0}".format(e))
            elem = self.accessibility.send_keys_and_get_focused_element(elem, self.spaces_driver.keys.ESCAPE)

        # find the message thread of ended call
        count = 0

        while len(elem.find_elements_by_xpath(self.CQF_RATING_ELEM_XPATH_TEMPLATE % call_id)) == 0 and count < self.CQF_SEARCH_LIMIT:
            elem = self.accessibility.send_keys_and_get_focused_element(elem, self.spaces_driver.keys.ARROW_UP)
            count += 1

        if len(elem.find_elements_by_xpath(self.CQF_RATING_ELEM_XPATH_TEMPLATE % call_id)) == 0:
            logging.info("ERROR: Unable to find calling thread with CQF rating")

        for x in range(0, 2):
            elem = self.accessibility.send_keys_and_get_focused_element(elem, self.spaces_driver.keys.ENTER)
        elem = self.accessibility.send_keys_and_get_focused_element(elem, self.spaces_driver.keys.SHIFT, self.spaces_driver.keys.TAB)
        return elem

    def traverse_call_quality_feedback_for_call_id(self, call_id, star_rating_count):
        """
        Focus message tread where star rating was displayed
        :return:
        """
        logging.info("Going to focus the star rating element's parent message thread")
        elem = self.focus_cqf_for_call_id(call_id)

        # check if star rating is focused
        if "rating" in elem.get_attribute("class"):
            logging.info("Star rating element is focused")
        else:
            logging.info("ERROR: Unable to focus star rating element")
        self.spaces_driver.take_screen_shot("star_rating_focused")
        # set stars and send feedback / open CQF form
        arrow_click_count = star_rating_count - self.CQF_DEFAULT_STARS

        if 0 < arrow_click_count <= 2:

            for x in range(0, arrow_click_count):
                elem = self.accessibility.send_keys_and_get_focused_element(elem, self.spaces_driver.keys.SHIFT, self.spaces_driver.keys.ARROW_RIGHT)

        elif 0 > arrow_click_count >= -2:

            for x in range(0, abs(arrow_click_count)):
                elem = self.accessibility.send_keys_and_get_focused_element(elem, self.spaces_driver.keys.SHIFT, self.spaces_driver.keys.ARROW_LEFT)
        logging.info("Star rating is set to %d stars" % star_rating_count)
        self.spaces_driver.take_screen_shot("Star_rating_is_set_to_%d_stars" % star_rating_count)
        elem = self.accessibility.send_keys_and_get_focused_element(elem, self.spaces_driver.keys.ENTER)

        if star_rating_count < self.CQF_MAX_STARS:
            self.spaces_driver.wait_for_visible(locator=self.CQF_QUESTIONNAIRE_BUTTONS_XPATH_TEMPLATE % call_id, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
            self.spaces_driver.take_screen_shot("cqf_form_opened")
            logging.info("Call quality feedback form opened")
            # on tab panel
            elem = self.accessibility.send_keys_and_get_focused_element(elem, self.spaces_driver.keys.ENTER)
            self.spaces_driver.take_screen_shot("cqf_form_first_enter")
            elem = self.accessibility.send_keys_and_get_focused_element(elem, self.spaces_driver.keys.TAB)
            self.spaces_driver.take_screen_shot("cqf_form_second_tab")
            elem = self.accessibility.send_keys_and_get_focused_element(elem, self.spaces_driver.keys.ENTER)
            self.spaces_driver.take_screen_shot("cqf_form_third_enter")
            self.spaces_driver.wait_for_visible(self.CQF_QUESTIONNAIRE_ITEMS_XPATH_TEMPLATE % call_id, self.XPATH, timeout=10)
            self.spaces_driver.take_screen_shot("feedback_details_visible")
            logging.info("Call quality feedback details visible")
            logging.info("send_keys_and_get_focused_element + keypress SPACE : CSS class = '%s'" % (elem.get_attribute("class")))
            elem = self.accessibility.send_keys_and_get_focused_element(elem, self.spaces_driver.keys.SPACE)

            for x in range(0, 7):
                logging.info("send_keys_and_get_focused_element + keypress ARROW_DOWN : CSS class = '%s'" % (elem.get_attribute("class")))
                elem = self.accessibility.send_keys_and_get_focused_element(elem, self.spaces_driver.keys.ARROW_DOWN)
            elem = self.accessibility.send_keys_and_get_focused_element(elem, "Test comment")

            for x in range(0, 1):
                logging.info("send_keys_and_get_focused_element + TAB : CSS class = '%s'" % (elem.get_attribute("class")))
                elem = self.accessibility.send_keys_and_get_focused_element(elem, self.spaces_driver.keys.TAB)
            logging.info("send_keys_and_get_focused_element + keypress ENTER : CSS class = '%s'" % (elem.get_attribute("class")))
            elem = self.accessibility.send_keys_and_get_focused_element(elem, self.spaces_driver.keys.ENTER)

        try :
            variable = self.CQF_THANKS_FOR_FEEDBACK_XPATH_TEMPLATE % call_id
            logging.info("Trying if thanks for feedback is present for already ended meetup '%s'" % variable)
            self.spaces_driver.take_screen_shot("thanks_for_feedback_is_present_for_already_ended_meetup")
            self.spaces_driver.wait_for_visible(variable, self.XPATH, timeout=self.LOADING_TIMEOUT)
        except Exception, e:
            logging.info("Exception was catch \n Exception : \n %s \n" %e)
            variable = self.CQF_THANKS_FOR_FEEDBACK_IN_PROGRESS_XPATH_TEMPLATE % call_id
            logging.info("Trying if thanks for feedback is present for ongoing meetup '%s'" % variable)
            self.spaces_driver.take_screen_shot("Trying_if_thanks_for_feedback_is_present_for_ongoing_meetup")

        self.spaces_driver.wait_for_visible(variable, self.XPATH, timeout=10)
        self.spaces_driver.take_screen_shot("feedback_confirmation_visible")
        logging.info("Feedback confirmation displayed")

    def start_new_meetup(self, timeout=15):
        """
        Confirms new meetup start from new meetup experience
        :return:
        """
        logging.info("Starting new meetup from new meetup experience")
        start_button = self.spaces_driver.wait_for_element(locator=self.CHANNEL_CONVERSATION_NEW_CALL_START_BUTTON_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.spaces_driver.take_screen_shot("before_meetup_start")
        start_button.click()
        self.spaces_driver.wait_for_visible(locator=self.CALLING_SCREEN_XPATH, locator_type=self.XPATH, timeout=timeout)
        self.spaces_driver.take_screen_shot("meetup_started")

    def select_screen_from_screen_share_panel(self):
        logging.info("Selecting first screen from screen share panel...")
        first_screen = self.spaces_driver.wait_for_element(locator=self.CALLING_SCREEN_SHARE_DESKTOP_PANEL_SCREEN_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        first_screen.click()

    def click_at_share_desktop_button(self):
        logging.info("Clicking on share desktop...")
        share_desktop_button = self.spaces_driver.wait_for_element(locator=self.CALLING_SCREEN_SHARE_DESKTOP_BUTTON_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.spaces_driver.move_mouse_to_element(share_desktop_button)
        self.wait_for_seconds(1)
        self.spaces_driver.take_screen_shot("before_share_desktop_button_clicked")
        share_desktop_button.click()
        self.wait_for_seconds(1)
        self.spaces_driver.take_screen_shot("after_share_desktop_button_clicked")

        if self.spaces_driver.is_element_present(locator=self.CALLING_SCREEN_SHARE_DESKTOP_PANEL_XPATH, locator_type=self.XPATH, timeout=10):
            self.select_screen_from_screen_share_panel()

        logging.info("starting screen share")

    def click_at_start_call_button(self, meetup_title=None, wait_for_seconds_after_call_start=5, reply_chain_call_id=None):
        logging.info("click_at_start_call_button")
        self.wait_for_channel_to_be_ready()

        if reply_chain_call_id:
            call_start_button = self.CHANNEL_REPLY_CHAIN_CALL_START_BUTTON_XPATH_TEMPLATE % reply_chain_call_id
            self.wait_for_seconds(0.5)
            self.spaces_driver.take_screen_shot("reply_button_clicked")
        else:
            call_start_button = self.CHANNEL_CONVERSATION_CALL_START_BUTTON_XPATH

        self.spaces_driver.take_screen_shot("call_button_wait_for_appear")
        call_button = self.spaces_driver.wait_for_element(locator=call_start_button, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        logging.info("Clicking at call button to start a call.")
        self.spaces_driver.wait_for_visible(locator=call_start_button, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.spaces_driver.take_screen_shot("call_button_before_click")
        call_button.click()
        self.wait_for_seconds(5)
        self.spaces_driver.take_screen_shot("call_button_clicked")

        if reply_chain_call_id:
            self.spaces_driver.wait_for_element(self.CHANNEL_CONVERSATION_NEW_CALL_START_BUTTON_XPATH, self.XPATH, timeout=5)
            self.scroll_channel_to_specified_element_by_xpath(self.CHANNEL_CONVERSATION_NEW_CALL_START_BUTTON_XPATH)

        self.spaces_driver.wait_for_visible(locator=self.CHANNEL_CONVERSATION_NEW_CALL_START_BUTTON_XPATH, locator_type=self.XPATH, timeout=5)
        self.spaces_driver.take_screen_shot("new_meetup_exp")
        self.set_call_title_in_new_meetup(title=meetup_title)
        self.start_new_meetup()
        self.spaces_driver.take_screen_shot("call_created")
        self.wait_for_call_to_connect()

        if wait_for_seconds_after_call_start > 0:
            logging.info("Waiting %d seconds after call start." % wait_for_seconds_after_call_start)
            self.wait_for_seconds(wait_for_seconds_after_call_start)
        self.ongoing_call_make_sure_video_is_on()

    def wait_for_call_to_connect(self, timeout=120):
        """
        Waits until call time counter appears in the calling screen
        :return:
        """
        logging.info("Waiting for the call to connect")
        self.spaces_driver.wait_for_visible(self.CALLING_SCREEN_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.spaces_driver.wait_for_visible(self.CALL_COUNTER_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        logging.info("Call successfully connected.")
        # Due to slowness of application and not updating channel with ongoing meetups we need to prolong in call time
        self.wait_for_seconds(10)
        self.spaces_driver.take_screen_shot("call_connected")

    def get_call_id(self, retries=10):
        logging.info("Getting Call ID for call in progress")

        for i in range(0, retries):
            call_id = self.spaces_driver.driver.execute_script(self.GET_CALL_ID_ANGULAR_JS)

            if len(call_id) > 20:
                logging.info("Call ID: %s" % call_id)
                # Due to slowness of application and not updating channel with ongoing meetups we need to prolong in call time
                self.wait_for_seconds(10)
                return call_id
            else:
                logging.info("Call ID not detected, retrying..")
                self.wait_for_seconds(1)
        return None

    def get_all_log_events(self):
        logging.info("Getting all the log events..")
        log_events = self.spaces_driver.driver.execute_script(self.GET_ALL_LOG_EVENTS_JS)
        logging.info("Done..")
        try:
            return log_events.encode('utf-8')
        except Exception, e:
            logging.error("Exception while encoding logs to UTF-8, returning raw data: \n Exception : \n %s \n" %e)
            return log_events

    def wait_and_click_at_start_1_1_call_button(self, with_video=True, timeout=LOADING_TIMEOUT):
        logging.info("wait_and_click_at_start_1_1_call_button")

        if with_video:
            xpath = self.CHAT_VIDEO_CALL_START_BUTTON_XPATH
        elif not with_video:
            xpath = self.CHAT_AUDIO_CALL_START_BUTTON_XPATH

        if self.spaces_driver.is_element_present(locator=xpath, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT):
            call_button = self.spaces_driver.wait_for_element(locator=xpath, locator_type=self.XPATH, timeout=timeout)
            self.spaces_driver.take_screen_shot("before_call_start")
            logging.info("Clicking at 1:1 call button")
            call_button.click()
            logging.info("Waiting for calling screen to be opened.")
            self.spaces_driver.wait_for_visible(locator=self.CALLING_SCREEN_XPATH, locator_type=self.XPATH, timeout=timeout)
            self.spaces_driver.take_screen_shot("call_started")
            return
        else:
            logging.info("xpath = '{0}'".format(xpath))
            self.spaces_driver.take_screen_shot("ERROR_START_CALL_BUTTON_NOT_FOUND")
            logging.error("Call not Started start call button not found")
            raise Exception("Call not Started start call button not found")

    def wait_for_participant_to_join_1_1_call(self, participant_email, timeout=CALLING_TIMEOUT):
        logging.info("Waiting for participant to join a 1:1 call")
        step = 0
        # Negativni pristup testu detekujem error stavy
        while self.spaces_driver.is_element_present(locator=self.CALL_1_1_PARTICIPANT_ANIMATION_XPATH_TEMPLATE % participant_email, locator_type=self.XPATH, timeout=1) and step < timeout:
            step += 1

        if self.spaces_driver.is_element_present(locator=self.CALL_1_1_PARTICIPANT_ANIMATION_XPATH_TEMPLATE % participant_email, locator_type=self.XPATH, timeout=0):
            logging.info("Seems participant has not joined 1:1 call")
            self.spaces_driver.take_screen_shot("participant_not_joined_call")
            raise Exception("Seems participant has not joined 1:1 call")

        elif self.spaces_driver.is_element_present(self.CALL_1_1_JOIN_ERROR_STATE_XPATH, self.XPATH) and self.spaces_driver.driver.find_element_by_xpath(self.CALL_1_1_JOIN_ERROR_STATE_XPATH).is_displayed():
            logging.info("Seems participant was not able to join 1:1 call")
            self.spaces_driver.take_screen_shot("participant_failed_join_call")
            raise Exception("Seems participant was not able to join 1:1 call")

        logging.info("Participant probably successfully joined 1:1 call")
        self.spaces_driver.take_screen_shot("participant_joined_call")

    def navigate_to_chat_section(self):
        self.focus_spaces_app()
        logging.info("Navigating to Chat section...")
        app_bar_teams_button = self.spaces_driver.wait_for_element(self.APP_BAR_CHAT_BUTTON_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        app_bar_teams_button.click()
        self.spaces_driver.wait_for_visible(self.CHAT_LIST_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.spaces_driver.take_screen_shot("chat_list_opened")

    def click_at_active_call_recents_entry(self, timeout=CALLING_TIMEOUT):
        logging.info("Waiting for active call in chat recents section.")
        active_call_chat = self.spaces_driver.wait_for_element(self.CHAT_RECENTS_ACTIVE_CALL_XPATH, self.XPATH, timeout=timeout)
        logging.info("Active call in chat recents found.")
        self.spaces_driver.take_screen_shot("active_call_in_recents_menu")
        self.spaces_driver.click_js(active_call_chat)

    def check_1_1_chat_opened_with_user(self, username, timeout=LOADING_TIMEOUT):
        self.spaces_driver.wait_for_visible(self.CHAT_USERNAME_HEADER_XPATH_TEMPLATE % username, self.XPATH, timeout=timeout)

    def open_chat_with_person(self, username, from_channel=False):
        self.open_chat_with_people([username], from_channel=from_channel)

    def open_chat_with_people(self, usernames, from_channel=False):
        logging.info("Going to create a new chat with people: %s" % usernames)
        new_chat_btn_xpath = self.CHAT_CREATE_CHAT_BTN_XPATH

        if from_channel:
            logging.info("  * from teams section")
            new_chat_btn_xpath = self.TEAMS_CREATE_CHAT_BTN_XPATH
        else:
            logging.info("  * from chat section")
            self.navigate_to_chat_section()
        logging.info("Clicking at new chat button")
        # Newly using selector with or so no logic required for different targets
        create_new_chat_button = self.spaces_driver.wait_for_element(locator=new_chat_btn_xpath, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        create_new_chat_button.click()

        for username in usernames:
            self.type_and_pick_user_in_new_chat_creation_header(username)

        self.wait_for_channel_to_be_ready()
        msg = "%s" % self.generate_string(prefix="Hey,")
        self.send_message_to_conversation(msg)
        self.verify_message_received_in_conversation(msg)
        # In app change when more than one user is displayed this following check no longer works as now is displayed some king of merged icon that doesnt contains users email addresses
        if len(usernames) == 1:
            # for username in usernames:
            self.check_1_1_chat_opened_with_user(usernames[0])
        self.spaces_driver.take_screen_shot("chat_opened")

    def type_and_pick_user_in_new_chat_creation_header(self, username):
        logging.info("Picking user '%s' in new chat creation header" % username)
        picker = self.spaces_driver.wait_for_element(self.CHAT_CREATE_NEW_INPUT_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        picker.send_keys(username)
        user_chooser = self.spaces_driver.wait_for_element(self.CHAT_USER_CHOOSER_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        user_chooser.click()
        logging.info("User '%s' picked to new chat creation header" % username)

    def type_and_pick_user_in_add_group_chat_dialog(self, username):
        logging.info("Picking user '%s' in add user to group creation dialog" % username)
        picker = self.spaces_driver.wait_for_element(self.CHAT_PEOPLE_PICKER_INPUT_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        picker.send_keys(username)
        user_chooser = self.spaces_driver.wait_for_element(self.CHAT_USER_CHOOSER_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        user_chooser.click()
        logging.info("User '%s' picked to group creation dialog" % username)

    def add_participant_to_group_chat(self, username):
        """
        Adds person to the opened group chat
        :param username: person to add
        :return:
        """
        logging.info("Adding %s to the group chat" % username)
        button = self.spaces_driver.wait_for_element(self.CHAT_ADD_PARTICIPANT_BUTTON_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.spaces_driver.click_js(button)
        self.type_and_pick_user_in_add_group_chat_dialog(username)
        logging.info("Clicking at add button")
        add_button = self.spaces_driver.wait_for_element(locator=self.CHAT_ADD_USER_BUTTON_XPATH,locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        add_button.click()
        self.spaces_driver.wait_for_visible(self.CHAT_GROUP_HEADER_XPATH_TEMPLATE % username, self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.spaces_driver.take_screen_shot("user_added_to_group")

    def set_call_title_in_new_meetup(self, title, title_length=10):
        """
        Types in call title in new meetup experience
        :param title_length: length of title 
        :param title: if empty, we generate random string
        """
        logging.info("Going to set meetup title in new call experience")

        if not title:
            title = self.generate_string(title_length)
        self.spaces_driver.take_screen_shot("before_title_input")
        title_elem = self.spaces_driver.wait_for_element(self.CHANNEL_CONVERSATION_CALL_TITLE_INPUT_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        title_elem.send_keys(title)
        self.spaces_driver.take_screen_shot("after_title_input")
        logging.info("Meetup title set to '%s'" % title)

    @staticmethod
    def generate_string(title_length=10, prefix="My meeting "):
        """
        Generate random string of the specified length
        :param prefix: prefix
        :param title_length: length of generated string
        :return: generated string
        """
        random_title = prefix + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(title_length))
        logging.info("generating random call title string : '%s'" % random_title)
        return random_title

    def change_meetup_title_in_calling_header(self, title):
        """
        Changes meetup title in calling screen while on meetup
        :param title: new title string
        :return:
        """
        logging.info("Going to change meetup title in calling screen")
        # Make calling header to be visible by moving a mouse
        calling_screen = self.spaces_driver.wait_for_element(self.CALLING_SCREEN_XPATH, self.XPATH, self.LOADING_TIMEOUT)
        self.spaces_driver.move_mouse_to_element(calling_screen)
        self.wait_for_seconds(1)
        # Activate meetup title editing
        meetup_title = self.spaces_driver.wait_for_element(self.CALLING_SCREEN_MEETUP_TITLE_XPATH, self.XPATH)
        meetup_title.click()
        self.spaces_driver.take_screen_shot("meetup_title_in_edit")
        # Type in new meetup
        meetup_title_input = self.spaces_driver.wait_for_element(self.CALLING_SCREEN_MEETUP_TITLE_INPUT_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        meetup_title_input.clear()
        self.wait_for_seconds(1)
        meetup_title_input.send_keys(title)
        self.spaces_driver.take_screen_shot("new_title_entered")
        # Save new meetup title
        meetup_title_input.send_keys(self.spaces_driver.keys.ENTER)
        self.wait_for_seconds(0.3)
        self.spaces_driver.take_screen_shot("new_title_saved")

    def wait_for_meetup_title_update_in_channel_by_call_id(self, call_id, title, retry=60):
        """
        Waits for meetup title to update to new value in the channel
        :param call_id:  call id
        :param title: new title to expect in the channel's call header
        :param retry: retrying the title test
        :return:
        """
        self.wait_for_channel_to_be_ready()
        logging.info("Waiting for meetup title to update in the channel")
        meetup_title = self.spaces_driver.wait_for_element(self.CHANNEL_CONVERSATION_MEETUP_TITLE_FOR_CALL_ID_XPATH_TEMPLATE % call_id, self.XPATH)
        logging.info("Meetup title is '{0}'".format(meetup_title.text))
        logging.info("Waiting for title to be '{0}'".format(title))
        attempt = 0

        while meetup_title.text != title and attempt < retry:
            attempt += 1
            logging.info("Attempt #{0}: Meetup title not updated yet".format(attempt))
            self.wait_for_seconds(1)
            try:
                meetup_title = self.spaces_driver.wait_for_element(self.CHANNEL_CONVERSATION_MEETUP_TITLE_FOR_CALL_ID_XPATH_TEMPLATE % call_id, self.XPATH)
            except Exception, e:
                raise Exception("Meeting in the channel seems to disappear: \n Exception : \n {0} \n".format(e))

        if meetup_title.text == title:
            logging.info("If ((meetup_title.text == title)) is True")
            title_xpath = self.CHANNEL_CONVERSATION_MEETUP_TITLE_FOR_ONGOING_MEETUP_TEMPLATE + XPathBuilder.xpath_equals_or_contains_attribute(element="div", attribute="title", value=title)
            logging.info("title_xpath = '{0}'".format(title_xpath))
            meetup_title = self.spaces_driver.wait_for_element(locator=title_xpath, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
            self.spaces_driver.scroll_channel_to_specified_element_by_xpath(meetup_title)
        else:
            self.spaces_driver.take_screen_shot("FAILED_title_not_updated_in_channel")
            raise Exception("Meetup title not updated to '{0}' in the channel".format(title))

        self.spaces_driver.take_screen_shot("title_successfully_updated_in_channel")

    def wait_for_meetup_title_update_in_channel(self, initiator_email, title, timeout=CALLING_TIMEOUT):
        """
        Waits for meetup title to update to new value in the channel
        :param initiator_email: email
        :param title: new title to expect in the channel's call header
        :param timeout: time period to wait for the change to appear
        :return:
        """
        self.wait_for_channel_to_be_ready()
        logging.info("Waiting for meetup title to update in the channel")
        meetup_title = self.spaces_driver.wait_for_element(self.CHANNEL_CONVERSATION_MEETUP_TITLE_FOR_INITIATOR_SPECIFIED_XPATH_TEMPLATE % initiator_email, self.XPATH, 60)
        logging.info("Meetup title is '{0}'".format(meetup_title.text))
        logging.info("Waiting for title to be {0}".format(title))
        attempt = 0

        while meetup_title.text != title and attempt < timeout:
            attempt += 1
            logging.info("Attempt #%d: Meetup title not updated yet" % attempt)
            self.wait_for_seconds(1)
            try:
                meetup_title = self.spaces_driver.wait_for_element(self.CHANNEL_CONVERSATION_MEETUP_TITLE_FOR_INITIATOR_SPECIFIED_XPATH_TEMPLATE % initiator_email, self.XPATH)
            except Exception, e:
                raise Exception("Meeting in the channel seems to disappear: \n Exception : \n %s \n" %e)

        if meetup_title.text == title:
            logging.info("Meetup title successfully updated to '%s'" % title)
            self.spaces_driver.take_screen_shot("title_updated_in_channel")
        else:
            self.spaces_driver.take_screen_shot("title_not_updated_in_channel")
            raise Exception("Meetup title not updated to '%s' in the channel" % title)

    def open_in_call_chat(self):
        """
        Open in-call chat while on a call
        :return:
        """
        logging.info("Going to open in-call chat")
        # Check if in-call chat already opened
        self.spaces_driver.wait_for_visible(self.CALLING_SCREEN_TOGGLE_CHAT_ENABLED_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)

        if self.spaces_driver.is_element_visible(self.CALLING_SCREEN_TOGGLE_CHAT_ENABLED_ACTIVE_XPATH, self.XPATH, timeout=5):
            logging.info("In-call chat already opened.")
            self.spaces_driver.take_screen_shot("in-call-chat-already-opened")
            self.spaces_driver.wait_for_visible(self.CALLING_SCREEN_NEW_MESSAGE_INPUT, self.XPATH, timeout=self.LOADING_TIMEOUT)
            return
        else:
            logging.info("In-call chat not opened, going to open it")
            toggle_chat = self.spaces_driver.wait_for_element(self.CALLING_SCREEN_TOGGLE_CHAT_ENABLED_NOT_ACTIVE_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
            calling_screen = self.spaces_driver.wait_for_element(self.CALLING_SCREEN_XPATH, self.XPATH, self.LOADING_TIMEOUT)
            self.spaces_driver.move_mouse_to_element(calling_screen)
            self.wait_for_seconds(1)
            self.spaces_driver.take_screen_shot("before_toggling_chat")
            logging.info("Toggling in-call chat.")
            toggle_chat.click()

        # Verify that in-call chat is opened
        self.spaces_driver.wait_for_visible(self.CALLING_SCREEN_TOGGLE_CHAT_ENABLED_ACTIVE_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.spaces_driver.wait_for_visible(self.CALLING_SCREEN_NEW_MESSAGE_INPUT, self.XPATH, timeout=self.LOADING_TIMEOUT)
        logging.info("In-call chat opened successfully and new message input box is visible")
        self.spaces_driver.take_screen_shot("in-call-chat-opened")
        return

    def open_in_call_add_participant(self):
        """
        Open in-call add participant while on call
        :return:
        """
        logging.info("Going to open in-call add participant")
        # Check if in-call add participant already opened
        logging.info("Is In-call add participant already opened?")

        try:
            self.spaces_driver.wait_for_visible(self.CALLING_SCREEN_ADD_PARTICIPANT_PANE_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
            return
        except Exception, e:
            logging.info("In-call add participant not opened, going to open it. \n Exception : \n %s \n" %e)
        self.spaces_driver.take_screen_shot("in-call-add-participant")
        add_participant_btn = self.spaces_driver.wait_for_element(self.CALLING_SCREEN_ADD_PARTICIPANT_BUTTON_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        calling_screen = self.spaces_driver.wait_for_element(self.CALLING_SCREEN_XPATH, self.XPATH, self.LOADING_TIMEOUT)
        self.spaces_driver.move_mouse_to_element(calling_screen)
        self.wait_for_seconds(1)
        self.spaces_driver.take_screen_shot("before_opening_add_participant")
        add_participant_btn.click()
        logging.info("Opening in-call add participant.")
        # Verify that in-call add participant is opened
        self.spaces_driver.wait_for_visible(self.CALLING_SCREEN_ADD_PARTICIPANT_PANE_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        logging.info("In-call add participant opened successfully.")
        self.spaces_driver.take_screen_shot("in-call-add-participant-opened")

    def add_participant_to_meetup(self, username):
        """
        Adds participant to the ongoing meetup
        pre-condition: User is on the meetup and calling screen is opened
        :param username: username to add to the meetup
        :return:
        """
        self.open_in_call_add_participant()
        logging.info("Going to add %s to the meetup" % username)
        participant_search_input = self.spaces_driver.wait_for_element(self.CALLING_SCREEN_INVITE_INPUT_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        participant_search_input.send_keys(username)
        self.wait_for_seconds(1)
        logging.info("Username typed to the search box")
        self.spaces_driver.take_screen_shot("add_participant_typed_to_search")
        user_search_result_item = self.spaces_driver.wait_for_element(self.CALLING_SCREEN_SEARCH_RESULT_USER_XPATH_TEMPLATE % username, self.XPATH, timeout=self.LOADING_TIMEOUT)
        user_search_result_item.click()
        logging.info("User %s nudged to the meetup")
        self.wait_for_seconds(1)
        self.spaces_driver.take_screen_shot("user_nudged_to_meetup")
        self.spaces_driver.wait_for_visible(self.CALLING_SCREEN_USER_CONNECTING_XPATH_TEMPLATE % username, self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.ongoing_call_make_sure_video_is_on()

    def send_message_to_conversation(self, msg):
        """
        Sends message to opened in-call chat
        :param msg: message to send
        :return:
        """
        try:
            logging.info("send_message_to_conversation - Going to send message '%s' to conversation." %msg)
            self.spaces_driver.take_screen_shot("send_message_to_conversation")

            if self.spaces_driver.is_element_visible(locator=self.CALLING_SCREEN_NEW_MESSAGE_INPUT, locator_type=self.XPATH, timeout=10):
                msg_editor_xpath = self.CALLING_SCREEN_NEW_MESSAGE_INPUT
                logging.info("msg_editor_xpath == self.CALLING_SCREEN_NEW_MESSAGE_INPUT == " + self.CALLING_SCREEN_NEW_MESSAGE_INPUT)

            elif self.spaces_driver.is_element_visible(locator=self.CHAT_NEW_MESSAGE_INPUT_COMMON, locator_type=self.XPATH, timeout=5):
                msg_editor_xpath = self.CHAT_NEW_MESSAGE_INPUT_COMMON
                logging.info("msg_editor_xpath == self.CHAT_NEW_MESSAGE_INPUT_COMMOMN == " + self.CHAT_NEW_MESSAGE_INPUT_COMMON)

            else:
                msg_editor_xpath = self.CHAT_NEW_MESSAGE_INPUT
                logging.info("msg_editor_xpath == self.NEW_MESSAGE_INPUT == " + self.CHAT_NEW_MESSAGE_INPUT)

            try :
                new_message_input = self.spaces_driver.wait_for_element(locator=msg_editor_xpath, locator_type=self.XPATH)
                new_message_input.send_keys(msg)
                self.spaces_driver.take_screen_shot("new_message_inputted")


                if self.spaces_driver.is_element_visible(self.CHAT_NEW_MESSAGE_INPUT_FOCUSED, self.XPATH, 5):
                    new_message_input_focused = self.spaces_driver.wait_for_element(self.CHAT_NEW_MESSAGE_INPUT_FOCUSED, self.XPATH)
                elif self.spaces_driver.is_element_visible(self.CALLING_SCREEN_NEW_MESSAGE_INPUT_FOCUSED, self.XPATH, 5):
                    new_message_input_focused = self.spaces_driver.wait_for_element(self.CALLING_SCREEN_NEW_MESSAGE_INPUT_FOCUSED, self.XPATH)
                elif self.spaces_driver.is_element_visible(self.CHAT_NEW_MESSAGE_INPUT, self.XPATH, 5):
                    new_message_input_focused = self.spaces_driver.wait_for_element(msg_editor_xpath, self.XPATH)
                else:
                    raise TimeoutException("New message input not detected !! exception NoSuchElementException", TimeoutException)

                new_message_input_focused.is_displayed()

            except TimeoutException, e:
                logging.info("ERROR New message input field wasn't found - Caught NoSuchElementException - {0}".format(e))
                self.spaces_driver.take_screen_shot("ERROR_NEW_MESSAGE_INPUT")
                raise TimeoutException(e)

            self.spaces_driver.take_screen_shot("new_message_input_should_contains_message")
            logging.info("new_message_input_should_contains message '{0}'".format(msg))

            if not self.spaces_driver.is_text_present_in_input(msg=msg, locator=msg_editor_xpath, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT):
                logging.info("text '{0}' not present located by '{1}' : '{2}'".format(msg, self.XPATH, msg_editor_xpath))
                logging.warning("text '{0}' not present located by '{1}' : '{2}'".format(msg, self.XPATH, msg_editor_xpath))
                logging.error("text '{0}' not present located by '{1}' : '{2}'".format(msg, self.XPATH, msg_editor_xpath))
            # Send message
            self.spaces_driver.wait_for_element(msg_editor_xpath, self.XPATH, 15)
            new_message_input.send_keys(self.spaces_driver.keys.ENTER)
            logging.info("Message submitted by hitting keys.ENTER")
            self.spaces_driver.wait_for_element(self.CHAT_MESSAGE_TEMPLATE_XPATH % msg, self.XPATH)
            self.spaces_driver.take_screen_shot("msg_sent")
        except TimeoutException as e:
            logging.info("Error while sending message: {0}".format(e))
            self.spaces_driver.take_screen_shot("cannot_send_msg")
            # Not treating refresh message as exception as we want to test calling and not chats
            if not self.spaces_driver.is_text_visible(self.PLEASE_REFRESH_MSG):
                raise TimeoutException("Error while sending message : {0}".format(e))

    def reply_message_to_conversation_by_call_id(self, call_id, mesg):
        logging.info("Going to reply to the meetup conversation by call ID: %s" % call_id)
        reply_button = self.spaces_driver.driver.find_element_by_xpath(self.CHANNEL_REPLY_BTN_FOR_CALL_ID_TEMPLATE % call_id)
        reply_button.click()
        self.wait_for_seconds(1)
        logging.info("Reply message input opened.")
        # message_input = self.spaces_driver.driver.switch_to_active_element()
        self.spaces_driver.wait_for_visible(self.CHANNEL_REPLY_MESSAGE_INPUT_XPATH_TEMPLATE % call_id, self.XPATH, timeout=self.LOADING_TIMEOUT)
        message_input = self.spaces_driver.wait_for_element(locator=self.CHANNEL_REPLY_MESSAGE_INPUT_XPATH_TEMPLATE % call_id, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        message_input.send_keys(mesg)
        self.wait_for_seconds(1)
        logging.info("Message typed in")
        message_input.send_keys(self.spaces_driver.keys.ENTER)
        self.spaces_driver.wait_for_visible(self.CHANNEL_REPLY_CHAIN_MESSAGE_CONTENT_CALL_ID_XPATH_TEMPLATE % (call_id, mesg), self.XPATH, timeout=self.LOADING_TIMEOUT)
        logging.info("Message sent to reply-chain")
        self.spaces_driver.take_screen_shot("reply_chain_message_sent")

    def verify_message_received_in_conversation(self, msg, timeout=LOADING_TIMEOUT):
        """
        Verifies that specified message is visible in conversation pane
        pre-condition: in-call chat is opened
        :param msg: message to look for
        :return:
        """
        logging.info("Verifying message '%s' to appear in conversation pane" % msg)
        try:
            self.spaces_driver.wait_for_visible(self.CALLING_SCREEN_MESSAGES_PANE_TEXT_XPATH_TEMPLATE % msg, self.XPATH, timeout=timeout)
            logging.info("Message successfully visible in chat pane")
            self.spaces_driver.take_screen_shot("msg_sent")
        except Exception as e:
            logging.info("Error while verifying message sent: %s" % e)
            self.spaces_driver.take_screen_shot("msg_not_visible")
            # Not treating refresh message as exception as we want to test calling and not chats
            if not self.spaces_driver.is_text_visible(self.PLEASE_REFRESH_MSG):
                raise Exception("Unknown error while verifying message sent")

    def hang_up_ongoing_call(self, by_js=True):
        logging.info("Going to hang up the call..")

        if by_js:
            logging.info("  - by JS direct call")
            self.spaces_driver.driver.execute_script(self.CALL_HANGUP_EXE_ANGULAR_JS)
        else:
            logging.info("  - by clicking at hang-up button")
            hang_up = self.spaces_driver.wait_for_element(locator=self.CALLING_SCREEN_HANGUP_BUTTON_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT, fail_on_not_found=False)
            self.spaces_driver.move_mouse_to_element(hang_up)
            self.wait_for_seconds(1)
            self.spaces_driver.take_screen_shot("before_hang_up")
            hang_up.click()
        logging.info("Call hanging up.")
        self.spaces_driver.wait_for_element_visible(locator=self.CALL_HANGING_UP_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT, fail_on_not_found=False)
        self.spaces_driver.take_screen_shot("call_hanging_up")
        timeout = 15
        attempt = 0

        while self.spaces_driver.is_element_present(self.CALLING_SCREEN_XPATH, self.XPATH) and attempt < timeout:
            attempt += 1
            logging.info("Attempt #%d: Call not hang up yet." % attempt)
            self.wait_for_seconds(1)

        if self.spaces_driver.is_element_present(self.CALLING_SCREEN_XPATH, self.XPATH, 5):
            self.spaces_driver.take_screen_shot("call_not_hang_up")
            raise Exception("Call not hang up, calling screen still present")
        logging.info("Call hang up done.")
        self.spaces_driver.take_screen_shot("call_hang_up")

    def wait_for_meetup_ended_msg_in_channel(self, call_id, timeout=LOADING_TIMEOUT):
        """
        Waits until meetup ended message appears in the channel
        :param call_id: call id
        :param timeout: time to wait until message appears
        :return:
        """
        logging.info("Waiting for meetup ended message to appear in channel..")
        meetup_ended_xpath = self.CHANNEL_CONVERSATION_MEETUP_ENDED_XPATH_DTID_TEMPLATE % call_id
        self.spaces_driver.wait_for_visible(meetup_ended_xpath, self.XPATH, timeout=timeout)
        logging.info("Meetup ended message for call initiator %s appeared in a channel" % call_id)
        self.spaces_driver.take_screen_shot("meetup_ended_in_channel")

    def ongoing_call_make_sure_video_is_on(self):
        logging.info("ongoing_call_make_sure_video_is_on")
        if self.spaces_driver.is_element_present(locator=self.VIDEO_TURN_ON_XPATH, locator_type=self.XPATH, timeout=5):
            logging.info("Video is currently off")
            self.ongoing_call_turn_video(turn_on=True)
            logging.info("Video has been turned on")
            return
        elif self.spaces_driver.is_element_present(locator=self.VIDEO_TURN_OFF_XPATH, locator_type=self.XPATH, timeout=5):
            logging.info("Video is currently on")
            return

    def ongoing_call_turn_video(self, turn_on = None, by_js=False):
        logging.info("ongoing_call_turn_video turn_on --> {0}".format(turn_on))
        default_button = self.spaces_driver.wait_for_element(locator=self.VIDEO_TOGGLE_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        if by_js and turn_on is True or False:
            logging.info("Turning video on or off by_js")
            if turn_on is False:
                logging.info("is_video_on is False =?= '{0}'".format(turn_on))
                self.spaces_driver.driver.execute_script(self.CALL_STOP_VIDEO_EXE_ANGULAR_JS)
                return
            elif turn_on is True:
                logging.info("is_video_on is True =?= '{0}'".format(turn_on))
                self.spaces_driver.driver.execute_script(self.CALL_STOP_VIDEO_EXE_ANGULAR_JS)
                return
            logging.info("Ignoring configured by_js because turn_on / is_video_on was not set =?={0}".format(turn_on))
            logging.info("Attempting to fall back to normal button clicking")
        if turn_on is True:
            logging.info("turning on")
            button = self.spaces_driver.wait_for_element(locator=self.VIDEO_TURN_ON_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)

            self.spaces_driver.move_mouse_to_element(button)

            button.click()
            self.spaces_driver.move_mouse_to_element(default_button)
            button = self.spaces_driver.wait_for_element(locator=self.VIDEO_TURN_OFF_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
            self.spaces_driver.move_mouse_to_element(button)
        elif turn_on is False:
            # Turn off
            logging.info("turning off")
            button = self.spaces_driver.wait_for_element(locator=self.VIDEO_TURN_OFF_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
            self.spaces_driver.move_mouse_to_element(button)
            button.click()
            self.spaces_driver.move_mouse_to_element(default_button)
            button = self.spaces_driver.wait_for_element(locator=self.VIDEO_TURN_ON_XPATH, locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
            self.spaces_driver.move_mouse_to_element(button)
        elif turn_on is None:
            logging.info("just switching no matter is it is already on or of")
            self.spaces_driver.move_mouse_to_element(default_button)
            default_button.click()
            self.spaces_driver.move_mouse_to_element(default_button)
            if self.spaces_driver.is_element_present(locator=self.VIDEO_TURN_OFF_XPATH, locator_type=self.XPATH, timeout=0):
                logging.info("Video was Turned On")
            elif self.spaces_driver.is_element_present(locator=self.VIDEO_TURN_ON_XPATH, locator_type=self.XPATH, timeout=0):
                logging.info("Video was Turned Off")
            else :
                logging.warning("Couldn't detect correct video button end-state")
        return

    def toggle_video_ongoin_call(self, is_video_on=True, by_js=False):
        logging.info("Toggling video...")
        if by_js:
            logging.info(" - by JS direct call")
            if is_video_on:
                self.spaces_driver.driver.execute_script(self.CALL_STOP_VIDEO_EXE_ANGULAR_JS)
            else:
                self.spaces_driver.driver.execute_script(self.CALL_STOP_VIDEO_EXE_ANGULAR_JS)
        else:
            logging.info("  - by clicking at video button")
            toggle_video = self.spaces_driver.wait_for_element(self.CALLING_SCREEN_TOGGLE_VIDEO_BUTTON_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)

            self.spaces_driver.take_screen_shot("before_toggle_video")
            try:
                self.spaces_driver.move_mouse_to_element(toggle_video)
                toggle_video.click()
            except StaleElementReferenceException:
                logging.info("StaleElementReferenceException")
                ActionChains(self.spaces_driver.driver).move_to_element(toggle_video).click(toggle_video).perform()

            self.spaces_driver.take_screen_shot("after_toggle_video")

        logging.info("Call toggle video is done.")
        self.wait_for_seconds(2)
        self.spaces_driver.take_screen_shot("call_toggle_video")

    def check_in_app_call_monitor(self):
        logging.info("Checking in app calling monitor...")
        self.spaces_driver.wait_for_element(self.CHANNEL_CONVERSATION_CALL_MONITOR_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        logging.info("In app calling monitor found")

    def navigate_from_call_to_channel(self):
        """
        While on a call navigate to 'General' channel for the 1st team in the channel-list
        """
        logging.info("Navigating away from the call to the channel...")
        calling_screen = self.spaces_driver.wait_for_element(self.CALLING_SCREEN_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.spaces_driver.move_mouse_to_element(calling_screen)
        app_bar_teams_button = self.spaces_driver.wait_for_element(self.APP_BAR_TEAMS_BUTTON_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        app_bar_teams_button.click()
        self.spaces_driver.wait_for_visible(self.CHANNEL_LIST_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.spaces_driver.take_screen_shot("channel_list_opened")
        # Navigate to the first team's first channel
        general_channel = self.spaces_driver.wait_for_element("//div[@data-tid = 'team-channel-list']/..//li[contains(@id,'@thread.skype')]/a[.//span[contains(text(),'General')]]", self.XPATH, timeout=30)
        general_channel.click()
        # Wait for channel to open
        self.spaces_driver.wait_for_element(locator=str("//h2[@data-tid = 'messagesHeader-Title' and . = '{0}']".format("General")), locator_type=self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.spaces_driver.take_screen_shot("general_channel_opened")

    def navigate_back_to_call(self):
        logging.info("Navigation back to call...")
        calling_monitor = self.spaces_driver.wait_for_element(self.CHANNEL_CONVERSATION_CALL_MONITOR_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.wait_for_seconds(1)
        calling_monitor.click()

    def check_myself_video(self, timeout=LOADING_TIMEOUT, fail_on_not_found=True):
        self.spaces_driver.wait_for_element(self.CALLING_MYSELF_VIDEO_XPATH, self.XPATH, timeout=timeout, fail_on_not_found=fail_on_not_found)
        logging.info("Expanded myself video is expected to be shown on stage")
        self.spaces_driver.take_screen_shot("Calling_myself_video")

    def check_myself_collapsed_video(self, timeout=LOADING_TIMEOUT):
        logging.info("Checking Small Calling Myself Video")
        self.spaces_driver.wait_for_visible(self.CALLING_MYSELF_VIDEO_XPATH_COLLAPSED, self.XPATH, timeout=timeout)
        logging.info("Calling Myself Video Collapsed is present on the page")
        self.spaces_driver.take_screen_shot("Calling_myself_video_collapsed")

    def check_myself_expanded_video(self, timeout=LOADING_TIMEOUT):
        logging.info("Checking Big Calling Myself Video")
        self.spaces_driver.wait_for_visible(self.CALLING_MYSELF_VIDEO_XPATH_EXPANDED, self.XPATH, timeout=timeout)
        logging.info("Calling Myself Video Expanded is present on the page")
        self.spaces_driver.take_screen_shot("Calling_myself_video_expanded")

    def check_calling_timer(self, timeout=LOADING_TIMEOUT):
        logging.info("Checking Calling Screen Duration Timer")
        self.spaces_driver.wait_for_visible(self.CALLING_SCREEN_DURATION_TIMER, self.XPATH, timeout=timeout)
        logging.info("Calling Screen Duration Timer is present on the page")
        self.spaces_driver.take_screen_shot("Calling_screen_duration_timer")

    def check_myself_avatar(self, timeout=LOADING_TIMEOUT, fail_on_not_found = True):
        self.spaces_driver.wait_for_element(self.CALLING_MYSELF_AVATAR_XPATH, self.XPATH, timeout=timeout, fail_on_not_found=fail_on_not_found)
        logging.info("Myself avatar is expected to be shown on stage")
        self.spaces_driver.take_screen_shot("Calling_myself_avatar")

    def is_in_call(self):
        logging.info("Checking if user is in call")

        if self.spaces_driver.is_element_present(self.CALLING_SCREEN_XPATH, self.XPATH, 15):
            self.spaces_driver.take_screen_shot("is_in_call")
            logging.info("User is in call")
            return True
        self.spaces_driver.take_screen_shot("not_in_call")
        return False

    def check_if_in_call(self):
        """
        Checks if user is in a call
        :return:
        """
        logging.info("Checking if user is in call.")

        if self.is_in_call():
            logging.info("User is in a call.")
        else:
            logging.info("User is not in call")
            raise Exception("User is not in call")

    def wait_for_participant_to_appear_in_call(self, participant_email, group_call=False, timeout=CALLING_TIMEOUT):
        logging.info("wait_for_participant_to_appear_in_call checking participant = '{0}'".format(participant_email))
        self.ongoing_call_make_sure_video_is_on()

        if group_call:
            logging.info("Waiting for %s to appear in group call.." % participant_email)
            participant_avatar = self.CALLING_SCREEN_GROUP_CALL_PARTICIPANT_AVATAR_XPATH_TEMPLATE % participant_email
        else:
            logging.info("Waiting for %s to appear in call.." % participant_email)
            participant_avatar = self.CALLING_SCREEN_PARTICIPANT_AVATAR_XPATH_TEMPLATE % participant_email
        self.spaces_driver.take_screen_shot("participant_to_join_call")
        self.spaces_driver.wait_for_element(participant_avatar, self.XPATH, timeout=timeout)
        logging.info("Participant %s appeared in a call" % participant_email)
        self.spaces_driver.take_screen_shot("participant_joined_call")
        self.wait_for_seconds(3)

    def wait_for_participant_to_start_screen_share(self, participant_email):
        logging.info("Waiting for %s to start screen share" % participant_email)
        participant_screen_share = self.CALLING_SCREEN_PARTICIPANT_SHARING_SCREEN_AVATAR_XPATH_TEMPLATE % participant_email
        self.spaces_driver.take_screen_shot("participant_to_start_screen_share")
        self.spaces_driver.wait_for_element(participant_screen_share, self.XPATH, timeout=self.LOADING_TIMEOUT)
        logging.info("Participant %s started screen share" % participant_email)
        self.spaces_driver.take_screen_shot("participant_to_started_screen_share")
        self.wait_for_seconds(3)

    def wait_for_participant_to_leave_a_call(self, participant_email, timeout=LEAVE_TIMEOUT):
        logging.info("Waiting for %s to leave a call.." % participant_email)
        participant_avatar = self.CALLING_SCREEN_PARTICIPANT_AVATAR_XPATH_TEMPLATE % participant_email
        self.spaces_driver.take_screen_shot("participant_to_leave_call")
        attempt = 0
        while self.spaces_driver.is_element_present(locator=participant_avatar, locator_type=self.XPATH, timeout=5) and attempt < timeout:
            attempt += 1
            self.wait_for_seconds(5)

        if self.spaces_driver.is_element_present(locator=participant_avatar, locator_type=self.XPATH, timeout=5):
            self.spaces_driver.take_screen_shot("participant_not_left_call")
            logging.info("Participant %s has not left a call within dedicated time." % participant_email)
            raise Exception("Participant %s has not left a call within dedicated time." % participant_email)
        else:
            logging.info("Participant %s has left a call" % participant_email)
            self.spaces_driver.take_screen_shot("participant_left_call")

    def wait_until_number_of_participants_in_call(self, count, group_call=False, timeout=CALLING_TIMEOUT, fail_on_timeout=False, special_fix_to_reinvite_calee=False):

        if group_call:
            elem = self.CALLING_SCREEN_GROUP_CALL_PARTICIPANT_AVATAR_XPATH_ENTRY
            logging.info("Waiting for %d participants to join a group call" % count)
        else:
            elem = self.CALLING_SCREEN_PARTICIPANT_AVATAR_XPATH_ENTRY
            logging.info("Waiting for %d participants to join a call" % count)
        attempt = 0

        while attempt < timeout:
            self.wait_for_seconds(1)
            attempt += 1
            actual_count = len(self.spaces_driver.driver.find_elements_by_xpath(elem))

            if actual_count == count:
                logging.info("Attempt #%d: %d participants successfully on a call" % (attempt, actual_count))
                self.spaces_driver.take_screen_shot("%d_people_in_call" % actual_count)
                return
            else:
                logging.info("Attempt #%d: %d participants joined out of %d" % (attempt, actual_count, count))
        self.spaces_driver.take_screen_shot("%d_people_not_in_call" % count)

        if fail_on_timeout:
            logging.info("Wait timed out for %d participants to join a call" % count)
            raise Exception("Wait timed out for %d participants to join a call" % count)
        else:
            logging.info("Wait timed out for %d participants to join a call" % count)

        if special_fix_to_reinvite_calee:
            # Special testing fix for xp group call test execution failure
            self.reinvite_participant_from_calling_screen()

    def reinvite_participant_from_calling_screen(self):
        logging.info("Attempting to resend group call invitation for callee")
        self.spaces_driver.take_screen_shot("reinvite_group_call_invitation_for_callee")

        if self.spaces_driver.is_element_present(self.CALLING_SCREEN_ADD_PARTICIPANT_BUTTON_XPATH):
            logging.info("Add Participants button was present")
            self.spaces_driver.take_screen_shot("resend_group_call_invitation_for_callee_Add_button_is_present")

            self.spaces_driver.move_mouse_to_element(self.CALLING_SCREEN_ADD_PARTICIPANT_BUTTON_XPATH)
            logging.info("Moved to element Add Participants button")
            self.spaces_driver.take_screen_shot("Moved_to_element_Add_Participants_button")

            expand_add_attendee_btn = self.spaces_driver.wait_for_element(self.CALLING_SCREEN_ADD_PARTICIPANT_BUTTON_XPATH)
            expand_add_attendee_btn.click()
            logging.info("Clicked on element Add Participants button")
            self.spaces_driver.take_screen_shot("Clicked_on_element_Add_Participants_button")

        self.spaces_driver.take_screen_shot("pre_synchro_check")
        self.wait_for_seconds(3)
        self.spaces_driver.take_screen_shot("post_synchro_check")

        if len(self.spaces_driver.driver.find_elements_by_xpath(self.CALLING_SCREEN_ADD_PARTICIPANT_INVITE_OTHERS_FROM_CONV_ALL_ENTRIES)) > 0:
            logging.info("Count was : %d" % len(self.spaces_driver.driver.find_elements_by_xpath(self.CALLING_SCREEN_ADD_PARTICIPANT_INVITE_OTHERS_FROM_CONV_ALL_ENTRIES)))
            self.spaces_driver.take_screen_shot("Count_was_synchro_check")

            elements = self.spaces_driver.driver.find_elements_by_xpath(self.CALLING_SCREEN_ADD_PARTICIPANT_INVITE_OTHERS_FROM_CONV_ALL_ENTRIES)
            counter = 0
            for element in elements:
                counter = counter + 1

                logging.info("Element num %d" % counter)
                self.spaces_driver.take_screen_shot("Element_num_%d" % counter)

                element.is_displayed()
                element.click()

                logging.info("Element num %d clicked" % counter)
                self.spaces_driver.take_screen_shot("Element_num_%d_clicked" % counter)

    def wait_until_number_of_participants_in_channel_calling_header(self, initiator_email, count, timeout=CALLING_TIMEOUT, fail_on_timeout=True, step=1):
        logging.info("Waiting for number '{0}' of participants in the channel calling live roster".format(count))
        attempt = 0

        calling_live_roster_number_of_entries = self.CHANNEL_CALLING_LIVE_ROSTER_FOR_MEETUP_XPATH_TEMPLATE + XPathBuilder.xpath_locator_has_child(element="img", attribute="pl-upn", value=initiator_email, use_contains=False) + "//img"
        logging.info("XPATH for calling_live_roster = '{0}'".format(calling_live_roster_number_of_entries))

        while attempt < timeout:
            self.wait_for_seconds(step)
            attempt += step
            list_of_web_elements = self.spaces_driver.get_all_present_web_elements(calling_live_roster_number_of_entries)
            actual_count = len(list_of_web_elements)

            for web_element in list_of_web_elements:
                self.spaces_driver.take_screen_shot("wait_for_people_in_calling_header")
                logging.info("Attempt '{0}' to check '{1}'".format(attempt, web_element.is_displayed()))
                web_element.is_displayed()

                if actual_count != count:
                    logging.info("WARNING - Wrong number of participants in calling-live_roster!!!!")
                    logging.info("actual_count != count || {0} != {1}".format(actual_count, count))
                elif actual_count == count:
                    return

        self.spaces_driver.take_screen_shot("wait_for_people_in_calling_live_roster_another_attempt")

        if fail_on_timeout:
            logging.info("Wait timed out for %d participants in channel calling header" % count)
            raise Exception("Wait timed out for %d participants in channel calling header" % count)
        else:
            logging.info("Wait timed out for %d participants in channel calling header" % count)
        pass

    def check(self):
        pass

    def wait_until_someone_appears_in_call(self, timeout=CALLING_TIMEOUT):
        logging.info("Waiting for someone to join a call..")
        self.spaces_driver.wait_for_visible(self.CALLING_SCREEN_PARTICIPANT_STREAM_XPATH, self.XPATH, timeout=timeout)

    def check_participant_in_call(self, participant_email):
        logging.info("Checking whether %s is in a call" % participant_email)
        participant_avatar = self.CALLING_SCREEN_SPECIFIC_PARTICIPANT_VISIBLE_STREAM_XPATH % participant_email
        logging.info("xpath = " + self.CALLING_SCREEN_SPECIFIC_PARTICIPANT_VISIBLE_STREAM_XPATH % participant_email)
        self.spaces_driver.take_screen_shot("is_participant_in_call")

        if self.spaces_driver.is_element_present(locator=participant_avatar, locator_type=self.XPATH):
            logging.info("Participant %s found in call" % participant_email)
            self.spaces_driver.take_screen_shot("participant_found_in_call")
            self.wait_for_seconds(3)
        else:
            self.spaces_driver.take_screen_shot("participant_not_found_in_call")
            logging.info("Participant %s not in a call" % participant_email)
            raise Exception("Participant %s not in a call" % participant_email)

    def get_jump_in_button_xpath(self, initiator_email):
        logging.info("get_jump_in_button_xpath")
        return self.CHANNEL_CONVERSATION_JUMP_IN_BUTTON_FOR_INITIATOR_SPECIFIED_XPATH_TEMPLATE % initiator_email

    def wait_for_jump_in_button_persistent_and_join(self, meetup_title, timeout=CALLING_TIMEOUT, attempts=6):
        """
        Waits for jump in button to appear in a channel persistent indicator
        :param attempts: 
        :param meetup_title: title of the meetup
        :param timeout: time to wait until jump in button appears in a channel
        Fails when jump in button not present within the timeout period
        """
        self.wait_for_channel_to_be_ready()
        logging.info("Waiting for Jump in button appear in persistent indicator with '%s' title..." % meetup_title)
        jump_in_xpath = self.CHANNEL_PERSISTENT_INDICATOR_JUMP_IN_BUTTON_XPATH % (meetup_title, meetup_title)

        if self.spaces_driver.is_element_present(self.CHANNEL_PERSISTENT_INDICATOR_MORE_BUTTON_XPATH, self.XPATH):
            more_button = self.spaces_driver.wait_for_element(self.CHANNEL_PERSISTENT_INDICATOR_MORE_BUTTON_XPATH, self.XPATH)
            logging.info("Clicking at more button in call persistent indicator")
            more_button.click()
        self.reload_channel_for_jump_in(jump_in_xpath)
        self.spaces_driver.wait_for_visible(jump_in_xpath, self.XPATH, timeout)
        jump_in_button = self.spaces_driver.wait_for_element(jump_in_xpath, self.XPATH, timeout)
        logging.info("Going to click on join button in persistent view")
        self.spaces_driver.take_screen_shot("jump-in_button_before_click_in_persistent_view")

        for i in range(1, attempts):
            try:
                logging.info("Attempt #%d:" % i)
                jump_in_button.click()
                self.wait_for_seconds(2)
                logging.info("  * join button clicked in persistent view")
                self.check_if_calling_supported()
                self.spaces_driver.wait_for_visible(self.CALLING_SCREEN_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
                logging.info("  * call is joined successfully.")
                self.spaces_driver.take_screen_shot("jump-in_clicked_ok_in_persistent_view")
                break
            except Exception as e:
                logging.info("  * join not successful via persistent view: \n Exception : \n %s \n" %e)
                self.wait_for_seconds(2)
        self.spaces_driver.wait_for_element(self.CALLING_SCREEN_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        self.wait_for_call_to_connect()

    def join_call_from_call_notification(self, is_meetup=True, audio_call=False, attempts=60):
        """
        Clicks at call join audio/video in call notification
        :param attempts: re-tries
        :param is_meetup: is it meetup true/ false
        :param audio_call: if specified, user clicks at join with audio button
        :return:
        """
        elem = self.CALL_NOTIFICATION_ACCEPT_CALL_VIDEO_BUTTON_XPATH
        if is_meetup:
            logging.info("Going to jump in to the meetup from call notification")
            elem = self.CALL_NOTIFICATION_JUMP_IN_CALL_BUTTON_XPATH
        else:
            if audio_call:
                elem = self.CALL_NOTIFICATION_ACCEPT_CALL_AUDIO_BUTTON_XPATH
                logging.info("Going to join a audio call from call notification")
            else:
                logging.info("Going to join a video call from call notification")
        i=0
        for i in range(1, attempts):
            i += 1
            logging.info("{0} retries to focus call notification".format(i))
            self.wait_for_seconds(0.5)
            if self.is_focused_call_notification_window():
                try:
                    self.wait_for_seconds(0.5)
                    logging.info("is element from call notification visible ?")
                    logging.info("Window Handle : '{0}'".format(self.spaces_driver.driver.current_window_handle))
                    logging.info("Number of Handlers : '{0}'".format(len(self.spaces_driver.driver.window_handles)))
                    if self.spaces_driver.is_element_present(locator=elem, locator_type=self.XPATH, timeout=1):
                        logging.info("Clicking at join button in call notification")
                        join_button = self.spaces_driver.wait_for_element(locator=elem, locator_type=self.XPATH, timeout=1)
                        join_button.click()
                    else:
                        logging.info("notification not displayed")
                except Exception, e:
                    logging.info("'{0}'".format(str(e)))
            else:
                logging.info("attempt {0} to lock on call notification failed".format(i))
        self.focus_spaces_app()
        self.spaces_driver.wait_for_element(self.CALLING_SCREEN_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)

    def reject_call_from_call_notification(self):
        """
        Clicks at call reject button in call notification
        pre-condition: call notification is displayed
        :return:
        """
        logging.info("Going to reject call from call notification")
        self.focus_call_notification_window()
        reject_button = self.spaces_driver.wait_for_element(self.CALL_NOTIFICATION_REJECT_CALL_BUTTON_XPATH, self.XPATH, timeout=self.LOADING_TIMEOUT)
        reject_button.click()
        logging.info("Call rejected from call notification")
        self.focus_spaces_app()

    def wait_and_find_join_call_button(self, audio_only=False, timeout=CALLING_TIMEOUT):
        """
        Waits for join call button to appear in opened 1:1 chat
        :param audio_only: wait for video join or audio join button
        :param timeout: wait timeout

        Fails when join call button is not present within the timeout period
        """
        button_xpath = self.CHAT_VIDEO_CALL_JOIN_BUTTON_XPATH
        if audio_only:
            button_xpath = self.CHAT_AUDIO_CALL_JOIN_BUTTON_XPATH
        logging.info("Waiting for join call button in 1:1 chat")
        self.spaces_driver.take_screen_shot("wait_for_join_call_button")
        join_button = self.spaces_driver.wait_for_visible(locator=button_xpath, locator_type=self.XPATH, timeout=timeout)
        self.spaces_driver.take_screen_shot("join_call_button_found")
        return join_button

    def wait_and_find_reject_call_button(self, timeout=CALLING_TIMEOUT):
        """
        Waits for reject call button to appear in opened 1:1 chat
        :param timeout: wait timeout

        Fails when reject call button is not present within the timeout period
        """
        button_xpath = self.CHAT_VIDEO_CALL_REJECT_BUTTON_XPATH
        logging.info("Waiting for reject call button in 1:1 chat")
        self.spaces_driver.take_screen_shot("wait_for_reject_call_button")
        self.spaces_driver.wait_for_visible(locator=button_xpath, locator_type=self.XPATH, timeout=timeout)
        self.spaces_driver.take_screen_shot("reject_call_button_found")
        return self.spaces_driver.driver.find_element_by_xpath(button_xpath)

    def wait_for_jump_in_button_by_call_id(self, call_id, timeout=CALLING_TIMEOUT, scroll_down=True):
        """
        Waits for jump in button to appear by call ID
        :param scroll_down: scroll down
        :param call_id:
        :param timeout:
        :return:
        """
        self.wait_for_channel_to_be_ready()
        logging.info("Waiting for Meetup Started with expected call ID: %s" % call_id)
        self.spaces_driver.wait_for_element(self.CHANNEL_CONVERSATION_CALL_STARTED_IN_PROGRESS_MESSAGE_TEMPLATE % call_id, self.XPATH, timeout=timeout)
        logging.info("Waiting for Join button to appear for call ID: %s" % call_id)
        self.spaces_driver.wait_for_element(self.CHANNEL_CONVERSATION_JOIN_BUTTON_BY_CALL_ID_TEMPLATE % call_id, self.XPATH, timeout=timeout)

        if scroll_down:
            # self.channel_scroll_up_down(scroll_down=scroll_down)
            self.scroll_channel_to_specified_element_by_xpath(self.CHANNEL_CONVERSATION_JOIN_BUTTON_BY_CALL_ID_TEMPLATE % call_id)

    def reload_channel_for_jump_in(self, jump_in_xpath):
        logging.info("reload_channel_for_jump_in")

        if not self.spaces_driver.is_element_present(jump_in_xpath, self.XPATH):
            logging.info("jump_in_xpath is not visible going to load chat pannel then back to teams chat")
            chat_menu_button = self.spaces_driver.wait_for_element(self.APP_BAR_CHAT_BUTTON_XPATH, self.XPATH)
            teams_menu_button = self.spaces_driver.wait_for_element(self.APP_BAR_TEAMS_BUTTON_XPATH, self.XPATH)
            chat_menu_button.click()
            self.spaces_driver.wait_for_visible("//left-rail[@data-tid='left-rail'][contains(@ng-if,'isLoaded')]", self.XPATH)
            teams_menu_button.click()
            # Scrolling up
            self.channel_scroll_up_down(False)
            self.channel_scroll_up_down(False)

    def wait_for_jump_in_button(self, initiator_email, timeout=CALLING_TIMEOUT, scroll_down=True):
        """
        Waits for jump in button to appear in a channel for a call initiated by specified user
        :param scroll_down: scroll down 
        :param initiator_email: initiator username (email)
        :param timeout: time to wait until jump in button appears in a channel
        Fails when jump in button not present within the timeout period
        """
        self.wait_for_channel_to_be_ready()
        jump_in_xpath = self.get_jump_in_button_xpath(initiator_email=initiator_email)
        self.reload_channel_for_jump_in(jump_in_xpath)
        logging.info("Waiting for join button to appear (call created by %s)" % initiator_email)
        self.spaces_driver.take_screen_shot("wait_for_jump-in_button")
        self.spaces_driver.wait_for_element(locator=jump_in_xpath, locator_type=self.XPATH, timeout=timeout)
        self.wait_for_seconds(1)
        self.spaces_driver.wait_for_visible(locator=jump_in_xpath, locator_type=self.XPATH, timeout=timeout)
        if scroll_down:
            self.scroll_channel_to_specified_element_by_xpath(jump_in_xpath)
            self.wait_for_seconds(1)
        else:
            self.channel_scroll_up_down(scroll_down=False)
        self.spaces_driver.take_screen_shot("jump-in_button_found")

    def wait_for_join_call_button_and_join_call(self, audio_only=False, timeout=CALLING_TIMEOUT):
        """
        Waits until join call button appears in the opened 1:1 chat, then clicks at it
        :param timeout: timeout
        :param audio_only: if audio or video call join
        :return:
        """
        logging.info("Waiting for join 1:1 call button to appear.")
        self.spaces_driver.take_screen_shot("join_call_waiting")
        join_button = self.wait_and_find_join_call_button(audio_only=audio_only, timeout=timeout)
        join_button.click()
        self.spaces_driver.wait_for_element(self.CALLING_SCREEN_XPATH, self.XPATH, timeout=timeout)
        self.spaces_driver.take_screen_shot("call_joined")
        self.wait_for_call_to_connect()

    def wait_for_join_call_button_and_reject_call(self, timeout=CALLING_TIMEOUT):
        """
        Waits until join call button appears in the opened 1:1 chat, then clicks at call reject
        :return:
        """
        logging.info("Waiting for refuse 1:1 call button to appear.")
        self.spaces_driver.take_screen_shot("reject_call_waiting")
        reject_button = self.wait_and_find_reject_call_button(timeout=timeout)
        reject_button.click()
        self.spaces_driver.take_screen_shot("call_rejected")

    def wait_for_join_button_and_join_call(self, call_id, attempts=5, scroll_down=True, reply_chain=False, timeout=CALLING_TIMEOUT):
        """
        Waits for join button to appear in a channel for specified call by call ID
        :param reply_chain: reply chain
        :param attempts: number of retries
        :param call_id: call to wait for
        :param scroll_down: scroll down to join button when found
        :param timeout: time to wait before failing in seconds
        :return:
        """
        logging.info("Waiting for Meetup Started with expected call ID: %s" % call_id)
        self.spaces_driver.wait_for_element(self.CHANNEL_CONVERSATION_CALL_STARTED_IN_PROGRESS_MESSAGE_TEMPLATE % call_id, self.XPATH, timeout=timeout)
        if reply_chain:
            logging.info("Clicking at join button in reply chain")
            join_button = self.CHANNEL_REPLY_CHAIN_JOIN_BUTTON_BY_CALL_ID_TEMPLATE % call_id
        else:
            logging.info("Clicking at join button")
            join_button = self.CHANNEL_CONVERSATION_JOIN_BUTTON_BY_CALL_ID_TEMPLATE % call_id
        self.spaces_driver.take_screen_shot("join_button_before_click")
        self.spaces_driver.wait_for_visible(locator=join_button, locator_type=self.XPATH, timeout=timeout)
        for i in range(1, attempts):
            try:
                logging.info("Attempt #%d:" % i)
                join_btn = self.spaces_driver.wait_for_element(join_button, self.XPATH, timeout=timeout)
                if scroll_down:
                    self.scroll_channel_to_specified_element_by_xpath(join_button)
                join_btn.click()
                self.wait_for_seconds(2)
                logging.info("  * join button clicked")
                self.check_if_calling_supported()
                self.spaces_driver.wait_for_visible(self.CALLING_SCREEN_XPATH, self.XPATH, timeout=timeout)
                logging.info("  * call is joined successfully.")
                self.spaces_driver.take_screen_shot("jump-in_clicked_ok")
                break
            except Exception as e:
                logging.info("  * join not successful due Exception : {0}".format(e))
                logging.info(" Reloading the channel ")
                self.navigate_to_chat_section()
                self.navigate_to_channel()
                self.spaces_driver.wait_for_element(self.CHANNEL_CONVERSATION_CALL_STARTED_IN_PROGRESS_MESSAGE_TEMPLATE % call_id, self.XPATH, timeout=timeout)
            self.wait_for_seconds(2)
        self.spaces_driver.wait_for_element(self.CALLING_SCREEN_XPATH, self.XPATH, timeout=timeout)
        self.wait_for_call_to_connect()

    def wait_for_jump_in_button_and_join_call(self, initiator_email, attempts=5, timeout=CALLING_TIMEOUT, scroll_down=True):
        """
        Waits until call in progress header appears in a channel, then clicks at Jump-in button
        :param scroll_down: scrolling
        :param timeout: timeout
        :param attempts: retries
        :param initiator_email: mandatory
        :return:
        """
        jump_in_xpath = self.get_jump_in_button_xpath(initiator_email=initiator_email)
        self.wait_for_channel_to_be_ready()
        self.wait_for_jump_in_button(initiator_email=initiator_email, timeout=timeout, scroll_down=scroll_down)
        jump_in_button = self.spaces_driver.wait_for_element(jump_in_xpath, self.XPATH, timeout=timeout)
        logging.info("Clicking at join button")
        self.spaces_driver.take_screen_shot("jump-in_button_before_click")

        for i in range(1, attempts):

            try:
                logging.info("Attempt #%d:" % i)
                jump_in_button.click()
                self.wait_for_seconds(2)
                logging.info("  * join button clicked")
                self.check_if_calling_supported()
                self.spaces_driver.wait_for_visible(self.CALLING_SCREEN_XPATH, self.XPATH, timeout=3)
                logging.info("  * call is joined successfully.")
                self.spaces_driver.take_screen_shot("jump-in_clicked_ok")
                break
            except Exception as e:
                logging.info("  * join not successful: \n Exception : \n %s \n" %e)
            self.wait_for_seconds(2)
        self.spaces_driver.wait_for_element(self.CALLING_SCREEN_XPATH, self.XPATH, timeout=10)

    def is_displayed_meetup_ended_message(self, meetup_name, participants_emails):
        self.spaces_driver.wait_for_element(XPathBuilder.xpath_meetup_ended_message_calling_roster_contains_multiple_participants(meetup_name, participants_emails), self.XPATH, 5)

    def generate_meetup_title(self, meetup_name="Automation "):
        meetup_name += self.generate_string(10)
        logging.info("New Generated Meetup Name will be  -> '" + meetup_name + "'")
        return meetup_name

    def check_tab_order_calling_screen(self, click_to_start_elem=False):
        # logging.info("Checking TAB order on calling screen")
        logging.info("Checking TAB order on calling screen")
        self.accessibility.check_tab_order(self.TAB_ORDERS["calling_screen"], start_elem=self.CALLING_SCREEN_XPATH, click_to_start_elem=click_to_start_elem, ignore_missing_elem=True)

    def write_to_run_log(self, msg, log_type="info"):
        logging.info(msg)

    def get_console_logs(self, filenames=["console_logs.txt", "web_logs.txt"], log_type=["ALL"]):
        # errors = []
        # warnings = []
        # infos = []
        # severes = []
        if not self.show_console_logs:
            return
        failure = False
        failure_reason = None

        try:
            log_events = self.get_all_log_events()
        except Exception, e:
            logging.info(" \n Exception : \n %s \n" %e)
            log_events = "ERROR GETTING WEB LOGS:\n\n%s" %e
            failure = True
            failure_reason = e

        # Dump web logs
        f = open(os.path.join(self.sys.lib.logs_dir, filenames[1]), 'w')
        f.write(log_events)
        f.close()
        f = open(os.path.join(self.sys.lib.logs_dir, filenames[0]), 'w')
        f.write("\nConsole logs:\n==============\n\n")

        for entry in self.spaces_driver.driver.get_log("browser"):

            if "ALL" in log_type:
                f.write(str(entry))
                f.write("\n\n")
            else:

                if "ERROR" in log_type and "ERROR" in entry.values():
                    f.write(str(entry))
                    f.write("\n\n")

                elif "WARNING" in log_type and "WARNING" in entry.values():
                    f.write(str(entry))
                    f.write("\n\n")

                elif "INFO" in log_type and "INFO" in entry.values():
                    f.write(str(entry))
                    f.write("\n\n")

                elif "SEVERE" in log_type and "SEVERE" in entry.values():
                    f.write(str(entry))
                    f.write("\n\n")
        f.write("========== logs end ===========")
        f.close()

        if failure:
            raise Exception(failure_reason)

    def compute_measurement(self, measure_start, measure_end, measure_desc="Measurement time: "):
        """
        Computes measurement from start time to end time and prints it to the log
        :type measure_end: object
        :param measure_start: object
        :param measure_desc: description to be printed to the logs
        :return:
        """
        if not measure_start or not measure_end:
            return
        time_interval = measure_end - measure_start
        logging.info("Start time: %s ; End time: %s" % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(measure_start)), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(measure_end))))
        logging.info("<MEASURE COUNTER> " + measure_desc + str(time_interval) + " sec")

    def app_cleanup(self):
        logging.info("Starting app clean-up")
        # Dump page source
        try:
            logging.info("Last opened URL was: %s" % self.spaces_driver.driver.current_url)
            self.spaces_driver.dump_html_for_actual_page()
        except Exception, e:
            logging.error("Error while dumping page source: \n %s \n" % e)
            logging.info("Error while dumping page source: \n %s \n" % e)

        try:
            # Make screen shot
            self.spaces_driver.take_screen_shot("cleanup")
            self.stop_video_recording()
        except Exception, e:
            logging.error("Exception while taking screen shot: \n %s \n" % e)
            logging.info("Exception while taking screen shot: \n %s \n" % e)

        try:
            # Save electron console logs
            self.get_console_logs()
            self.sys.lib.get_logs()
        except Exception, e:
            logging.error("Exception while getting console logs: \n %s \n" % e)
            logging.info("Exception while getting console logs: \n %s \n" % e)

        # Always try to hang-up every ongoing call before exit
        try:
            logging.info("Hanging-up a call")
            self.hang_up_ongoing_call(by_js=True)
        except Exception, e:
            logging.error("Seems no call in progress. Nothing to hang-up. \n Exception : \n %s \n" %e)
            logging.info("Seems no call in progress. Nothing to hang-up. \n Exception : \n %s \n" %e)
        logging.info("App cleanup done")

    def test_passed(self, customPassText= "TEST PASSED"):
        logging.info("\n*--------------*\n|| {0} ||\n|| {0} ||\n|| {0} ||\n|| {0} ||\n|| {0} ||\n|| {0} ||\n|| {0} ||\n|| {0}||\n*--------------*\n".format(customPassText))

    def _cleanup(self):
        logging.info("Starting test clean-up")
        self.app_cleanup()
        # Return test users back to APM pool if needed
        self.test_config.release_apm_test_users_back_to_pool()
        try:
            self.spaces_driver.kill_app()
        except Exception, e:
            logging.error("Exception while killing the app \n Exception : \n %s \n" %e)

        if not self.is_local:
            self.sys.lib.uninstall_skypespaces()
        logging.info("Cleanup done")
