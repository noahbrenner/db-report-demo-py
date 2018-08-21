Database Reporting Demo - Python 3
==================================

> Query and display some statistics for a (specific) PostgreSQL database

Simple reporting tool demo for a pretend blog site. Reports are generated using PostgreSQL and Python 3.

Setup
-----

1. Make sure [Python][] (either 2 or 3), [PostgreSQL][], and [git][] are installed.

[Python]: https://www.python.org/
[PostgreSQL]: https://www.postgresql.org/
[git]: https://git-scm.com/

2. Make sure that PostgreSQL is initialized, that you are logged in as a user who can create databases, and that you do not currently have a PostgreSQL database named "news" (unless it's the same one used for this demo).

3. Install the `psycopg2` Python module (if it's not already installed) by running this in your terminal.

   ```bash
   # Depending on your setup, you may need to use `sudo`
   pip3 install psycopg2

   # If you're using Python 2, run this instead
   pip install psycopg2
   ```

4. Clone this git repository and change to its directory.

   ```bash
   git clone https://github.com/noahbrenner/db-report-demo-py.git
   cd path/to/db-report-demo-py
   ```

5. Run `bootstrap.sh` to create and set up the database. The script will also download sample data (provided by Udacity) and add it to the created database. It may take a few minutes to run, since there are more than a million rows to add.

   ```bash
   bash bootstrap.sh
   ```

Usage
-----

As simple as this:

```bash
python3 report.py
```

This is a static reporting tool, so it does not accept any arguments, though of course its reports will change if the database data changes.

For an example of the output, see [example-output.txt](example-output.txt).

Design
------

SQL query strings are returned from separate functions. While these functions only return SQL strings, they do allow for setting the maximum number of results to query for. All queries result in 2 columns, both strings, with numbers already formatted to include units (e.g. "9001 views").

The query strings are gathered in a list of tuples, along with a description to print with each query's results. The number of desired results for each query is set at this point.

The list is then iterated over to generate reports. To format the output, an additional function is used to align the columns for a given query before writing to stdout.
