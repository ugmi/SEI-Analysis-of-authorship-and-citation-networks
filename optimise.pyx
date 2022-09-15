#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  6 16:37:27 2022

@author: milasiunaite
"""

import networkx as nx
import mysql.connector
from network_stats import citation_network, get_partition
import matplotlib.pyplot as plt
import numpy as np
cimport numpy as np
cimport cython
np.import_array()
DTYPE = float

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

def two_labels():
    from labelling import keywords
    lab = [key for key in keywords]
    cdef Py_ssize_t n_lab
    n_lab = len(lab)
    labels = {}
    cdef short n_labels, i, j
    n_labels = 0
    for i in range(n_lab-1):
        labels[lab[i]] = n_labels
        n_labels = n_labels + 1
        for j in range(i+1,n_lab):
            labels[','.join([lab[i], lab[j]])] = n_labels
            n_labels = n_labels + 1
    labels[lab[n_lab-1]] = n_labels
    return labels


def second(G, labels):
    secondary = {}
    cdef short s, i, j
    for node in G:
        primary = G.nodes[node]['primary']
        s = len(primary.split(','))
        if s > 2:
            sec = []
            sl = primary.split(',')
            for i in range(s-1):
                for j in range(i+1, s):
                    string = ','.join([sl[i], sl[j]])
                    if string in labels:
                        sec.append(string)
                    else:
                        sec.append(sl[j]+','+sl[i])
            secondary[node] = '/'.join(sec)
        elif s == 1:
            secondary[node] = primary
        else:
            if primary in labels:
                secondary[node] = primary
            else:
                sl = primary.split(',')
                secondary[node] = ','.join([sl[1], sl[0]])
    return secondary


def get_comm(G):
    cdef Py_ssize_t n_comm
    partition = get_partition(G, 'leiden')
    n_comm = len(set(partition.values()))
    communities = []
    cdef unsigned int r
    for r in range(n_comm):
        communities.append([])
    for node in partition:
        communities[partition[node]].append(node)
    communities.sort(reverse=True, key=len)
    return communities

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def get_array(labels, secondary, comm):
    cdef Py_ssize_t n, w, l, n_labels, col, q
    n = len(comm)
    n_labels = len(labels)
    cdef np.ndarray temp = np.zeros((n, n_labels), dtype=DTYPE)
    cdef double[:, :] temp_view = temp
    for q in range(n):
        c = secondary[comm[q]].split('/')
        for cpt in c:
            col = labels[cpt]
            temp_view[q, col] = temp_view[q, col] + 1
    for q in range(n-1):
        l = q
        while l >= 0:
            for w in range(n_labels):
                if temp_view[l, w] < temp_view[l+1, w]:
                    temp[[l, l+1]] = temp[[l+1, l]]
                    break
                elif temp_view[l, w] > temp_view[l+1, w]:
                    l = 0
                    break
            l = l - 1
    return temp

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def main():
    G = citation_network()
    print('Citation graph finished.')
    labels = two_labels()
    cdef Py_ssize_t n_labels, total, n_comm
    n_labels = len(labels)
    secondary = second(G, labels)
    total = len(G.nodes)
    communities = get_comm(G)
    n_comm = len(communities)
    print('Calculating the array.')
    cdef np.ndarray arr
    arr = np.zeros((1, n_labels), dtype=DTYPE)
    for r in range(n_comm):
        arr = np.vstack((arr, get_array(labels, secondary, communities[r])))
    print('Array calculated.')
    abbrev = []
    for entry in labels:
        pair = entry.split(',')
        if len(pair) == 1:
            abbrev.append(abb[pair[0]])
        else:
            abbrev.append(','.join([abb[pair[0]], abb[pair[1]]]))
    # Print the heatmap.
    cdef np.ndarray x_ticks
    x_ticks = np.arange(0.5, n_labels, 1)
    plt.figure(figsize=(8.27, 11.69))
    plt.xticks(x_ticks, abbrev, fontsize=7, rotation='vertical')
    plt.ylim(0,total)
    plt.ylabel('Works', fontsize=10)
    plt.title('Composition of communities', fontsize=10)
    plt.pcolormesh(arr, cmap='Greys')
    cdef unsigned long k
    cdef float lw
    k = 0
    for comm in communities:
        if len(comm) < 10:
            lw = 0.025
        else:
            lw = 0.1
        plt.plot([0, n_labels], [k, k], color='red', lw=lw)
        k = k + len(comm)
    plt.savefig('cit_comm_leiden.png')


main()