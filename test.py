import streamlit as st
from operation import Operations
from transaction import Transactions
from balance import Balance

# Create instances of necessary classes
transaction = Transactions()
operations = Operations()
balance = Balance()

st.title("Simple Calculator & Transaction Tracker")

while True:
    st.sidebar.markdown("### Choose Operation")
    choice = st.sidebar.radio("Choose an operation:", ["Calculator", "Transaction", "Exit"])

    if choice == "Calculator":
        st.header("Calculator")
        num1 = st.number_input("Enter first number:")
        num2 = st.number_input("Enter second number:")
        operation = st.selectbox("Select Operation:", options=["Addition", "Subtraction", "Multiplication", "Division"])

        result = None
        if st.button("Calculate"):
            try:
                if operation == "Addition":
                    result = operations.add(num1, num2)
                elif operation == "Subtraction":
                    result = operations.subtract(num1, num2)
                elif operation == "Multiplication":
                    result = operations.multiply(num1, num2)
                elif operation == "Division":
                    if num2 == 0:
                        st.error("Error: Division by zero!")
                        result = None
                    else:
                        result = operations.divide(num1, num2)
                if result is not None:
                    st.success(f"Result: {result}")
            except ValueError:
                st.error("Error: Invalid input. Please enter numeric values.")
            except ZeroDivisionError:
                st.error("Division by zero is not allowed.")

    elif choice == "Transaction":
        st.header("Transaction History")
        transaction.view_transactions()
        balance.update_and_display_balance()

    elif choice == "Exit":
        st.write("Bye bye! See you later!")
        break
