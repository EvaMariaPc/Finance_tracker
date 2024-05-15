import streamlit as st
from datetime import datetime


class Background:
    @staticmethod
    def set_background_color(color):
        st.markdown(
            f"""
            <style>
            body {{
                background-color: {color};
            }}
            </style>
            """,
            unsafe_allow_html=True
        )


class Text:
    @staticmethod
    def set_text_color(color):
        st.markdown(
            f"""
            <style>
            .purple-text {{
                color: {color};
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def display_purple_text():
        st.markdown('<p class="purple-text">This text is purple!</p>', unsafe_allow_html=True)


class Transactions:
    transactions = []

    @staticmethod
    def record_transaction(description, amount, timestamp):
        """Record a transaction with a description, amount, and timestamp."""
        Transactions.transactions.append((description, amount, timestamp))

    @staticmethod
    def calculate_balance():
        """Calculate the current balance considering all recorded transactions."""
        balance = 0
        for _, amount, _ in Transactions.transactions:
            balance += amount
        return balance


def record_transaction(description, amount):
    timestamp = datetime.now()  # Get the current timestamp
    Transactions.record_transaction(description, amount, timestamp)


st.title("Combined Streamlit Application")


Background.set_background_color("#FFC0CB")  # Pink


Text.set_text_color("purple")


Text.display_purple_text()


record_transaction("Initial Balance", 1000)


current_balance = Transactions.calculate_balance()


st.sidebar.title("Current Balance")
st.sidebar.write(f"${current_balance:.2f}")