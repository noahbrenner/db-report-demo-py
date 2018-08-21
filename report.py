#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create a concise report for the "news" database.

Usage:
  python3 report.py

Data reported includes:
  - The three most popular articles
  - The most popular article authors
  - The days that had more than a 1% HTTP error rate
"""

import psycopg2


DB_NAME = 'news'


def popular_articles_query(limit=None):
    """Return an SQL string to query for popular articles.

    Args:
        limit (int): The maximum number of results to query for. (optional)

    Returns:
        str: An SQL string.  When used in a query, the result will contain
             two columns:
                 - str: The article's name.
                 - str: The number of page visits (e.g. "1337 views").
    """
    return """
        SELECT title, format('%s views', count(*)) AS views
            FROM log
                JOIN articles ON log.path = ('/article/' || articles.slug)
            GROUP BY articles.title
            ORDER BY count(*) DESC
            LIMIT {number};
    """.format(number=limit or 'ALL')


def popular_authors_query(limit=None):
    """Return an SQL string to query for popular article authors.

    Args:
        limit (int): The maximum number of results to query for. (optional)

    Returns:
        str: An SQL string.  When used in a query, the result will contain
             two columns:
                 - str: The author's name.
                 - str: The combined number of page visits for all of that
                   author's articles (e.g. "9001 views").
    """
    return """
        SELECT authors.name, format('%s views', count(*)) AS views
            FROM log
                JOIN articles ON log.path = ('/article/' || articles.slug)
                JOIN authors ON articles.author = authors.id
            GROUP BY authors.name
            ORDER BY count(*) DESC
            LIMIT {number};
    """.format(number=limit or 'ALL')


def days_with_errors_query(limit=None):
    """Return an SQL string to qurery for days with many HTTP errors.

    Args:
        limit (int): The maximum number of results to query for. (optional)

    Returns:
        str: An SQL string.  When used in a query, the result will contain
             two columns describing days which had an HTTP response error
             rate of more than 1%:
                 - The date as a string (e.g. "December 31, 2000").
                 - The rate of HTTP requests for that day which did not
                   result in a "200 OK" response (e.g. "1.11% errors").
    """
    return """
        WITH date_errpercent AS (
            SELECT
                    time::date AS date,
                    (
                        -- Count the number of errors on this date
                        sum(CASE WHEN status != '200 OK' THEN 1 ELSE 0 END)
                        -- Calculate percentage compared to the total requests
                        -- Convert from integer so that we get decimal places
                        / count(*)::decimal * 100
                    ) as err_percent
                FROM log
                GROUP BY date
        )
        SELECT
                to_char(date, 'FMMonth FMDD, YYYY') AS date,
                format('%s%% errors', round(err_percent, 2)) AS errors
            FROM date_errpercent
            WHERE err_percent > 1
            ORDER BY err_percent
            LIMIT {number};
    """.format(number=limit or 'ALL')


# Gather SQL queries along with short descriptions of their output
reports = [
    ('Three most popular articles', popular_articles_query(3)),
    ('Most popular article authors', popular_authors_query()),
    ('Days with more than 1% HTTP error rate', days_with_errors_query()),
]


def format_report(table):
    """Return data from `table` in aligned columns of optimal width.

    Args:
        table (list[list[str, str]]): The data structure to format.  Each list
            inside the top-level one represents a row.  All rows must have
            exactly two columns and contain only strings.

    Returns:
        str: Columns sized to the longest item of that column.  The first
             column is aligned to the left, the second is to the right:

                Column number one -             Column 2
                Another row       - Second column, row 2
    """
    col_widths = tuple(max(map(len, column)) for column in zip(*table))
    row_format = '{:<%s} - {:>%s}' % col_widths

    return '\n'.join(row_format.format(*row) for row in table)


def main():
    """Print database reports to stdout.
    """
    print('=== Report for database: {} ==='.format(DB_NAME))

    heading_format = '\n{indent}{{heading}}:\n'.format(indent=' ' * 3)

    for heading, query in reports:
        print(heading_format.format(heading=heading))

        # The context manager automatically closes `db` and `cursor`
        with psycopg2.connect(database=DB_NAME) as db, db.cursor() as cursor:
            cursor.execute(query)
            table = cursor.fetchall()

        print(format_report(table))

    print('\n=== End of report ===')


if __name__ == '__main__':
    main()
