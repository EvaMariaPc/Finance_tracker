from transaction import Transactions
from operation import Operations


class Balance:
    @staticmethod
    def current_balance():
        """Calculate and return the current balance."""
        total = sum(amount for _, amount in Transactions.transactions)
        return total

    @staticmethod
    def display_balance():
        """Display the current balance."""
        balance = Balance.current_balance()
        print(f"Current Balance: ${balance:.2f}")

    @staticmethod
    def update_and_display_balance():
        """Update and continuously display the current balance."""
        while True:
            Balance.display_balance()
            choice = input("Choose operation (or 'q' to quit): ")
            if choice.lower() == 'q':
                break
            Balance.perform_operation(choice)

    @staticmethod
    def perform_operation(choice):
        """Perform operation based on user choice."""
        try:
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))
        except ValueError:
            print("Invalid input. Please enter numeric values.")
            return

        if choice == '1':
            print("Result:", Operations.add(num1, num2))
        elif choice == '2':
            print("Result:", Operations.subtract(num1, num2))
        elif choice == '3':
            print("Result:", Operations.multiply(num1, num2))
        elif choice == '4':
            if num2 == 0:
                print("Error: Division by zero!")
            else:
                print("Result:", Operations.divide(num1, num2))
        else:
            print("Invalid input. Please enter a valid operation.")