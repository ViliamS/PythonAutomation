# -*- coding: utf-8 -*-

from common_lib import CommonLib as common
import time
import logging

class Accessibility(object):

    FIND_ELEMENT_BY_XPATH_JS_TEMPLATE = "var %s = document.evaluate(\"%s\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
    FOCUS_ELEMENT_JS = "%s.focus();"

    def __init__(self, spaces_driver, platform_lib):
        logging.info("Initialising Accessibility layer")
        self.spaces_driver = spaces_driver
        self.sys = platform_lib

    def check_tab_order(self, tab_order_elem_list, start_elem=None, click_to_start_elem=False, ignore_missing_elem=False):
        """
        Checks TAB order for the opened page/view
        :param click_to_start_elem: 
        :param tab_order_elem_list: ordered list of the elements which represent TAB order
        :param start_elem: if specified, this element will be focused at the beginning of the check
        :param ignore_missing_elem: when specified, check will not fail if element from TAB order is not rendered on the view
        :return:
        """
        logging.info("Going to check TAB order for page %s" % self.spaces_driver.driver.current_url)
        self.sys.lib.take_fullscreen_screenshot("tab_order_check_start")

        if start_elem:
            logging.info("  - we need to focus element first: %s" % start_elem)

            if click_to_start_elem:
                logging.info("   - focusing start element by click.")
                elem = self.spaces_driver.driver.find_element_by_xpath(start_elem)
                elem.click()
            else:
                self.focus_element_by_xpath(start_elem)

        active_element = self.spaces_driver.driver.switch_to_active_element()
        logging.info("Checking %d items in TAB order" % len(tab_order_elem_list))
        i = 0

        for item in tab_order_elem_list:
            i += 1
            logging.info("   * %d: Element %s" % (i, item))

            try:
                elem = self.spaces_driver.driver.find_element_by_xpath(item)

                if not elem.is_displayed():
                    raise Exception("Element 'item' (xpath) is found but not visible")
            except Exception, e:
                logging.info("Specified element not found on the page: %s (%s)" % (item, e), "warning")

                if ignore_missing_elem:
                    logging.info("   - Skipping element.")
                    continue
                else:
                    raise Exception("Specified element not found on the page: %s" % item)

            if not active_element:
                raise Exception("Active element not detected")

            logging.info(" - hitting TAB")
            active_element.send_keys(self.spaces_driver.keys.TAB)
            time.sleep(0.5)
            logging.info(" - checking if element is focused")
            active_element = self.spaces_driver.driver.switch_to_active_element()
            self.sys.lib.take_fullscreen_screenshot("%d-tab_order_check" % i)

            if elem == active_element:
                logging.info(" - PASS")
            else:
                logging.info(" - FAIL: Wrong element focused (element with class='%s'). Should be element '%s'" % (active_element.get_attribute("class"), tab_order_elem_list[i - 1]))
                self.sys.lib.take_fullscreen_screenshot("tab_order_fail")
                raise Exception("TAB order not as desired")

    def focus_element_by_xpath(self, elem):
        """
        Focuses element specified by xpath using JS
        :param elem: xpath of the element
        :return:
        """
        logging.info("Going to focus element: %s" % elem)
        script_js = "%s %s" % (self.FIND_ELEMENT_BY_XPATH_JS_TEMPLATE % ("elemToFocus", elem), self.FOCUS_ELEMENT_JS % "elemToFocus")
        self.spaces_driver.driver.execute_script(script_js)
        time.sleep(0.5)
        logging.info("Done.")

    def send_keys_and_get_focused_element(self, elem, *keys):
        """
        send key(s) to an element
        :param elem: target element
        :return: element focused after the key (or key combination) was sent
        """
        logging.info("send_keys_and_get_focused_element CSS class = '%s'" % (elem.get_attribute("class")))
        elem.send_keys(*keys)
        time.sleep(0.5)
        try:
            logging.info("self.spaces_driver.driver.switch_to.active_element")
            return self.spaces_driver.driver.switch_to.active_element
        except Exception, e:
            logging.error(e)
            logging.info("failed on 'return self.spaces_driver.driver.active_element()' fallback to deprecated 'return self.spaces_driver.driver.switch_to_active_element()'")
            return self.spaces_driver.driver.switch_to_active_element()