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
    lst = set()
    for ab in abbr:
        if title.find(ab) != -1:
            lst.add(abbr[ab])
    ltitle = title.casefold()
    for lab in keywords:
        for key in keywords[lab]:
            if ltitle.find(key) != -1:
                for word in keywords[lab][key]:
                    if ltitle.find(word) != -1:
                        lst.add(lab)
                        break
    return ','.join(lst)


def stage2(concepts):
    lconcepts = concepts.casefold()
    cpts = set(lconcepts.split(','))
    lst = []
    for lab in concepts_level2:
        for key in concepts_level2[lab]:
            if key in cpts:
                lst.append(lab)
                break
    if len(lst) != 0:
        return ','.join(lst)
    for lab in concepts_level1:
        for key in concepts_level1[lab]:
            if key in cpts:
                lst.append(lab)
                break
    return ','.join(lst)


def primary(data):
    res = stage1(data[1])
    if res:
        return res
    res = stage2(data[2])
    if res:
        return res
    return


def label_nodes(G, nodes):
    for ele in nodes:
        pr = primary(ele)
        if pr:
            G.nodes[ele[0]]['primary'] = pr
        else:
            G.nodes[ele[0]]['primary'] = 'NONE'
        # might add secondary labels later
    return


def main():
    G = nx.DiGraph()
    return


if __name__ == '__main__' or __name__ == 'builtins':
    main()
