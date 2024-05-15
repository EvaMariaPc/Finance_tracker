class Transactions:
    transactions = []

    @staticmethod
    def record_transaction(description, amount):
        """Record a transaction with a description and amount."""
        Transactions.transactions.append((description, amount))

    @staticmethod
    def view_transactions():
        """View all recorded transactions."""
        print("Transaction History:")
        if not Transactions.transactions:
            print("No transactions recorded yet.")
        else:
            for index, (description, amount) in enumerate(Transactions.transactions, start=1):
                print(f"{index}. {description}: ${amount:.2f}")
