#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 15:01:12 2022

@author: milasiunaite
"""
import requests
from csv import reader
import mysql.connector
from filtering import normalize


publications = {}
all_ids = set()


def load_to_database(mydb):
    mycursor = mydb.cursor()
    # SQL query to insert a row into the table 'authors'.
    sql_a = 'INSERT INTO authors (openalex_id, name) VALUES (%s, %s)'
    # SQL query to insert a row into the table 'venues'.
    sql_v = ('INSERT INTO venues (openalex_id, venue, issn_l, publisher) '
             'VALUES (%s, %s, %s, %s)')
    # Get the name of each venue.
    mycursor.execute('SELECT venue FROM venues')
    host_ids = set(mycursor.fetchall())
    # Get the openalex_id of each work.
    mycursor.execute('SELECT openalex_id FROM authors')
    auth_ids = set(mycursor.fetchall())
    for entry in publications.values():
        # Check if the info on the venue is already inserted into the table.
        if (entry['host_venue']['display_name'],) not in host_ids:
            # If the name of the venue is too long, crop it.
            if len(entry['host_venue']['display_name']) > 255:
                entry['host_venue']['display_name'] = entry['host_venue']['display_name'][0:255]
            # Tuple of values to insert into the row.
            val_v = (entry['host_venue']['id'], entry['host_venue']['display_name'],
                     entry['host_venue']['issn_l'], entry['host_venue']['publisher'])
            mycursor.execute(sql_v, val_v)
            mydb.commit()
            host_ids.add((entry['host_venue']['display_name'],))
        # Get the unique id of the venue with the required name.
        mycursor.execute('SELECT venue_id FROM venues WHERE venue = %s',
                         (entry['host_venue']['display_name'],))
        host_id = mycursor.fetchall()
        # Concatenation of openalex_ids separated by commas
        # of each work that the entry cites.
        cited_str = ','.join([work for work in entry['referenced_works']])
        # Concatenation of each concept of the entry, separated by commas.
        concept_str = ','.join([cpt['display_name']
                               for cpt in entry['concepts']])
        author_str = ''
        for auth in entry['authorships']:
            if (auth['author']['id'],) not in auth_ids:
                val_a = (auth['author']['id'], normalize(auth['author']['display_name']))
                mycursor.execute(sql_a, val_a)
                mydb.commit()
                auth_ids.add((auth['author']['id'],))
            # Get the unique id of the author with the required name.
            mycursor.execute(
                'SELECT author_id FROM authors WHERE name = %s',
                (normalize(auth['author']['display_name']),))
            try:
                author_str = author_str + ',' + str(mycursor.fetchall()[0][0])
            except IndexError:
                pass
        author_str = author_str.strip(',')
        try:
            if type(host_id) != list:
                host_id = int(host_id)
        except TypeError:
            host_id = None
        if host_id and len(host_id) > 0:
            try:
                host_id = host_id[0][0]
            except IndexError:
                host_id = host_id[0]
            sql_w = ('INSERT INTO works '
                     '(openalex_id, doi, title, publication_type, cited_by_count, '
                     'host_venue_id, author_ids, updated_date, publication_date, '
                     'cited_ids, concepts) '
                     'VALUES (' + '%s, ' * 10 + '%s)')
            val_w = (entry['id'], entry['doi'], entry['title'], entry['type'],
                     entry['cited_by_count'], host_id, author_str, entry['updated_date'],
                     entry['publication_date'], cited_str, concept_str)
        else:
            val_w = (entry['id'], entry['doi'], entry['title'], entry['type'],
                     entry['cited_by_count'], author_str, entry['updated_date'],
                     entry['publication_date'], cited_str, concept_str)
            sql_w = ('INSERT INTO works '
                     '(openalex_id, doi, title, publication_type, cited_by_count, '
                     'author_ids, updated_date, publication_date, cited_ids, concepts) '
                     'VALUES (' + '%s, ' * 9 + '%s)')
        mycursor.execute(sql_w, val_w)
        mydb.commit()
    mycursor.close()


def load(work_info):
    """
    Load the data into a dictionary.

    Parameters
    ----------
    work_info : dictionary
        Information about the work, given as a dictionary.

    Returns
    -------
    None.

    """
    # 
    if ((work_info['id'],) not in all_ids and work_info['doi']
            and not(work_info['is_retracted'] or work_info['is_paratext'])
            and len(work_info['authorships'])):
        try:
            # Remove irrelevant fields.
            work_info.pop('open_access')
            work_info.pop('mesh')
            work_info.pop('abstract_inverted_index')
        except Exception:
            pass
        # Update dictionary.
        publications[work_info['id']] = work_info
        # Update list.
        all_ids.add((work_info['id'],))


def lookup(concept, mydb):
    """
    Use the API to find all the works of a specified concept in openalex. Load them into dictionaries.

    Parameters
    ----------
    concept : string
        The concept id in openalex.

    Returns
    -------
    None.

    """
    publications.clear()
    try:
        # Update the headers to get into the polite pool.
        headers = requests.utils.default_headers()
        headers['User-Agent'] = headers['User-Agent'] + \
            ' mailto:ugne.me@gmail.com'

        # Note down required API address,
        # then use it to find all the works about a given concept.
        next_cursor = '*'
        while next_cursor:
            api = 'https://api.openalex.org/works?filter=concepts.id:' + \
                concept + '&per-page=100&cursor=' + next_cursor
            response = requests.get(api, headers=headers).json()
            if len(response['results']) == 0:
                next_cursor = None
            else:
                # Load the works into dictionaries for later use.
                for entry in response['results']:
                    load(entry)
                # Update cursor.
                next_cursor = response['meta']['next_cursor']
    except requests.RequestException:
        print('RequestException occured.')
    print('LOAD TO DATABASE ' + concept)
    load_to_database(mydb)


def read_concept_file(filename, mydb):
    """
    Read the info on concepts from a csv file. Load found data on each concept.

    Parameters
    ----------
    filename : string
        Name of the file to read the concepts from, with extention '.csv'.

    Returns
    -------
    None.

    """
    with open(filename, mode='rt', encoding='utf8', newline='') as f:
        concept_reader = reader(f, delimiter=',')
        next(concept_reader)  # Skip the header.
        for row in concept_reader:
            (display_name, concept_id) = row
            # find data and load it into dictionaries
            print('LOOKUP ' + row[1])
            lookup(row[1], mydb)


def main():
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='RunTheNum6!',
        database='draft',
        auth_plugin='mysql_native_password',
    )
    mycursor = mydb.cursor()
    mycursor.execute('SELECT openalex_id FROM works')
    all_ids.update(mycursor.fetchall())
    mycursor.close()
    read_concept_file('concepts.csv', mydb)
    mydb.close()


if __name__ == '__main__' or __name__ == 'builtins':
    main()
