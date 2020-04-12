# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By

import spacesdriver
import logging as log
import sys


class XPathBuilder(object):

    @staticmethod
    def xpath_meetup_ended_message_calling_roster_contains_multiple_participants(meetup_name, emails):
        return_xpath = spacesdriver.SkypeSpaces.CHANNEL_CONVERSATION_MEETUP_ENDED_XPATH_PARTICIPANT_LIST % meetup_name
        for email in emails:
            return_xpath += spacesdriver.SkypeSpaces.IMAGE_CONTAINS_EMAIL_ADDRESS % email
        log.info("{0}".format(return_xpath))
        return return_xpath

    @staticmethod
    def tuple_xpath_locator_type_body_contains_text(text):
        return By.XPATH, XPathBuilder.xpath_body_contains_text(text)

    @staticmethod
    def xpath_body_contains_text(text):
        log.info("//body[contains(., '{0}')]".format(text))
        return "//body[contains(., '{0}')]".format(text)

    @staticmethod
    def xpath_locator(element, attribute, value, use_contains=False):
        if attribute is "text" or "text()":
            if use_contains is True:
                log.info("//{0}[contains(text(),'{1}')]".format(element, value))
                return "//{0}[contains(text(),'{1}')]".format(element, value)
            elif use_contains is False:
                log.info("//{0}[text()='{1}']".format(element, value))
                return "//{0}[text()='{1}']".format(element, value)
        elif attribute is not "text" or "text()":
            if use_contains is False :
                log.info("//{0}[@{1}='{2}']".format(element, attribute, value))
                return "//{0}[@{1}='{2}']".format(element, attribute, value)
            elif use_contains is True :
                log.info("//{0}[contains(@{1},'{2}')]".format(element, attribute, value))
                return "//{0}[contains(@{1},'{2}')]".format(element, attribute, value)

    @staticmethod
    def xpath_equals_or_contains_attribute(element="div", attribute="text()", value=""):
        if attribute is "text" or "text()":
            log.info("//{0}[(text()='{1}') or contains(text(),'{2}')]".format(element, value, value))
            return "//{0}[(text()='{1}') or contains(text(),'{2}')]".format(element, value, value)
        log.info("//{0}[(@{1}='{2}') or contains(@{3},'{4}')]".format(element, attribute, value, attribute, value))
        return "//{0}[(@{1}='{2}') or contains(@{3},'{4}')]".format(element, attribute, value, attribute, value)

    @staticmethod
    def xpath_locator_has_child(element, attribute, value, use_contains=False):
        if attribute is "text" or "text()":
            if use_contains is True :
                log.info("[.//{0}[contains(text(),'{1}')]]".format(element, value))
                return "[.//{0}[contains(text(),'{1}')]]".format(element, value)
            elif use_contains is False :
                log.info("[.//{0}[text()='{1}']]".format(element, value))
                return "[.//{0}[text()='{1}']]".format(element, value)
        elif attribute is not "text" or "text()":
            if use_contains is True :
                log.info("[.//{0}[contains(@{1},'{2}')]]".format(element, attribute, value))
                return "[.//{0}[contains(@{1},'{2}')]]".format(element, attribute, value)
            elif use_contains is False :
                log.info("[.//{0}[@{1}='{2}']]".format(element, attribute, value))
                return "[.//{0}[@{1}='{2}']]".format(element, attribute, value)
