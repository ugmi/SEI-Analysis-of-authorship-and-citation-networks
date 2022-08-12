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
        # Remove foreign characters from the name
        # and make sure each name starts with a capital letter.
        cap_name = udecode(name.title())
    except AttributeError:
        # No need to do anything if name was an empty string.
        return None
    # Remove trailing whitespace.
    cap_name = cap_name.strip()
    # Examine the name letter by letter.
    for i in range(len(cap_name)-1):
        if cap_name[i] == '-':
            if cap_name[i+1] != ' ' and norm_name[len(norm_name)-1] != ' ':
                # Add space instead of dash if the dash was between names.
                norm_name = norm_name + ' '
        else:
            if cap_name[i+1] == ' ' and cap_name[i] == ' ':
                # Remove multiple spaces.
                continue
            norm_name = norm_name + cap_name[i]
            if cap_name[i+1] == ' ' and cap_name[i].isupper():
                # Add a period after name abbreviation if there was none.
                norm_name = norm_name + '.'
            elif cap_name[i+1] != ' ' and cap_name[i] == '.':
                # Add a space after a period if there was none.
                norm_name = norm_name + ' '
    # Add the final letter to the name.
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
    print('Delete works which are not journal articles, proceedings articles,'
          ' book chapters or books.')
    mycursor.execute(
        'DELETE FROM works WHERE NOT (publication_type="proceedings-article"'
        ' OR publication_type="journal-article" OR publication_type="book"'
        ' OR publication_type="book-chapter")')
    mydb.commit()
    print('Delete works published later than 2022-09-01.')
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
    print('Remove irrelevant data.')
    remove_irr(mydb)
    print('Normalize author names.')
    normalize_authors(mydb)
    print('Set alt ids.')
    set_alt_ids(mydb)
    mydb.close()


if __name__ == '__main__' or __name__ == 'builtins':
    main()
