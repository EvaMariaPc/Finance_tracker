import streamlit as st
from datetime import datetime
from transaction import Transactions


def get_current_balance():
    return 1000


def record_transaction(description, amount):
    timestamp = datetime.now()
    Transactions.record_transaction(description, amount, timestamp)


current_balance = get_current_balance()
st.sidebar.title("Current Balance")
st.sidebar.write(f"${current_balance:.2f}")


class Transactions:
    transactions = []

    @staticmethod
    def record_transaction(description, amount, timestamp):
        """Record a transaction with a description, amount, and timestamp."""
        Transactions.transactions.append((description, amount, timestamp))