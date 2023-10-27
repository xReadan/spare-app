from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout

from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty

from lib.db import connect_to_db
from lib.utils import signup_user, check_login_user, check_user, save_expense

from datetime import datetime

import json
import os.path

"""
COLORS: https://colorhunt.co/palette/0f0f0f232d3f005b41008170
"""


class ContentNavigationDrawer(MDBoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


class PasswordField(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()


class MainApp(MDApp):
    def build(self):
        # Init DB
        conn, cursor = connect_to_db()
        self.conn = conn
        self.cursor = cursor
        # Init Window
        self.title = "Hello"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        # Check if user is preset
        if os.path.isfile("logged_user.json"):
            with open("logged_user.json", "r") as f:
                user = json.load(f)
                # Check if user exist
                if check_user(self, user):
                    self.login(user)
        # Create app
        app = Builder.load_file("layout.kv")
        if self.user:
            # Redirect
            app.ids["root_screen_manager"].current = "logged"
        return app

    def signup(self):
        signup_user(self)

    def run_login(self):
        user = check_login_user(self)
        if user is not None:
            self.login(user)
            # Redirect
            self.root.ids["root_screen_manager"].current = "logged"

    def login(self, user):
        if user is not None:
            self.budget = "1000€"
            self.user = user

    def logout(self):
        self.user = None
        if os.path.isfile("logged_user.json"):
            os.remove("logged_user.json")
        self.root.ids["root_screen_manager"].current = "login"

    def store_expense(self):
        # Reset text just in case of errors
        self.root.ids["notification_text"].text = ""
        # Retrieve data and parse amount
        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            amount = float(self.root.ids["expense_amount"].text)
        except Exception:
            self.root.ids["notification_text"].text = "Please enter a valide number"
            return
        if save_expense(self, amount, today):
            self.root.ids["screen_manager"].transition.direction = 'right'
            self.root.ids["screen_manager"].current = "dashboard"
        else:
            self.root.ids["notification_text"].text = "Something went wrong"
            return


MainApp().run()
