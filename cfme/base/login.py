from widgetastic.exceptions import NoSuchElementException
from widgetastic.widget import View
from widgetastic_patternfly import NavDropdown, VerticalNavigation, FlashMessages


class BaseLoggedInPage(View):
    """This page should be subclassed by any page that models any other page that is available as
    logged in.
    """
    CSRF_TOKEN = '//meta[@name="csrf-token"]'
    flash = FlashMessages(
        './/div[@id="flash_msg_div"]/div[@id="flash_text_div" or '
        'contains(@class, "flash_text_div")] | '
        './/div[starts-with(@class, "flash_text_div") or @id="flash_text_div"]'
    )
    help = NavDropdown('.//li[./a[@id="dropdownMenu1"]]|.//li[./a[@id="help-menu"]]')
    settings = NavDropdown('.//li[./a[@id="dropdownMenu2"]]')
    navigation = VerticalNavigation('#maintab')

    @property
    def is_displayed(self):
        return self.logged_in_as_current_user

    def logged_in_as_user(self, user):
        if self.logged_out:
            return False

        return user.name == self.current_fullname

    @property
    def logged_in_as_current_user(self):
        return self.logged_in_as_user(self.extra.appliance.user)

    @property
    def current_username(self):
        try:
            return self.extra.appliance.user.principal
        except AttributeError:
            return None

    @property
    def current_fullname(self):
        return self.settings.text.strip().split('|', 1)[0].strip()

    @property
    def current_groupname(self):
        return self.settings.items[1].strip()

    @property
    def logged_in(self):
        return self.settings.is_displayed

    @property
    def logged_out(self):
        return not self.logged_in

    def logout(self):
        self.settings.select_item('Logout')
        self.browser.handle_alert(wait=None)
        self.extra.appliance.user = None

    @property
    def csrf_token(self):
        return self.browser.get_attribute('content', self.CSRF_TOKEN)

    @csrf_token.setter
    def csrf_token(self, value):
        self.browser.set_attribute('content', value, self.CSRF_TOKEN)

    @property
    def unexpected_error(self):
        if not self.browser.elements('//h1[contains(., "Unexpected error encountered")]'):
            return None
        try:
            err_el = self.browser.element('//h2[contains(., "Error text:")]/following-sibling::h3')
            return self.browser.text(err_el)
        except NoSuchElementException:
            return None
