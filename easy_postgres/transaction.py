"""Module containing the Transaction class."""


class Transaction:
    """Pseudo-transaction, which pauses the PostgreSQL auto-commit setting."""

    def __init__(self, conn):
        """
        Initialize a new transaction.

        Avoid creating multiple transactions for the same connection
        at the same time. This could lead to race conditions and
        some changes could be accidentally committed or
        rolled back by one of the other transactions.
        """
        self.conn = conn
        self.autocommit = conn.conn.autocommit

    def __enter__(self):
        """Turn off auto-commit and return the transaction instance."""
        if self.autocommit:
            self.conn.conn.autocommit = False

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Commit or roll-back and reset the auto-commit setting.

        Changes will be committed if no exception has been thrown.
        Otherwise a roll-back of this transaction will happen.
        """
        # Roll-back on an exception
        if exc_type or exc_value or exc_traceback:
            self.conn.rollback()
        # Otherwise commit the changes
        else:
            self.conn.commit()

        if self.autocommit:
            self.conn.conn.autocommit = True
