from transaction import Transactions  # Assuming the Transactions class is imported correctly


class Operations:
    @staticmethod
    def record_operation(operation, x, y, result):
        """Helper function to record the transaction."""
        Transactions.record_transaction(f"{operation}: {x} {operation} {y}", result)

    @staticmethod
    def add(x, y):
        """Function to perform addition."""
        result = x + y
        Operations.record_operation("Addition", x, y, result)
        return result

    @staticmethod
    def subtract(x, y):
        """Function to perform subtraction."""
        result = x - y
        Operations.record_operation("Subtraction", x, y, result)
        return result

    @staticmethod
    def multiply(x, y):
        """Function to perform multiplication."""
        result = x * y
        Operations.record_operation("Multiplication", x, y, result)
        return result

    @staticmethod
    def divide(x, y):
        """Function to perform division."""
        if y != 0:
            result = x / y
            Operations.record_operation("Division", x, y, result)
            return result
        else:
            Operations.record_operation("Error: Division by zero!", x, y, "N/A")
            return "Error: Division by zero!"
