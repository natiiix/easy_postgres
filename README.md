# Easy Postgres

**Abstraction layer for PostgreSQL database manipulation based on the `psycopg2` package**

Primary focuses are **lightweight API** and **high flexibility** when it comes to handling user input. This should make the package very easy to use while maintaining a usable performance level.

## Contents

- [Easy Postgres](#easy-postgres)
  - [Contents](#contents)
  - [WARNING: Work in Progress](#warning-work-in-progress)
  - [How To Use](#how-to-use)
    - [`Connection` class](#connection-class)
      - [`Connection.run` method](#connectionrun-method)
      - [`Connection.one` method](#connectionone-method)
      - [`Connection.all` method](#connectionall-method)
      - [`Connection.iter` method](#connectioniter-method)
      - [`Connection.XXX_dict` methods](#connectionxxxdict-methods)
    - [`Dictionary` class](#dictionary-class)
      - [Accessing Items](#accessing-items)
  - [License](#license)

## WARNING: Work in Progress

*This package is currently under heavy development and should NOT be used in production. The current API is very likely to change in the near future.*

## How To Use

### `Connection` class

To do anything, you must first create an instance of the `Connection` class. Give the instructor a [DSN](https://en.wikipedia.org/wiki/Data_source_name). The DSN can take many forms, so please check the [`psycopg2.connect()` function documentation](http://initd.org/psycopg/docs/module.html#psycopg2.connect) for more details.

Once you have a `Connection`, you are ready to run any common SQL query (`SELECT`, `INSERT`, `UPDATE`, `DELETE` should definitely work; the rest should probably work, but it is not guaranteed).

#### `Connection.run` method

Executes the specified SQL query and returns nothing (`None`). This is the right choice for all non-returning queries (`INSERT`, `UPDATE`, `DELETE`, `DROP`, etc.). An `INSERT` query with a `RETURNING` clause should use the `Connection.one` method instead.

#### `Connection.one` method

Executes the specified SQL query and returns a single row. If the returned row only has a single column, the single value will be returned. In the case of multiple returned columns, a tuple containing all the column values will be returned.

If the number of returned rows is not exactly equal to one, `None` will be returned instead.

This method is meant to be used for SQL queries that are guaranteed to always return exactly one row (e.g., `SELECT COUNT(*) FROM table;`, `INSERT INTO table (id) VALUES (1) RETURNING id;`).

| SQL Query                   | Returned Result       |
| --------------------------- | --------------------- |
| `SELECT 'Hello World!';`    | `"Hello World!"`      |
| `SELECT 'Hello', 'World!';` | `("Hello", "World!")` |
| `SELECT 1;`                 | `1`                   |
| `SELECT 1, 2;`              | `(1, 2)`              |
| `SELECT 1, 2, 3, 4, 5;`     | `(1, 2, 3, 4, 5)`     |

#### `Connection.all` method

Executes the specified SQL query and returns all the rows as a list. Single-column results will be converted to a list of the column's values. The behavior is similar to the `Connection.one` method.

This method is mostly meant to be used for `SELECT` queries that may return more (or less) than one row.

#### `Connection.iter` method

Executes the specified SQL query and returns all the rows as a generator. This method is an alternative to `Connection.all` to be used when iterating over a large number of rows. The rows are fetched one at a time, so casting the generator to a list will give the same exact result as calling `Connection.all` would have, but it will likely be much slower.

#### `Connection.XXX_dict` methods

These methods execute the SQL queries just like their non-dict counterparts, but instead of returning a value or a tuple, they return a `Dictionary` instance.

It is advisable to give all the returned columns a unique name without any special characters (`_` is the only allowed exception). If you include any special character in the column name or if the column name is a Python keyword (`if`, `for`, etc.) or the name of a built-in method name (`__init__`, `__str__`, etc.), the column value will become inaccessible as an attribute, or worse yet, some functionality of the `Dictionary` class may be broken. Please keep this in mind when using the `XXX_dict` methods.

### `Dictionary` class

An extension of the Python's built-in [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) class. It makes the items accessible via attributes (the item's key is used as the attribute name). There are several limitations, but the code should be slightly more readable. The support for the default dictionary item access (via an index) remains.

A `Dictionary` can be initialized from a regular dictionary, using keyword arguments or a combination of both.

#### Accessing Items

For the purpose of this example, imagine you ran an SQL query that returned a single row as a `Dictionary`. The query result is stored in a variable called `result`. Now you want to print the value of the `price` column. Here is a comparison of `dict` and `Dictionary`.

| Access Method | Standard `dict`          | `Dictionary`             |
| ------------- | ------------------------ | ------------------------ |
| Index         | `print(result["price"])` | `print(result["price"])` |
| Attribute     | N/A                      | `print(result.price)`    |

You can use whichever way of accessing the items you prefer. If you want, you can even cast the `Dictionary` back to a `dict` for better compatibility. Being able to access items as attributes simply seems more convenient and easier to read.

## License

This package is available under the [MIT License](https://en.wikipedia.org/wiki/MIT_License).
