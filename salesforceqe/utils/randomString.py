
import random
import string
import pytest
from playwright.sync_api import Playwright

class Utils():
    def generate_random_string(self):
        generaterandomstring = ''.join(random.choices(string.ascii_letters, k=5))
        return generaterandomstring

    def generate_random_number(self):
        generaterandomnumber = ''.join(random.choices(string.digits, k=5))
        return generaterandomnumber