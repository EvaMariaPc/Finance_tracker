from operation import Operations
from transaction import Transactions
from balance import Balance
import streamlit as st


st.title("Simple Calculator & Transaction Tracker")


choice = st.sidebar.selectbox("Choose operation:", ["Calculator", "Transaction"])

if __name__ == "__main__":
    transaction = Transactions()
    operations = Operations()
    balance = Balance()

    print("Salut!")
    while True:
        print("\nChoose operation:")
        print("1. Addition")
        print("2. Subtraction")
        print("3. Multiplication")
        print("4. Division")
        print("5. Bye bye")
        print("10. Transaction")
        choice = input("Enter your choice: ")

        if choice == '5':
            print("Bye bye! See you later!")
            break

        elif choice == '10':
            transaction.view_transactions()
            balance.update_and_display_balance()
            continue  # Continue to the next iteration of the loop

        try:
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))
        except ValueError:
            print("Invalid input. Please enter numeric values.")
            continue

        if choice == '1':
            print("Result:", operations.add(num1, num2))
        elif choice == '2':
            print("Result:", operations.subtract(num1, num2))
        elif choice == '3':
            print("Result:", operations.multiply(num1, num2))
        elif choice == '4':
            if num2 == 0:
                print("Error: Division by zero!")
            else:
                print("Result:", operations.divide(num1, num2))
        else:
            print("Invalid input. Please enter a valid number.")

        # Display current balance after each transaction
        balance.update_and_display_balance()