from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.menu import MDDropdownMenu

from kivy.metrics import dp
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty

from lib.db import connect_to_db
from lib.utils import *

from datetime import datetime

import json, time
import os.path

from kivy.core.window import Window

"""
COLORS: https://colorhunt.co/palette/0f0f0f232d3f005b41008170
"""

__version__ = "1.0.2"


class ContentNavigationDrawer(MDBoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


class PasswordField(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()


class MainApp(MDApp):
    def build(self):
        # Init verion
        self.version = __version__
        # Init DB
        conn, cursor = connect_to_db()
        self.conn = conn
        self.cursor = cursor
        # Init Window
        self.title = "SpareApp"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        # Init icon
        self.icon = "assets/sapre_app_launcher.png"
        # Init info
        self.user = None
        self.user_data = fetch_user_data(self)
        # Return app
        return Builder.load_file("layout.kv")

    def on_start(self):
        # Add tables
        self.create_recurring_expense_table()
        self.create_check_expense_table()
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
        # Parse amount
        try:
            amount = float(self.root.ids[type].text)
        except Exception:
            self.root.ids.notification_text.text = "Please enter a valide number"
            return
        # Retrieve Category
        if type == "expense_amount":
            text_category = self.root.ids.category_dropdown_button.text
            if text_category == "Select a Category":
                self.root.ids.notification_text.text = "Select a Category"
                return
        else:
            # For recurring expense default to 'Utilities'
            text_category = "Utilities"
        # Get the ID
        category = [
            element
            for element in self.user_data["categories"]
            if element[1] == text_category
        ][0]
        # Store expense
        if save_expense(self, amount, category[0], today, type):
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

    def update_savings(self):
        # Reset text just in case of errors
        self.root.ids["notification_text"].text = ""
        try:
            amount = float(self.root.ids.update_savings.text)
        except Exception:
            self.root.ids.notification_text.text = "Please enter a valide number"
            return
        if amount < 0 or amount > 99:
            self.root.ids[
                "notification_text"
            ].text = "THe amount must be between 0 and 99"
            return
        if save_savings(self, amount):
            self.update_app_text()
            self.root.ids.screen_manager.transition.direction = "right"
            self.root.ids.screen_manager.current = "Manage Incomes"
        else:
            self.root.ids.notification_text.text = "Something went wrong"
            return

    def update_categories(self):
        # Reset text just in case of errors
        self.root.ids["notification_text"].text = ""
        # Check sum
        categories_val = []
        # Retrieve data
        for catgory in self.user_data["categories"]:
            categories_val.append(
                float(self.root.ids[f"{catgory[1].lower()}_threshold_field"].text)
            )
        # Check
        if sum(categories_val) != 0 and sum(categories_val) != 100:
            self.root.ids["notification_text"].text = "Incorrect input"
            return
        else:
            for catgory in self.user_data["categories"]:
                save_category(
                    self,
                    catgory[1],
                    float(self.root.ids[f"{catgory[1].lower()}_threshold_field"].text),
                )
            # Update infos
            self.update_app_text()
            # Redirect
            self.root.ids.screen_manager.transition.direction = "right"
            self.root.ids.screen_manager.current = "Dashboard"

    def update_app_text(self):
        # Fetch new data
        self.user_data = fetch_user_data(self)
        # Update text
        self.root.ids.remaining_budget.text = (
            f"{self.user_data['net_budget'] + self.user_data['net_savings']}€"
        )
        self.root.ids.current_income.text = self.user_data["income"]
        self.root.ids.current_savings.text = self.user_data["savings"]
        self.root.ids.direct_saving_label.text = f"({self.user_data['net_savings']} are direct savings)"
        # Update categories
        for catgory in self.user_data["categories"]:
            # Update input fields
            self.root.ids[
                f"{catgory[1].lower()}_threshold_field"
            ].text = f"{catgory[2]}"
            # Update dashboard
            self.root.ids[
                f"{catgory[1].lower()}_remaining_budget"
            ].text = f"{self.user_data['category_budgets'][catgory[1]]}€"
        # Update tables
        self.root.ids.incomes_data_layout.remove_widget(self.recurring_expenses_table)
        self.create_recurring_expense_table()
        self.root.ids.check_expense_data_layout.remove_widget(self.check_expense_table)
        self.create_check_expense_table()
        # Update table selection
        self.recurring_expense_selection = []

    def create_recurring_expense_table(self):
        # Translate expense
        expense_data = create_expense_tables_data(
            self, self.user_data["recurring_expenses"], type="recurring"
        )
        # Create tables
        self.recurring_expenses_table = MDDataTable(
            check=True,
            column_data=[("ID", dp(20)), ("Category", dp(60)), ("Amount", dp(40))],
            row_data=expense_data,
        )
        # Add widget
        self.root.ids.incomes_data_layout.add_widget(self.recurring_expenses_table)

    def create_check_expense_table(self):
        # Translate expense
        expense_data = create_expense_tables_data(self, self.user_data["temp_expenses"], type="temp")
        # Create tables
        self.check_expense_table = MDDataTable(
            check=False,
            column_data=[
                ("ID", dp(10)),
                ("Date", dp(40)),
                ("Category", dp(30)),
                ("Amount", dp(20)),
            ],
            row_data=expense_data,
        )
        # Add widget
        self.root.ids.check_expense_data_layout.add_widget(self.check_expense_table)

    def category_menu(self):
        # Create dropdown items
        categories = []
        for category in DEFAULT_CATEGORIES:
            categories.append(
                {
                    "text": category,
                    "on_release": lambda x=category: self.select_category(x),
                    "viewclass": "OneLineListItem",
                    "height": dp(56),
                }
            )
        self.menu = MDDropdownMenu(
            caller=self.root.ids.category_dropdown_button,
            items=categories,
            width_mult=4,
        )
        self.menu.open()

    def select_category(self, category):
        self.root.ids.category_dropdown_button.text = category
        self.menu.dismiss()


MainApp().run()
