class Transaction:
    def __init__(self, conn):
        self.conn = conn
        self.autocommit = conn.autocommit

    def __enter__(self):
        if self.autocommit:
            self.conn.autocommit = False

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # Roll-back on an exception
        if exc_type or exc_value or exc_traceback:
            self.conn.rollback()
        # Otherwise commit the changes
        else:
            self.conn.commit()

        if self.autocommit:
            self.conn.autocommit = True
