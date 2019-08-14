"""Module containing the Connection class."""

import psycopg2
from .dictionary import Dictionary
from .transaction import Transaction


class Connection:
    """
    Hopefully an easier-to-use wrapper for the psycopg2 Connection class.

    Single-item tuples are replaced with the value of the only item.
    This applies to all tuple-retruning methods: `one`, `all` and `iter`.

    The primary use of this feature are single-column `SELECT` queries and
    `INSERT` and `UPDATE` statements with a single-value `RETURNING` clause.
    """

    def __init__(self, dsn, autocommit=True):
        """Initialize a new PostgreSQL connection using a DSN."""
        self.conn = psycopg2.connect(dsn)
        self.conn.autocommit = autocommit

    def __enter__(self):
        """
        Return reference to the connection object.

        This method is called when entering a
        block statement such as `with` or `try`.
        """
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Commit or rollback changes and close the connection.

        Changes will be committed unless an exception was raised.

        This method is called when leaving a block statement.
        """
        if exc_type or exc_value or exc_traceback:
            self.rollback()
        else:
            self.commit()

        self.close()

    def __del__(self):
        """
        Close the connection.

        This method is called when the object is being deleted.

        This can happen virtually anytime, so please make
        no assumptions about when it is going to be called.
        """
        self.close()

    def __str__(self):
        """Convert the connection to a string."""
        return str(self.conn)

    def __repr__(self):
        """Get a string representation of the connection."""
        return repr(self.conn)

    def close(self):
        """
        Close the connection.

        It is preferrable to use the `with` statement instead
        of manually closing the connection via this method.
        """
        self.conn.close()

    def rollback(self):
        """Roll-back any changes made since the last commit."""
        self.conn.rollback()

    def commit(self):
        """Commit all changes made using this connection."""
        self.conn.commit()

    def cursor(self):
        """Get a new `psycopg2` cursor. Use this for a more direct access."""
        return self.conn.cursor()

    def transaction(self):
        """
        Create a new pseudo-transaction.

        This method is a shorthand for calling the `Transaction` constructor.
        You should always only create a single `Transaction` at a time.
        For correct functionality, please use this in a `with` statement.
        """
        return Transaction(self)

    def run(self, query, *args, **kwargs):
        """Run the SQL query and return `None`."""
        return self._exec(query, _fetch_none, None, *args, **kwargs)

    def one(self, query, *args, **kwargs):
        """
        Run the SQL query and return single row as a direct value or a tuple.

        If a single column is returned, the value will
        be returned instead of a single-item tuple.

        `None` will be returned in case the SQL query
        did not return exactly one row.
        """
        return self._exec(query, _fetch_one, _row_tuple, *args, **kwargs)

    def one_dict(self, query, *args, **kwargs):
        """
        Run the SQL query and return a single row as a dictionary.

        `None` will be returned in case the SQL query
        did not return exactly one row.
        """
        return self._exec(query, _fetch_one, _row_dict, *args, **kwargs)

    def all(self, query, *args, **kwargs):
        """
        Run the SQL query and return a list of values or tuples.

        If a single column is returned, the value will
        be returned instead of a single-item tuple.
        """
        return self._exec(query, _fetch_all, _row_tuple, *args, **kwargs)

    def all_dict(self, query, *args, **kwargs):
        """Run the SQL query and return a list of dictionaries."""
        return self._exec(query, _fetch_all, _row_dict, *args, **kwargs)

    def iter(self, query, *args, **kwargs):
        """
        Run the SQL query and return a generator of values or tuples.

        If a single column is returned, the value will
        be returned instead of a single-item tuple.
        """
        return self._exec(query, _fetch_iter, _row_tuple, *args, **kwargs)

    def iter_dict(self, query, *args, **kwargs):
        """Run the SQL query and return a generator of dictionaries."""
        return self._exec(query, _fetch_iter, _row_dict, *args, **kwargs)

    def _exec(self, query, fetch_callback, row_callback, *args, **kwargs):
        """Run the SQL query and apply specified callbacks to the results."""
        # Handle variable-length argument list
        if len(args) == 1:
            first = args[0]
            if isinstance(first, (tuple, dict)):
                params = first
            elif isinstance(first, list):
                params = tuple(first)
            else:
                params = (first,)
        else:
            params = tuple(args)

        # Handle keyword arguments
        if kwargs:
            # Convert parameters into a dictionary if they aren't one already
            if not isinstance(params, dict):
                params = {i: v for i, v in enumerate(params)}

            params.update(kwargs)

        with self.cursor() as cur:
            cur.execute(query, params)

            # Handle query results
            return fetch_callback(cur, row_callback)


def _fetch_none(_, __):
    """Fetch no rows and return `None`."""
    return None


def _fetch_one(cursor, row_callback):
    """Fetch exactly one row and return it or `None`."""
    return row_callback(cursor.fetchone(), cursor) \
        if cursor.rowcount == 1 else None


def _fetch_all(cursor, row_callback):
    """Fetch all rows and return them all at once."""
    return [row_callback(r, cursor) for r in cursor.fetchall()] \
        if cursor.rowcount else []


def _fetch_iter(cursor, row_callback):
    """Fetch rows one by one and yield them as a generator."""
    for _ in range(cursor.rowcount):
        yield row_callback(cursor.fetchone(), cursor)


def _row_tuple(row, _):
    """Extract single value from row or return the whole tuple."""
    return row[0] if len(row) == 1 else row


def _row_dict(row, cursor):
    """Convert the row into a smart dictionary and return it."""
    return Dictionary({column.name: row[i] for i, column in enumerate(cursor.description)})
