from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout

from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty

from bin.db import connect_to_db
from bin.utils import signup_user, check_login_user, check_user

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
        # Create app
        app = Builder.load_file("layout.kv")
        # Check if user is preset
        if os.path.isfile("logged_user.json"):
            with open("logged_user.json", "r") as f:
                user = json.load(f)
                # Check if user exist
                if check_user(self, user):
                    self.login(user, app.ids["main_menu"].ids["menu_header"])
                    # Redirect
                    app.ids["root_screen_manager"].current = "logged"
        return app

    def signup(self):
        signup_user(self)

    def run_login(self):
        user = check_login_user(self)
        if user is not None:
            self.login(user, self.root.ids["main_menu"].ids["menu_header"])
            # Redirect
            self.root.ids["root_screen_manager"].current = "logged"

    def login(self, user, menu_header):
        if user is not None:
            self.user = user
            # Update header
            menu_header.title = user[2]
            menu_header.text = user[1]

    def logout(self):
        self.user = None
        if os.path.isfile("logged_user.json"):
            os.remove("logged_user.json")
        self.root.ids["root_screen_manager"].current = "login"


MainApp().run()
