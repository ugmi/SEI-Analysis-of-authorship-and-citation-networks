#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 20:04:19 2022

@author: milasiunaite
"""

import networkx as nx
import labelling as lb
# import stat_fig as sf
import network_stats as ns
import numpy as np
import pandas as pd
import holoviews as hv
from holoviews import opts, dim
import matplotlib.pyplot as plt


def second(G, labels):
    """
    Assign each node a secondary label.

    Secondary label is the same as primary if the node had only one such label,
    a pair of primary labels if it had two,
    and all possible pairs of labels if it had more than two primary labels.

    Parameters
    ----------
    G : nx.DiGraph
        Citation network.
    labels : dict
        Keys are labels, values are label ids.

    Returns
    -------
    secondary : dict
        Keys are nodes, values are secondary labels.

    """
    secondary = {}
    for n in G:
        primary = G.nodes[n]['primary']
        s = len(primary.split(','))
        if s > 2:
            sec = []
            sl = primary.split(',')
            for i in range(s-1):
                for j in range(i+1, s):
                    string = sl[i]+','+sl[j]
                    if string in labels:
                        sec.append(string)
                    else:
                        sec.append(sl[j]+','+sl[i])
            secondary[n] = '/'.join(sec)
        elif s == 1:
            secondary[n] = primary
        else:
            if primary in labels:
                secondary[n] = primary
            else:
                sl = primary.split(',')
                secondary[n] = sl[1] + ',' + sl[0]
    return secondary


def abbreviations(labels):
    """
    Abbreviate the labels. Return dictionary with abbreviated labels.

    Parameters
    ----------
    labels : dict
        Keys are labels, values are label ids.

    Returns
    -------
    abbrev : dict
        Keys are abbreviated labels, values are label ids.

    """
    abb = {
        'particle swarm optimization': 'PSO',
        'evolutionary algorithms': 'EA',
        'ant colony optimization': 'ACO',
        'differential evolution': 'DE',
        'cuckoo search': 'Cuckoo',
        'harmony search': 'Harmony',
        'bat algorithm': 'Bat',
        'firefly algorithm': 'FA',
        'artificial bee colony': 'ABC'
    }
    abbrev = {}
    for entry in labels:
        pair = entry.split(',')
        if len(pair) == 1:
            abbrev[abb[pair[0]]] = labels[entry]
        else:
            abbrev[abb[pair[0]]+','+abb[pair[1]]] = labels[entry]
    return abbrev


def to_from_w_labels(G):
    """
    Get a dictionary of node labels, as well as three other dictionaries.

    The dictionaries are returned in order shown in the name of the function.

    Parameters
    ----------
    G : nx.DiGraph
        Citation network.

    Returns
    -------
    e_to : dict
        Keys are label ids, values are the total number of citations
        to nodes that have the label.
    e_from : dict
        Keys are label ids, values are the total number of citations
        from nodes that have the label.
    e_w : dict
        Keys are tuples of two label ids.
        Values are the number of citations from nodes that have the first label
        to nodes that have the second label.
    labels : dict
        Keys are labels, values are label ids.

    """
    e_to = {}
    lab = [key for key in lb.keywords]
    n_lab = len(lab)
    labels = {}
    n_labels = 0
    for i in range(n_lab-1):
        labels[lab[i]] = n_labels
        e_to[n_labels] = 0
        n_labels += 1
        for j in range(i+1, n_lab):
            labels[lab[i] + ',' + lab[j]] = n_labels
            e_to[n_labels] = 0
            n_labels += 1
    labels[lab[n_lab-1]] = n_labels
    e_to[n_labels] = 0
    e_from = e_to.copy()
    n_labels += 1
    secondary = second(G, labels)
    e_w = {}
    for lb1 in labels.values():
        for lb2 in labels.values():
            e_w[(lb1, lb2)] = 0
    for e in G.edges:
        sec1 = secondary[e[0]].split('/')
        sec2 = secondary[e[1]].split('/')
        for el in sec1:
            e_from[labels[el]] += 1
            for le in sec2:
                e_to[labels[le]] += 1
                e_w[(labels[el], labels[le])] += 1
    return e_to, e_from, e_w, labels


def chord_chart(arr, labels, name):
    """
    Print a chord diagram for the given data.

    Parameters
    ----------
    arr : numpy array
        Array containing info about relations between groups.
    labels : list
        List of labels for each group.

    Returns
    -------
    None.

    """
    hv.extension('matplotlib')
    hv.output(fig='svg', size=400)
    links = []
    n_labels = len(labels)
    for i in range(n_labels):
        for j in range(n_labels):
            n = int(round(arr[i, j]*100))
            if n > 10:
                links.append([i, j, n])
    links = pd.DataFrame(links, columns=['source', 'target', 'value'])
    nodes = [[i, labels[i]] for i in range(n_labels)]
    nodes = pd.DataFrame(nodes, columns=['index', 'name'])
    nodes = hv.Dataset(nodes, 'index')
    chord = hv.Chord((links, nodes)).opts(opts.Chord(
        cmap='tab20b', edge_color=dim('source').astype(str), labels='name',
        node_color=dim('index').astype(str)))
    hv.save(chord, filename=name, fmt='svg')
    return


def heatmap_grey(arr, labels, name):
    """
    Print a heatmap for the given array in greyscale.

    Parameters
    ----------
    arr : numpy array
        Array containing data.
    labels : list
        List of row and column labels.

    Returns
    -------
    None.

    """
    n_labels = len(labels)
    ticks = np.arange(0.5, n_labels, 1)
    plt.figure(figsize=(n_labels, n_labels))
    plt.xticks(ticks, labels, fontsize=30, rotation='vertical')
    plt.yticks(ticks, labels, fontsize=30)
    plt.pcolormesh(arr, cmap='Greys')
    for i in range(n_labels):
        for j in range(n_labels):
            if arr[i, j] > 0.25:
                color = 'white'
            else:
                color = 'black'
            plt.annotate(
                str(round(arr[i, j], 2)), xy=(j+0.25, i+0.25), color=color)
    plt.savefig(fname=name, format='svg')
    return


def main():
    citG = ns.citation_network()
    e_to, e_from, e_w, labels = to_from_w_labels(citG)
    n_labels = len(labels)
    abbrev_d = abbreviations(labels)
    abbrev = list(abbrev_d.keys())

    # Calculate array for outgoing citations.
    arr1 = np.empty((n_labels, n_labels), dtype=float)
    for i in range(n_labels):
        n = e_from[i]
        for j in range(n_labels):
            arr1[i, j] = e_w[(i, j)] / n
    heatmap_grey(arr=arr1, labels=abbrev, name='outgoing')
    # Alternatively, the function sf.heatmap can be used to print the heatmap.
    # sf.heatmap(labels=abbrev_d, entries=e_w, sizes=e_from, cat='reg')
    chord_chart(arr=arr1, labels=abbrev, name='out')

    # Calculate array for incoming citations.
    arr2 = np.empty((n_labels, n_labels), dtype=float)
    for i in range(n_labels):
        n = e_to[i]
        for j in range(n_labels):
            try:
                arr2[i, j] = e_w[(j, i)] / n
            except ZeroDivisionError:
                arr2[i, j] = n
    heatmap_grey(arr=arr2, labels=abbrev, name='incoming')
    # Alternatively, the function sf.heatmap can be used to print the heatmap.
    # sf.heatmap(labels=abbrev_d, entries=e_w, sizes=e_to, cat='rev')
    chord_chart(arr=arr2, labels=abbrev, name='in')

    # Print histograms for values in both arrays.
    plt.subplots(figsize=(15, 5))
    plt.subplot(1, 2, 1)
    hout = plt.hist(
        arr1.flatten(), bins=16, range=(0, 0.8), color='navy', edgecolor='skyblue')
    plt.title('Histogram of proportions of outgoing cit.')
    plt.subplot(1, 2, 2)
    hin = plt.hist(
        arr2.flatten(), bins=16, range=(0, 0.8), color='navy', edgecolor='skyblue')
    plt.title('Histogram of proportions of incoming cit.')
    plt.savefig(fname='histograms', format='svg')

    # Calculate array for difference of proportions
    # between outgoing and incoming citations.
    arr = np.empty((n_labels, n_labels), dtype=float)
    for i in range(n_labels):
        for j in range(n_labels):
            try:
                arr[i, j] = e_w[(i, j)] / e_from[i] - e_w[(j, i)] / e_to[i]
            except ZeroDivisionError:
                arr[i, j] = e_w[(i, j)] / e_from[i]
    # Print heatmap.
    ticks = np.arange(0.5, n_labels, 1)
    plt.figure(figsize=(n_labels, n_labels))
    plt.xticks(ticks, abbrev, fontsize=10, rotation='vertical')
    plt.yticks(ticks, abbrev, fontsize=10)
    plt.pcolormesh(arr, cmap='bwr', vmin=-0.5, vmax=0.5)
    for i in range(n_labels):
        for j in range(n_labels):
            if abs(arr[i, j]) > 0.15:
                color = 'white'
            else:
                color = 'black'
            plt.annotate(
                str(round(arr[i, j], 3)), xy=(j+0.25, i+0.5), color=color)
    plt.savefig(fname='diff_heatmap', format='svg')
    plt.close()
    # Print histogram of array values.
    hdiff = plt.hist(
        arr.flatten(), bins=20, range=(-0.5, 0.5), color='navy', edgecolor='skyblue')
    plt.title('Histogram of differences of proportions')
    plt.savefig(fname='hist', format='svg')
    return


if __name__ == '__main__' or __name__ == 'builtins':
    main()
