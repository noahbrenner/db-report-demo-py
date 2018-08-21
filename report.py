#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2


DB_NAME = 'news'


def popular_articles_query(limit=None):
    return """
        SELECT title, format('%s views', count(*)) AS views
            FROM log
                JOIN articles ON log.path = ('/article/' || articles.slug)
            GROUP BY articles.title
            ORDER BY count(*) DESC
            LIMIT {number};
    """.format(number=limit or 'ALL')


def popular_authors_query(limit=None):
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


reports = [
    ('Three most popular articles', popular_articles_query(3)),
    ('Most popular article authors', popular_authors_query()),
    ('Days with more than 1% HTTP error rate', days_with_errors_query()),
]


def format_report(table):
    col_widths = tuple(max(map(len, column)) for column in zip(*table))
    row_format = '{:<%s} - {:>%s}' % col_widths

    return '\n'.join(row_format.format(*row) for row in table)


def main():
    print('=== Report for database: {} ==='.format(DB_NAME))

    heading_format = '\n{indent}{{heading}}:\n'.format(indent=' ' * 3)

    for heading, query in reports:
        print(heading_format.format(heading=heading))

        with psycopg2.connect(database=DB_NAME) as db, db.cursor() as cursor:
            cursor.execute(query)
            table = cursor.fetchall()

        print(format_report(table))

    print('\n=== End of report ===')


if __name__ == '__main__':
    main()
