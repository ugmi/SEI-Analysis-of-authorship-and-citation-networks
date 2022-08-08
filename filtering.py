#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:32:56 2022

@author: milasiunaite
"""

import mysql.connector
from unidecode import unidecode as udecode


def fetch_names(mydb):
    mycursor = mydb.cursor()
    mycursor.execute('SELECT name FROM authors WHERE alt_id=%s', (0,))
    names = mycursor.fetchall()
    mycursor.close()
    return names


def normalize(name):
    norm_name = ''
    try:
        cap_name = udecode(name.title())
    except AttributeError:
        return None
    for i in range(len(cap_name)-1):
        if cap_name[i] == '-':
            if cap_name[i+1] != ' ' and norm_name[len(norm_name)-1] != ' ':
                norm_name = norm_name + ' '
        else:
            norm_name = norm_name + cap_name[i]
            if cap_name[i].isupper() and cap_name[i+1] == ' ':
                norm_name = norm_name + '.'
            elif cap_name[i] == '.' and cap_name[i+1] != ' ':
                norm_name = norm_name + ' '
    norm_name = norm_name + cap_name[len(cap_name)-1]
    return norm_name


def set_alt_ids(mydb):
    mycursor = mydb.cursor()
    # Ensure all entries are unique so that we don't end up going over
    # the same record multiple times.
    names = set(fetch_names(mydb))
    for name in names:
        mycursor.execute(
            'SELECT MIN(author_id) FROM authors WHERE name=%s', name)
        min_id = mycursor.fetchone()
        mycursor.execute(
            'UPDATE authors SET alt_id=%s WHERE name=%s', (min_id[0], name[0]))
        mydb.commit()
    mycursor.close()


def normalize_authors(mydb):
    mycursor = mydb.cursor()
    names = set(fetch_names(mydb))
    for name in names:
        norm_name = normalize(name[0])
        if norm_name is None:
            continue
        elif name[0] != norm_name:
            mycursor.execute(
                'UPDATE authors SET name=%s WHERE name=%s', (norm_name, name[0]))
            mydb.commit()
    mycursor.close()


def remove_irr(mydb):
    mycursor = mydb.cursor()
    print('delete type posted content or other or dissertation or grant'
          ' or component or dataset or monograph')
    mycursor.execute(
        'DELETE FROM works WHERE publication_type="posted-content"'
        ' OR publication_type="other" OR publication_type="dissertation"'
        ' OR publication_type="grant" OR publication_type="component"'
        ' OR publication_type="dataset" OR publication_type="monograph"')
    mydb.commit()
    print('delete type peer-review or report or report-series or journal'
          ' or reference-book or reference-entry')
    mycursor.execute(
        'DELETE FROM works WHERE publication_type="peer-review"'
        ' OR publication_type="report" OR publication_type="report-series"'
        ' OR publication_type="journal" OR publication_type="reference-book"'
        ' OR publication_type="reference-entry"')
    mydb.commit()
    print('delete date later than 2022-09-01')
    mycursor.execute('DELETE FROM works WHERE publication_date'
                     ' BETWEEN "2022-09-01" AND "2030-12-30"')
    mydb.commit()
    mycursor.close()


def main():
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='RunTheNum6!',
        database='draft',
        auth_plugin='mysql_native_password',
    )
    # remove_irr(mydb)
    # print('Normalize author names.')
    # normalize_authors(mydb)
    print('Set alt ids.')
    set_alt_ids(mydb)
    mydb.close()


if __name__ == '__main__' or __name__ == 'builtins':
    main()

"""
print('delete concept cuckoo search and (zoology or brood parasite or art or history)')
mycursor.execute('DELETE FROM works WHERE concepts LIKE "%Cuckoo search%" AND (concepts LIKE "%Zoology%" OR concepts LIKE "%Brood parasite%" OR concepts LIKE "%Art,%" OR concepts LIKE "%History%")')
mydb.commit()
print('delete concept harmony search and (aesthetics or color space or philosophy)')
mycursor.execute('DELETE FROM works WHERE concepts LIKE "%Harmony search%" AND (concepts LIKE "%Aestethics%" OR concepts LIKE "%Color space%" OR concepts LIKE "%Philosophy%")')
mydb.commit()
print('delete date earlier than 1970')
mycursor.execute('DELETE FROM works WHERE publication_date BETWEEN "1700-01-01" AND "1969-12-30"')
mydb.commit()

mycursor.execute('DELETE FROM works WHERE title LIKE "WITHDRAWN%" OR title LIKE "Withdrawal%"')
mydb.commit()
"""
