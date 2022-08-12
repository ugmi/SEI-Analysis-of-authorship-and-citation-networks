#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 17:02:47 2022

@author: milasiunaite
"""

import networkx as nx
concepts_level1 = {
    'particle swarm optimization': ['particle swarm optimization',
                                    'multi-swarm optimization'],
    'ant colony optimization': ['ant colony optimization algorithms'],
    'evolutionary algorithms': ['evolutionary algorithm', 'evolutionary programming',
                                'genetic algorithm', 'genetic programming',
                                'evolution strategy']
    }
concepts_level2 = {
    'cuckoo search': ['cuckoo search'],
    'harmony search': ['harmony search'],
    'bat algorithm': ['bat algorithm'],
    'firefly algorithm': ['firefly algorithm'],
    'differential evolution': ['differential evolution'],
    'artificial bee colony': ['artificial bee colony algorithm', 'bees algorithm']
    }
keywords = {
    'particle swarm optimization': {
        'swarm': ['particle swarm', 'particle-swarm',
                                    'multi-swarm', 'multi swarm']},
    'evolutionary algorithms': {
        'evolution': ['evolutionary algorithm', 'program', 'strateg',
                      'evolutionary-based', 'approach', 'evolution algorithm',
                      'evolutionary optimization', 'evolutionary optimisation'],
        'genetic': ['algorithm', 'program']},
    'ant colony optimization': {
        'ant': ['ant colony', 'ant system', 'ant algorithm']},
    'differential evolution': {'differential': ['evolution']},
    'cuckoo search': {'cuckoo': ['search', 'algorithm']},
    'harmony search': {'harmony': ['search', 'algorithm']},
    'bat algorithm': {' bat ': ['algorithm', 'optimiz']},
    'firefly algorithm': {
        'firefly': ['algorithm', 'optimiz', 'metaheuristic', 'technique']},
    'artificial bee colony': {
        'bees ': ['bees colony', 'bees algorithm', 'bees swarm'],
        'bee': ['bee algorithm', 'bee swarm', 'bee colony', 'bee-inspired']}
    }
abbr = {
        'PSO': 'particle swarm optimization',
        'ACO': 'ant colony optimization',
        ' GA ': 'evolutionary algorithms',
        '(GA)': 'evolutionary algorithms',
        'Bat ': 'bat algorithm',
        ' BA ': 'bat algorithm',
        ' BA-': 'bat algorithm',
        '(BA)': 'bat algorithm',
        ' FA ': 'firefly algorithm',
        ' FA-': 'firefly algorithm',
        '-FA ': 'firefly algorithm',
        '(FA)': 'firefly algorithm',
        '(ABC)': 'artificial bee colony',
        ' CS ': 'cuckoo search',
        ' HS ': 'harmony search'
        }


def stage1(title):
    """
    Generate a string of labels based on keywords in the title.

    Parameters
    ----------
    title : string
        Title of the publication.

    Returns
    -------
    string
        String of labels for the publication.

    """
    lst = set()
    # First check if there are any abbreviations in the title.
    for ab in abbr:
        if title.find(ab) != -1:
            lst.add(abbr[ab])
    # Covert to lowercase
    # because the keywords in dictionaries are lowercase.
    ltitle = title.casefold()
    for lab in keywords:
        for key in keywords[lab]:
            if ltitle.find(key) != -1:
                for word in keywords[lab][key]:
                    if ltitle.find(word) != -1:
                        lst.add(lab)
                        # Move to next key
                        break
    return ','.join(lst)


def stage2(concepts):
    """
    Generate a string of labels based on concepts associated with the work.

    Parameters
    ----------
    concepts : string
        String of concepts separated by commas.

    Returns
    -------
    string
        String of labels for the publication.

    """
    # Covert to lowercase
    # because the concepts in dictionaries are lowercase.
    lconcepts = concepts.casefold()
    cpts = set(lconcepts.split(','))
    lst = []
    for lab in concepts_level2:
        for key in concepts_level2[lab]:
            if key in cpts:
                lst.append(lab)
                # Move to next label.
                break
    if len(lst) != 0:
        # If there is at least one level 2 label,
        # we do not consider further labels.
        return ','.join(lst)
    for lab in concepts_level1:
        for key in concepts_level1[lab]:
            if key in cpts:
                lst.append(lab)
                # Move to next label.
                break
    return ','.join(lst)


def primary(data):
    """
    Generate a primary label for the node.

    Parameters
    ----------
    data : list
        List containing node id, title and string of concepts, in this order.

    Returns
    -------
    res : string
        String of labels for the publication.

    """
    res = stage1(data[1])
    if res:
        return res
    res = stage2(data[2])
    if res:
        return res
    return


def label_nodes(G, nodes):
    """
    Label the nodes in the given graph.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Graph whose nodes we need to label.
    nodes : list
        List of lists containing the data associated with the node.

    Returns
    -------
    None.

    """
    for ele in nodes:
        pr = primary(ele)
        if pr:
            G.nodes[ele[0]]['primary'] = pr
        else:
            G.nodes[ele[0]]['primary'] = 'NONE'
    return


def main():
    return


if __name__ == '__main__' or __name__ == 'builtins':
    main()
