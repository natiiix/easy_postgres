import psycopg2
from .dictionary import Dictionary


class Connection:
    """
    Hopefully an easier-to-use wrapper for the psycopg2 Connection class.
    """

    def __init__(self, dsn):
        self.conn = psycopg2.connect(dsn)
        self.conn.autocommit = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def __del__(self):
        self.close()

    def __str__(self):
        return str(self.conn)

    def __repr__(self):
        return repr(self.conn)

    def close(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def cursor(self):
        return self.conn.cursor()

    def one(self, query, *args, **kwargs):
        return self._exec(query, Connection._fetch_one, Connection._row_tuple, *args, **kwargs)

    def one_dict(self, query, *args, **kwargs):
        return self._exec(query, Connection._fetch_one, Connection._row_dict, *args, **kwargs)

    def all(self, query, *args, **kwargs):
        return self._exec(query, Connection._fetch_all, Connection._row_tuple, *args, **kwargs)

    def all_dict(self, query, *args, **kwargs):
        return self._exec(query, Connection._fetch_all, Connection._row_dict, *args, **kwargs)

    def iter(self, query, *args, **kwargs):
        return self._exec(query, Connection._fetch_iter, Connection._row_tuple, *args, **kwargs)

    def iter_dict(self, query, *args, **kwargs):
        return self._exec(query, Connection._fetch_iter, Connection._row_dict, *args, **kwargs)

    def _exec(self, query, fetch_callback, row_callback, *args, **kwargs):
        cur = self.cursor()

        # Handle variable-length argument list
        if len(args) == 1:
            first = args[0]
            if isinstance(first, tuple) or isinstance(first, dict):
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

        # Execute the query
        cur.execute(query, params)

        # Handle query results
        result = fetch_callback(cur, row_callback)

        cur.close()

        return result

    @staticmethod
    def _fetch_one(cursor, row_callback):
        return row_callback(cursor.fetchone(), cursor) \
            if cursor.rowcount == 1 else None

    @staticmethod
    def _fetch_all(cursor, row_callback):
        return [row_callback(r, cursor) for r in cursor.fetchall()] \
            if cursor.rowcount else []

    @staticmethod
    def _fetch_iter(cursor, row_callback):
        for _ in range(cursor.rowcount):
            yield row_callback(cursor.fetchone(), cursor)

    @staticmethod
    def _row_tuple(row, _):
        return row[0] if len(row) == 1 else row

    @staticmethod
    def _row_dict(row, cursor):
        return Dictionary({column.name: row[i] for i, column in enumerate(cursor.description)})
