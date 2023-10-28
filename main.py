from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.datatables import MDDataTable

from kivy.metrics import dp
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty

from lib.db import connect_to_db
from lib.utils import signup_user, check_login_user, check_user, save_expense, save_amount, fetch_user_data, delete_expense

from datetime import datetime

import json, time
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
        self.title = "SpareApp"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        # Init info
        self.user = None
        self.user_data = fetch_user_data(self)
        # Return app
        return Builder.load_file("layout.kv")

    def on_start(self):
        # Add tables
        self.create_recurring_expense_table()
        # Check if user is preset
        if os.path.isfile("logged_user.json"):
            with open("logged_user.json", "r") as f:
                user = json.load(f)
                # Check if user exist
                if check_user(self, user):
                    self.login(user)
                    # Redirect
                    self.root.ids.root_screen_manager.current = "logged"


    def signup(self):
        signup_user(self)

    def run_login(self):
        user = check_login_user(self)
        if user is not None:
            self.login(user)
            # Redirect
            self.root.ids.root_screen_manager.current = "logged"

    def login(self, user):
        if user is not None:
            # Set user
            self.user = user
            # Fetch and update user data
            self.update_app_text()

    def logout(self):
        self.user = None
        self.user_data = None
        if os.path.isfile("logged_user.json"):
            os.remove("logged_user.json")
        self.root.ids.root_screen_manager.current = "login"

    def store_expense(self, type: str):
        # Reset text just in case of errors
        self.root.ids["notification_text"].text = ""
        # Retrieve data and parse amount
        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            amount = float(self.root.ids[type].text)
        except Exception:
            self.root.ids.notification_text.text = "Please enter a valide number"
            return
        if save_expense(self, amount, today, type):
            self.update_app_text()
            self.root.ids.screen_manager.transition.direction = "right"
            if type == "recurring_expense":
                self.root.ids.screen_manager.current = "Manage Incomes"
            else:
                self.root.ids.screen_manager.current = "Dashboard"
        else:
            self.root.ids.notification_text.text = "Something went wrong"
            return

    def remove_expense(self, type: str):
        if type == "recurring":
            # Get selection
            selection = self.recurring_expenses_table.get_row_checks()
            # Check if there are selected item
            if len(selection) > 0:
                # Retrieve the expense id from the selection
                ids = [tmp[0] for tmp in selection]
                # Run the delete and check
                if delete_expense(self, ids, type):
                    self.update_app_text()
                    self.recurring_expense_selection = []
                    self.root.ids.screen_manager.transition.direction = "right"
                    self.root.ids.screen_manager.current = "Manage Incomes"
                else:
                    self.root.ids.notification_text.text = "Something went wrong"
                    return
        elif type == "tmp":
            if delete_expense(self, [], type):
                self.update_app_text()
            else:
                self.root.ids.notification_text.text = "Something went wrong"
                return

    def update_income(self):
        # Reset text just in case of errors
        self.root.ids["notification_text"].text = ""
        try:
            amount = float(self.root.ids.update_income.text)
        except Exception:
            self.root.ids.notification_text.text = "Please enter a valide number"
            return
        if save_amount(self, amount):
            self.update_app_text()
            self.root.ids.screen_manager.transition.direction = "right"
            self.root.ids.screen_manager.current = "Manage Incomes"
        else:
            self.root.ids.notification_text.text = "Something went wrong"
            return
    
    def update_app_text(self):
        # Fetch new data
        self.user_data = fetch_user_data(self)
        # Update text
        self.root.ids.remaining_budget.text = self.user_data["budget"]
        self.root.ids.current_incom.text = self.user_data["income"]
        self.root.ids.remaining_budget.text = self.user_data["budget"]
        # Update tables
        self.root.ids.incomes_data_layout.remove_widget(self.recurring_expenses_table)
        self.create_recurring_expense_table()
        # Update table selection
        self.recurring_expense_selection = []

    def create_recurring_expense_table(self):
        # Create tables
        self.recurring_expenses_table = MDDataTable(
            check=True,
            column_data=[
                ("ID", dp(20)),
                ("Category", dp(60)),
                ("Amount", dp(40))
            ],
            row_data=self.user_data["recurring_expenses"],
        )
        # Add widget
        self.root.ids.incomes_data_layout.add_widget(self.recurring_expenses_table)

MainApp().run()
