import psycopg2
from .dictionary import Dictionary
from .transaction import Transaction


class Connection:
    """
    Hopefully an easier-to-use wrapper for the psycopg2 Connection class.
    """

    def __init__(self, dsn, autocommit=True):
        self.conn = psycopg2.connect(dsn)
        self.conn.autocommit = autocommit

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type or exc_value or exc_traceback:
            self.rollback()
        else:
            self.commit()

        self.close()

    def __del__(self):
        self.close()

    def __str__(self):
        return str(self.conn)

    def __repr__(self):
        return repr(self.conn)

    def close(self):
        self.conn.close()

    def rollback(self):
        self.conn.rollback()

    def commit(self):
        self.conn.commit()

    def cursor(self):
        return self.conn.cursor()

    def transaction(self):
        return Transaction(self)

    def run(self, query, *args, **kwargs):
        return self._exec(query, None, None, *args, **kwargs)

    def one(self, query, *args, **kwargs):
        return self._exec(query, _fetch_one, _row_tuple, *args, **kwargs)

    def one_dict(self, query, *args, **kwargs):
        return self._exec(query, _fetch_one, _row_dict, *args, **kwargs)

    def all(self, query, *args, **kwargs):
        return self._exec(query, _fetch_all, _row_tuple, *args, **kwargs)

    def all_dict(self, query, *args, **kwargs):
        return self._exec(query, _fetch_all, _row_dict, *args, **kwargs)

    def iter(self, query, *args, **kwargs):
        return self._exec(query, _fetch_iter, _row_tuple, *args, **kwargs)

    def iter_dict(self, query, *args, **kwargs):
        return self._exec(query, _fetch_iter, _row_dict, *args, **kwargs)

    def _exec(self, query, fetch_callback, row_callback, *args, **kwargs):
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
    return None


def _fetch_one(cursor, row_callback):
    return row_callback(cursor.fetchone(), cursor) \
        if cursor.rowcount == 1 else None


def _fetch_all(cursor, row_callback):
    return [row_callback(r, cursor) for r in cursor.fetchall()] \
        if cursor.rowcount else []


def _fetch_iter(cursor, row_callback):
    for _ in range(cursor.rowcount):
        yield row_callback(cursor.fetchone(), cursor)


def _row_tuple(row, _):
    return row[0] if len(row) == 1 else row


def _row_dict(row, cursor):
    return Dictionary({column.name: row[i] for i, column in enumerate(cursor.description)})
