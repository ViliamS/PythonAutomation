# -*- coding: utf-8 -*-
import os
import time
import subprocess
import logging
import selenium.webdriver as webdriver

from xpath import XPathBuilder
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, WebDriverException, StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains as ac

from common_lib import CommonLib as common

class ElementNotFoundException(Exception):
    pass


class PageNotLoadedException(Exception):
    pass


class SpacesWebDriver(object):
    """
    WebDriver documentation: http://selenium-python.readthedocs.org/en/latest/api.html
    """
    ELECTRON_ARGS = ['--ignore-gpu-blacklist', '--disablesso']
    ENABLE_SLIMCORE_ARG = '--enableslimcore'
    DISABLE_SLIMCORE_ARG = '--disableslimcore'

    SLEEP_TIME = 2
    PAGE_TIMEOUT = 60
    ELEMENT_TIMEOUT = 90
    ELEMENT_NOT_PRESENT_TIMEOUT=5
    CONDITION_TIMEOUT = 30
    CHROMEDRIVER_PORT = "9515"
    CHROMEDRIVER_PID = None
    SCREENSHOTS_ENABLED = False
    MAXIMIZE_BROWSER_WINDOW = True

    keys = Keys
    driver = None

    def __init__(self, skypespaces_bin, driver_bin, run_mode, system_lib, enable_slimcore=False, retries=5):
        logging.info("__init___ \n skypespaces_bin = '{0}' \n driver_bin = '{1}' \n run_mode = '{2}' \n system_lib = '{3}' \n enable_slimcore == '{4}' \n retries == '{5}'".format(skypespaces_bin, driver_bin, run_mode, system_lib, enable_slimcore, retries))
        self.print_selenium_version()
        self.driver_bin = driver_bin
        self.driver = None
        self.sys = system_lib
        self.run_mode = run_mode
        if not self.is_desktop_run():
            logging.info("This is web test, launching a browser")
            logging.info("===================================")
            self.init_browser(run_mode)
            self.actions = ac(self.driver)
        else:
            if enable_slimcore:
                logging.info("Enabling Slim Core in the app")
                self.ELECTRON_ARGS.append(self.ENABLE_SLIMCORE_ARG)
            else:
                logging.info("Disabling Slim Core in the app")
                self.ELECTRON_ARGS.append(self.DISABLE_SLIMCORE_ARG)
            logging.info("WebDriver launch and app inject")
            logging.info("===============================")
            logging.info("Injecting to app: " + skypespaces_bin)
            logging.info("Using app arguments:")
            for arg in self.ELECTRON_ARGS:
                logging.info("   %s" % arg)
            logging.info("Going to attach webdriver to the app: %s" % skypespaces_bin)
            for attempt in range(0, retries):
                logging.info("\nAttempt #%d\n" % attempt)
                try:
                    logging.info("Going to attach webdriver to the app: %s" % skypespaces_bin)
                    self.sys.lib.kill_chromedriver()
                    opts = webdriver.ChromeOptions()
                    opts.binary_location = skypespaces_bin
                    for arg in self.ELECTRON_ARGS:
                        opts.add_argument(arg)
                    # Enable verbose logging note that file must be present in declared location
                    #self.driver = webdriver.Chrome(executable_path=self.driver_bin, chrome_options=opts, service_args=["--verbose", "--log-path=C:\\Users\\v-vistro\\Desktop\\electronWebDriverLog.txt"])
                    self.driver = webdriver.Chrome(executable_path=self.driver_bin, chrome_options=opts)
                    logging.info("Chrome Webdriver attach finished.")
                except Exception, e:
                    logging.warning("WebDriver launch attempt #%d failed: %s" % (attempt, e))
                    self.sys.lib.terminate_app()
                    self.kill_app()
                    self.sys.lib.kill_chromedriver()
                    self.static_pause(5)
                    continue
                self.actions = ac(self.driver)
                return
            raise Exception("WebDriver could not be launched and injected")

    def is_desktop_run(self):
        logging.info("is_desktop_run")
        if self.run_mode == "electron":
            return True

        return False

    @staticmethod
    def print_selenium_version():
        logging.info("print_selenium_version")
        try:
            import selenium

            logging.info("SELENIUM VERSION: %s" % selenium.__version__)
            logging.info("SELENIUM PATH: %s" % selenium.__file__)

        except Exception, e:
            logging.error("Cannot detect selenium version: %s" % e)

    def launch_chromedriver(self):
        """
        Launches chromedriver server
        """
        logging.info("launch_chromedriver")
        import os
        stdout = os.popen("netstat -p tcp")
        logging.info(stdout.read())
        subprocess.Popen(["netstat", "-p tcp"])
        logging.info("Launching chromedriver (%s)" % self.CHROMEDRIVER_PATH)
        try:
            self.CHROMEDRIVER_PID = subprocess.Popen([self.CHROMEDRIVER_PATH, "--port=" + self.CHROMEDRIVER_PORT])
            time.sleep(10)
            logging.info("Chromedriver was launched successfully.")
        except Exception, e:
            logging.error("Not able to launch chromedriver due to %s" % e)

    def init_browser(self, run_mode):
        logging.info("init_browser")
        if not run_mode:
            logging.error("No browser specified")
            raise Exception("No browser specified")
        logging.info("Launching browser: %s" % run_mode)

        # THIS IS EDGE BROWSER RUN
        if run_mode == "edge":
            logging.info("Using Edge driver: %s" % self.driver_bin)

            self.driver = webdriver.Edge(self.driver_bin)

            logging.info("Edge browser init finished.")

        # THIS IS CHROME BROWSER RUN
        elif run_mode == "chrome":
            logging.info("Using Chrome driver: %s" % self.driver_bin)
            self.driver = webdriver.Chrome(self.driver_bin)

        # THIS IS FIREFOX BROWSER RUN
        elif run_mode == "firefox":
            self.driver = webdriver.Firefox()

        # THIS IS UNKNOWN BROWSER RUN
        else:
            raise Exception("%s browser not supported yet. Please add support." % run_mode)
        time.sleep(5)
        if self.MAXIMIZE_BROWSER_WINDOW:
            logging.info("Maximizing browser window")
            self.driver.maximize_window()
        logging.info("Deleting all the cookies.")
        try:
            self.driver.delete_all_cookies()
        except Exception, e:
            # EDGE ERROR: https://developer.microsoft.com/en-us/microsoft-edge/platform/issues/5751773/
            logging.error("Exception while deleting cookies: %s" % e)

    def kill_app(self):
        logging.info("kill_app")
        """
        Quits webdriver hooked up to the electron and kills chromedriver
        """
        if self.CHROMEDRIVER_PID:
            if self.driver:
                logging.info("Killing app.")
                self.driver.quit()
                self.CHROMEDRIVER_PID.kill()
        try:
            self.driver.quit()
        except:
            return

    def dump_html_for_actual_page(self, filename="dumped_page.html"):
        """
        Stores HTML source for the page opened
        :return:
        """
        logging.info("Dumping page source to %s" % file)
        html_source = self.driver.page_source
        f = open(os.path.join(self.sys.lib.logs_dir, filename), 'w')
        f.write(html_source.encode('utf-8'))
        f.close()
        logging.info("Done.")

    def move_mouse_to_element(self, elem):
        logging.info("move_mouse_to_element")
        try:
            self.actions.move_to_element(elem).perform()
            self.static_pause(0.5)
            return
        except StaleElementReferenceException, e:
            logging.info("StaleElementReferenceException was caught : {0}".format(e))
            self.static_pause(10)
            self.actions = ac(self.driver)
            self.actions.move_to_element(elem).perform()
            return

    def click_js(self, elem):
        logging.info("click_js")
        self.actions.move_to_element(elem).click().perform()

    @staticmethod
    def static_pause(time_to_wait=5):
        logging.info("static_pause - Waiting for '{0}' seconds".format(time_to_wait))
        time.sleep(time_to_wait)

    def wait_for_page_to_load(self, counter = 0):
        logging.info("wait_for_page_to_load")
        self.static_pause(1)
        counter += 1
        try:
            if not self.driver.current_url:
                logging.info("Internal url not detected!")
                return False
            logging.info("Waiting for page '{0}' to load.".format(self.driver.current_url))
            try:
                WebDriverWait(self.driver, self.ELEMENT_TIMEOUT).until(
                    lambda s: s.execute_script('return document.readyState;') == 'complete')
                logging.info("Page is loaded.")
            except TimeoutException:
                logging.info("Page didn't load in time: '{0}'".format(self.driver.current_url))
                #raise PageNotLoadedException("Page didn't load in time: {0}".format(self.driver.current_url))

        except NoSuchWindowException, e:
            logging.info("NoSuchWindowException was caught when we were asking for current URL \n '{0}'".format(e))
        return self.driver.execute_script('return document.readyState;')

    ##################################
    # My own Selenium implementation #
    ##################################

    def get_web_elements_by(self, locator, locator_type):
        logging.debug("get_web_elements_by || Locator : {0} || Locator Type : {1}".format(locator, locator_type))
        try:
            if locator_type is By.XPATH or "xpath" or "XPATH":
                web_elements = self.driver.find_elements_by_xpath(xpath=locator)
            elif locator_type is By.CSS_SELECTOR or "css" or "CSS":
                web_elements = self.driver.find_elements_by_css_selector(css_selector=locator)
            elif locator_type is By.ID or "id" or "ID":
                web_elements = self.driver.find_elements_by_id(id_=locator)
            elif locator_type is By.CLASS_NAME or "class" or "CLASS":
                web_elements = self.driver.find_elements(by=By.CLASS_NAME, value=locator)
            else:
                logging.error("ERROR - Wrong handler type specified: %s" % locator_type)
                raise Exception("ERROR - Wrong handler type specified: %s" % locator_type)
        except WebDriverException, e:
            logging.error("ERROR - Element NOT Found due WebDriverException = '{0}'".format(e))
            self.take_screen_shot("ERROR_ELEMENT_NOT_FOUND")
            raise WebDriverException(e)
        logging.debug("Returning list of web_elements successfully")
        return web_elements

    # For lower code duplicity
    def get_web_element_by(self, locator, locator_type):
        logging.info("get_web_element_by || Locator : {0} || Locator Type : {1}".format(locator, locator_type))
        try:
            if locator_type is By.XPATH or "xpath" or "XPATH":
                web_element = self.driver.find_element_by_xpath(xpath=locator)
            elif locator_type is By.CSS_SELECTOR or "css" or "CSS":
                web_element = self.driver.find_element_by_css_selector(css_selector=locator)
            elif locator_type is By.ID or "id" or "ID":
                web_element = self.driver.find_element_by_id(id_=locator)
            elif locator_type is By.CLASS_NAME or "class" or "CLASS":
                web_element = self.driver.find_element(by=By.CLASS_NAME, value=locator)
            else:
                logging.info("ERROR - Wrong handler type specified: %s" % locator_type)
                raise Exception("ERROR - Wrong handler type specified: %s" % locator_type)
        except WebDriverException, e:
            logging.info("ERROR - Element NOT Found due WebDriverException = '{0}'".format(e))
            self.take_screen_shot("ERROR_WebDriverException")
            raise WebDriverException(e)
        logging.info("Returning web_element successfully")
        return web_element

    def wait_for_element(self, locator, locator_type="xpath", timeout=ELEMENT_TIMEOUT, fail_on_not_found=True):
        logging.info("wait_for_element || Locator : '{0}' || Locator type : '{1}' ||  Timeout : {2}".format(locator, locator_type, timeout))
        web_element = None
        try:
            web_element = ec.presence_of_element_located(locator=(locator_type, locator))
        except Exception, e :
            logging.info("Warning exception e = '{0}'".format(str(e)))
            logging.info("Locator = '{0}' not found".format(locator))
        try:
            WebDriverWait(self.driver, timeout).until(ec.presence_of_element_located(locator=(locator_type, locator)))
        except TimeoutException or StaleElementReferenceException, e:
            logging.info("ERROR - Element is not present | Locator by ('{0}') = '{1}' Due to Exception".format(locator_type, locator))
            if fail_on_not_found:
                self.take_screen_shot("ERROR_ELEMENT_NOT_PRESENT")
                self.dump_html_for_actual_page("ERROR_wait_for_element_FAILED")
                logging.info("TEST FAILED - fail_on_not_found = was TRUE")
                if isinstance(e, TimeoutException):
                    raise TimeoutException(e)
                elif isinstance(e, StaleElementReferenceException):
                    raise StaleElementReferenceException(e)
                else:
                    raise Exception(e)
            else:
                logging.info("WARNING - Element is not present | Locator by ('{0}') = '{1}' Due to TimeoutException".format(locator_type, locator))
                self.take_screen_shot("WARNING_wait_for_element_FAILED")
                self.dump_html_for_actual_page("WARNING_wait_for_element_FAILED")
                return web_element
        logging.info("PASS || Element is present | Locator by ('{0}') = '{1}' ".format(locator_type, locator))
        element = self.get_web_element_by(locator=locator, locator_type=locator_type)
        return element

    def wait_for_element_visible(self, locator, locator_type="xpath", timeout=ELEMENT_TIMEOUT, fail_on_not_found=True):
        logging.info("wait_for_element_visible || Locator : '{0}' || Locator type : '{1}' ||  Timeout : {2}".format(locator, locator_type, timeout))
        element = None
        try:
            WebDriverWait(self.driver, timeout).until(ec.visibility_of_element_located(locator=(locator_type, locator)))
        except TimeoutException or StaleElementReferenceException, e:
            logging.info("ERROR - Element is NOT visible | Locator by ('{0}') = '{1}'".format(locator_type, locator))
            if fail_on_not_found:
                self.take_screen_shot("ERROR_wait_for_visible_FAILED")
                self.dump_html_for_actual_page("ERROR_wait_for_visible_FAILED")
                logging.info("TEST FAILED - fail_on_not_found = was TRUE")
                if isinstance(e, TimeoutException):
                    raise TimeoutException(e)
                elif isinstance(e, StaleElementReferenceException):
                    raise StaleElementReferenceException(e)
                else:
                    raise Exception(e)
            else:
                logging.info("WARNING - TEST CONTINUES due fail_on_not_found was 'FALSE' - for - Element is NOT present | Locator by ('{0}') = '{1}'".format(locator_type, locator))
                self.take_screen_shot("WARNING_wait_for_visible_FAILED")
                self.dump_html_for_actual_page("WARNING_wait_for_visible_FAILED")
                return element
        logging.info("PASS || Element is visible | Locator by ('{0}') = '{1}' ".format(locator_type, locator))
        element = self.get_web_element_by(locator=locator, locator_type=locator_type)
        return element

    def wait_for_visible(self, locator, locator_type="xpath", timeout=ELEMENT_TIMEOUT):
        return self.wait_for_element_visible(locator=locator, locator_type=locator_type, timeout=timeout, fail_on_not_found=True)

    def take_screen_shot(self, file_name=None):
        logging.info("take_screen_shot")
        if file_name is None:
            raise Exception("EXCEPTION - Not provided file_name for method take_screen_shot")
        else:
            return self.sys.lib.take_fullscreen_screenshot(file_name)

    def wait_for_element_not_present(self, locator, locator_type, timeout=ELEMENT_NOT_PRESENT_TIMEOUT):
        logging.debug("wait_for_element_not_present || Locator : '{0}' | Locator type : '{1}' | Timeout : '{2}'".format(locator, locator_type, timeout))
        return WebDriverWait(self.driver, timeout).until_not(ec.presence_of_element_located(locator=(locator_type, locator)))

    def wait_for_not_visible(self, locator, locator_type, timeout=ELEMENT_NOT_PRESENT_TIMEOUT):
        logging.debug("wait_for_not_visible || Locator : '{0}' | Locator type : '{1}' | Timeout : '{2}'".format(locator, locator_type, timeout))
        try:
            return WebDriverWait(self.driver, timeout).until_not(ec.visibility_of_element_located(locator=(locator_type, locator)))
        except Exception, e:
            logging.info("wait for not visible failed with exception {0}".format(e))
            self.take_screen_shot("Failed_wait_for_not_visible")
            return WebDriverWait(self.driver, 0).until_not(ec.visibility_of_element_located(locator=(locator_type, locator)))

    def is_element_visible(self, locator, locator_type, timeout=5):
        logging.info("is_element_visible || Locator : '{0}' | Locator type : '{1}' | Timeout : '{2}'".format(locator, locator_type, timeout))
        if not timeout == 0:
            timeout = timeout / 2
        if self.is_element_present(locator=locator, locator_type=locator_type, timeout=timeout):
            logging.info("Element is present in DOM")
            try:
                WebDriverWait(self.driver, timeout).until(ec.visibility_of_element_located(locator=(locator_type, locator)))
            except TimeoutException:
                logging.info("element was present but wasn't not visible")
                return False
            logging.info("Element is present and is also visible")
            return True
        elif not self.is_element_present(locator=locator, locator_type=locator_type, timeout=timeout):
            logging.info("element not present skipping visibility checking")
            return False

    def recall_is_element_present(self, locator, locator_type, timeout):
        logging.info("recall_is_element_present || Locator : '{0}' | Locator type : '{1}' | Timeout : '{2}'".format(str(locator), str(locator_type), timeout))
        logging.info("Setting web_driver_exception = True for is_element_present command")
        self.static_pause(20)
        return self.is_element_present(locator=locator, locator_type=locator_type, timeout=timeout, web_driver_exception=True)

    def is_element_present(self, locator, locator_type="id", timeout=5, web_driver_exception=False):
        logging.info("is_element_present || Locator : '{0}' | Locator type : '{1}' | Timeout : '{2}' | webDriverException : '{3}'".format(str(locator), str(locator_type), timeout, web_driver_exception))
        try:
            try:
                WebDriverWait(self.driver, timeout).until(ec.presence_of_element_located(locator=(locator_type, locator)))
            except TimeoutException or NoSuchWindowException:
                logging.info("element was NOT found returning FALSE")
                return False
            logging.info("element was found returning TRUE")
            return True
        except WebDriverException, a:
            logging.info("WebDriver Exception caught : '{0}'".format(a))
            self.take_screen_shot("ERROR_WebDriverException_caught")
            if web_driver_exception:
                logging.info("Web Driver still throwing Exception there is some problem")
                raise WebDriverException(a)
            logging.info("Is possible that page was not yet opened so re-attempting this command")
            return self.recall_is_element_present(locator=locator, locator_type=locator_type, timeout=timeout)

    # Those below are not tested properly
    def click_on_element(self, locator, locator_type=By.XPATH, timeout=ELEMENT_TIMEOUT):
        logging.info("click_on_element || Locator : '{0}' | Locator type : '{1}' | Timeout : '{2}'".format(locator, locator_type, timeout))
        try:
            element = self.wait_for_element(locator, locator_type, timeout)
        except TimeoutException, e:
            self.take_screen_shot("ERROR_TimeoutException")
            logging.info("ERROR - Element not Found TimeoutException")
            raise TimeoutException(e)
        return self.actions.move_to_element(element).click().perform()

    def is_text_visible(self, text, timeout=ELEMENT_NOT_PRESENT_TIMEOUT):
        return self.is_element_visible(locator=XPathBuilder.xpath_body_contains_text(text), locator_type=By.XPATH, timeout=timeout)

    def is_text_present(self, text, timeout=ELEMENT_NOT_PRESENT_TIMEOUT):
        return self.is_element_present(locator=XPathBuilder.xpath_body_contains_text(text), locator_type=By.XPATH, timeout=timeout)

    def wait_for_text(self, text, timeout=ELEMENT_TIMEOUT):
        logging.info("Waiting for text: " + text)
        return self.wait_for_visible(locator= XPathBuilder.xpath_body_contains_text(text), locator_type=By.XPATH, timeout=timeout)

    def is_text_present_in_input(self, msg, locator, locator_type=By.XPATH, timeout=ELEMENT_TIMEOUT):
        """
        Checks if specified message is present in DOM
        pre-condition: User is on the meetup and calling screen is opened
        :param timeout: timeout in seconds
        :param locator_type: locator type xpath/css/id
        :param locator: locator for targeting element 
        :param msg: username to add to the meetup
        :return: True/False
        """
        logging.info("is_text_present_in_input '{0}' present_in_input '{1}'".format(msg, locator))
        exact_locator = "{0}[.//*[text()='{1}']]".format(locator, msg)
        contains_locator = "{0}[.//*[contains(text(),'{1}')]]".format(locator, msg)
        logging.info("1st. exact_locator = '{0}'".format(exact_locator))
        logging.info("2nd. contains_locator = '{0}'".format(contains_locator))
        logging.info("3rd. using locator = '{0}'".format(XPathBuilder.xpath_body_contains_text(msg)))

        if self.is_element_present(locator=exact_locator, locator_type=locator_type, timeout=timeout):
            logging.info("1st Passed - Exact match of text {0} was present in application input box".format(msg))
            return True
        elif self.is_element_present(locator=contains_locator, locator_type=locator_type, timeout=timeout):
            logging.info("2nd Passed - Containing part of text '{0}' was present in application input box".format(msg))
            return True
        elif self.is_text_present(text=msg, timeout=timeout):
            logging.info("3rd Passed - text '{0}' was present in application ".format(msg))
            return True
        else:
            logging.warning("Text {0} not detected after waiting 3x '{1}'".format(msg, timeout))
            logging.info("Not detected by : \n 1st. exact_locator = {0} or \n 2nd. contains_locator = {1} \n or 3rd. using locator = '{2}'".format(exact_locator, contains_locator, XPathBuilder.xpath_body_contains_text(msg)))
            return False

    def get_all_present_web_elements(self, locator, locator_type, timeout=ELEMENT_TIMEOUT, fail_on_not_found=False):
        logging.info("get_all_present_web_elements for '{0}' '{1}'".format(locator, locator_type))
        elements = None
        try:
            WebDriverWait(self.driver, timeout).until(ec.presence_of_all_elements_located(locator=(locator_type, locator)))
        except TimeoutException, e:
            logging.info("ERROR - No matching elements were found | Locator by ('{0}') = '{1}'".format(locator_type, locator))
            if fail_on_not_found:
                self.take_screen_shot("ERROR_NO_MATCHING_ELEMENTS")
                logging.error("TEST FAILED - fail_on_not_found = was TRUE")
                raise TimeoutException(e)
            else:
                logging.info("WARNING - TEST CONTINUES due fail_on_not_found was 'FALSE' - for - even when no elements were found | Locator by ('{0}') = '{1}'".format(locator_type, locator))
                return elements
        logging.info("PASS || Some elements are present | Locator by ('{0}') = '{1}' ".format(locator_type, locator))
        elements = self.get_web_elements_by(locator=locator, locator_type=locator_type)
        return elements