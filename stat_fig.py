#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 11:05:06 2022

@author: milasiunaite
"""
import matplotlib.pyplot as plt
import labelling as lb
import pandas as pd
import numpy as np
from statistics import stdev, mean, mode
import networkx as nx
from tabulate import tabulate


def pub_per_year(G):
    """
    Print diagram which shows how many works were published from 1985 to today.

    Parameters
    ----------
    G : nx.DiGraph
        Citation network.

    Returns
    -------
    None.

    """
    counts = {}
    for key in lb.keywords:
        counts[key] = 0
    # Dictionary to store data.
    pub_counts = {}
    import mysql.connector
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='RunTheNum6!',
        database='draft',
        auth_plugin='mysql_native_password',
    )
    mycursor = mydb.cursor()
    mycursor.execute('SELECT id, publication_date FROM works')
    info = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    for i in range(1985, 2022):
        pub_counts[i] = counts.copy()
    for entry in info:
        pb_year = entry[1].year
        try:
            labels = G.nodes[entry[0]]['primary'].split(',')
            for lab in labels:
                pub_counts[pb_year][lab] += 1
        except KeyError:
            # Ignore removed nodes.
            pass
    c = ['crimson', 'navy', 'pink', 'grey', 'brown', 'orange', 'purple', 'darkgreen', 'black']
    i = 0
    years = list(pub_counts.keys())
    plt.figure(figsize=(25,15))
    for key in counts:
        y = [entr[key] for entr in pub_counts.values()]
        plt.plot(years, y, lw=1, c=c[i], alpha=0.5, label=key, marker='o')
        i += 1
    plt.xlabel('Year')
    plt.ylabel('Number of publications')
    plt.legend()
    return


def correlation_plot(x, y, xlabel, ylabel):
    # Correlation between number of co-authors and number of papers published.
    # Might change later.
    plt.figure(figsize=(max(x) // 20, max(y) // 20))
    ds_x = x.copy()
    ds_y = [e / 2 for e in ds_x]
    plt.axes(xscale='log', yscale='log')
    plt.plot(ds_x, ds_y, lw=1, c='r', alpha=0.5, label='y=x/2')
    plt.scatter(x, y, alpha=0.8, s=2)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.show()
    return


def print_table(data):
    """
    Print table with the statistics for each subfield.

    Parameters
    ----------
    data : dict
        Dictionary containing entries associated with each subfield.

    Returns
    -------
    None.

    """
    info = {}
    # Calculate statistics for each subfield.
    for key in lb.keywords:
        info[key] = {}
        info[key]['average'] = mean(data[key])
        info[key]['stdv'] = stdev(data[key])
        info[key]['total'] = sum(data[key])
        info[key]['size'] = len(data[key])
    # Print table.
    tb = pd.DataFrame(data=info)
    print(tabulate(tb.transpose(), tablefmt='fancy_grid', floatfmt=".3f",
                   headers=['subfield', 'avg', 'stdev', 'total', 'size']))


def props_per_cpt(G):
    """
    Calculate properties of the graph for each subfield.

    If graph is directed, return the information about indegrees, outdegrees,
    number of authors per paper for each subfield.
    If graph is undirected, return the information about idegrees and
    number of papers per author for each subfield.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Graph whose properties we need to describe.

    Returns
    -------
    tuple
        Tuple of dictionaries with data about the properties of the graph.

    """
    directed = nx.is_directed(G)
    if directed:
        # Dictionary for lists of number of authors per paper for each subfield.
        acc = {}
        # Dictionary of lists of node degrees in each subfield.
        cdeg_out, cdeg_in = {}, {}
        for key in lb.keywords:
            acc[key], cdeg_out[key], cdeg_in[key] = [], [], []
        for n in G:
            cpts = G.nodes[n]['primary'].split(',')
            for c in cpts:
                acc[c].append(G.nodes[n]['number_of_authors'])
                cdeg_out[c].append(G.out_degree[n])
                cdeg_in[c].append(G.in_degree[n])
        return (acc, cdeg_out, cdeg_in)
    else:
        # Dictionary of lists of number of papers per person in each subfield.
        ppp = {}
        # Dictionary of lists of node degrees in each subfield.
        cdeg = {}
        for key in lb.keywords:
            cdeg[key], ppp[key] = [], []
        for n in G:
            cpts = G.nodes[n]['primary'].split(',')
            for c in cpts:
                ppp[c].append(G.nodes[n]['papers_published'])
                cdeg[c].append(G.degree[n])
        return (ppp, cdeg)


def graph_stats(G, name, plot=False):
    """
    Print statistics about a certain property of the graph.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Graph whose properties we need to describe.
    name : string
        Name of the property whose statistics we need to calculate.
    plot : bool, optional
        If true, print the bar chart of occurences. The default is False.

    Returns
    -------
    None.

    """
    name = name.casefold()
    if name == 'indegree':
        data = [entr[1] for entr in G.in_degree()]
    elif name == 'outdegree':
        data = [entr[1] for entr in G.out_degree()]
    elif name == 'degree':
        data = [entr[1] for entr in G.degree()]
    elif name == 'edge weight':
        data = [weight for u, v, weight in G.edges.data("weight")]
    elif name == 'node weight':
        data = [weight for u, weight in G.nodes.data("weight")]
    elif name == 'number of authors per paper':
        data = [weight for u, weight in G.nodes.data("number_of_authors")]
    elif name == 'papers per author':
        data = [weight for u, weight in G.nodes.data("papers_published")]
    else:
        return
    data.sort(reverse=True)
    # Print basic stats.
    print('Maximum ' + name + ':', data[0])
    print('Average ' + name + ':', round(mean(data), 3))
    print('Standard deviation:', round(stdev(data), 3))
    print('Mode:', mode(data))
    print('Percentage of nodes that are mode:',
          round(data.count(mode(data))/len(data), 3))
    if plot:
        # Plot bar chart of number of occurences of each value of the property.
        plt.figure(figsize=(15, 15))
        plt.hist(data, bins=data[0])
        plt.title(name.capitalize())
        plt.show()


def stats_sizes(sizes, name='communities', plot=False):
    """
    Print statistics about the sizes of certain objects.

    Parameters
    ----------
    sizes : list
        List of sizes of the objects we examine.
    name : string, optional
        Name of the objects whose sizes we examine. The default is 'communities'.
    plot : bool, optional
        If true, print the bar chart of occurences. The default is False.

    Returns
    -------
    None.

    """
    name = name.casefold()
    sizes.sort(reverse=True)
    print('Number of ' + name + ':', len(sizes))
    print('Average size:', round(mean(sizes), 3))
    print('Standard deviation:', round(stdev(sizes), 3))
    print('Maximum size:', max(sizes))
    print('Minimum size:', min(sizes))
    print('Most frequent size:', mode(sizes))
    print('Percentage of ' + name + ' of this size:',
          round(sizes.count(mode(sizes))/len(sizes), 3))
    if plot:
        plt.figure(figsize=(15, 15))
        plt.hist(sizes, bins=sizes[0])
        plt.title('Sizes of ' + name)
        plt.show()


def comm_heatmap(G, partition, labels=None, name='communities'):
    """
    Print a heatmap.

    Each cell contains the ratio between the number of nodes
    with label in the column and the total number of nodes in the group.
    The larger the ratio, the darker the color.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Graph we are examining.
    partition : dict
        Dictionary keyed by node, whose values are the id of group it belongs to.
    labels : list or None, optional
        The names of groups we examine. The default is None.
    name : string, optional
        Type of partition groups. The default is 'communities'.

    Returns
    -------
    None.

    """
    if labels is None:
        labels = [key for key in lb.keywords]
    n_comm = len(set(partition.values()))
    n_lab = len(labels)
    sizes = {}
    for i in range(n_comm):
        sizes[i] = 0
    arr = np.zeros((n_comm, n_lab), dtype=float)
    for node in partition:
        c = G.nodes[node]['primary'].split(',')
        sizes[partition[node]] += 1
        for cpt in c:
            arr[partition[node], labels.index(cpt)] += 1
    for i in range(n_comm):
        for j in range(n_lab):
            arr[i, j] = arr[i, j] / sizes[i]
    # Sort the array rows. The array will be displayed with the 0-th row
    # at the bottom (not at the top).
    rearr = np.copy(arr)
    for i in range(n_comm-1):
        k = i
        while k > -1:
            for j in range(n_lab):
                if rearr[k, j] < rearr[k+1, j]:
                    rearr[[k, k+1]] = rearr[[k+1, k]]
                    break
                elif rearr[k, j] > rearr[k+1, j]:
                    k = 0
                    break
            k = k - 1
    # Print stats about the objects.
    stats_sizes(list(sizes.values()), plot=True)
    # Print the heatmap.
    x_ticks = np.arange(0.5, n_lab, 1)
    plt.figure(figsize=(150, n_lab*10))
    plt.xticks(x_ticks, labels, fontsize=50, rotation='vertical')
    plt.ylabel(name, fontsize=50)
    plt.pcolormesh(rearr, cmap='Greys')
    plt.title('Composition of ' + name, fontsize=75)
    plt.show()


def heatmap(labels, entries, sizes=None, cat='reg'):
    """
    Print a heatmap.

    Each cell contains the ratio between number of relations between
    the group in the row and the group in the column
    and the total number of relations associated with group in the row.
    Possible relations: incoming and outgoing citations.
    The larger the ratio, the darker the color.

    Parameters
    ----------
    labels : dict
        Keys are labels, values are label/group ids.
    entries : dict
        Entries of each cell. Keys are row and column ids.
    sizes : dict or None, optional
        The sizes of groups, keyed by ids. If 'None', sums of row entries. The default is 'None'.
    cat : string
        The type of heatmap. If 'rev', switch the order of tuples which key 'entries'.
        The default is 'reg'.

    Returns
    -------
    None.

    """
    n_lab = len(labels)
    arr = np.empty((n_lab, n_lab), dtype=float)
    if cat == 'reg':
        for i in range(n_lab):
            if sizes is None:
                n = sum([entries[(i, j)] for j in range(n_lab)])
            else:
                n = sizes[i]
            for j in range(n_lab):
                arr[i, j] = (entries[(i, j)] / n)
    elif cat == 'rev':
        for i in range(n_lab):
            if sizes is None:
                n = sum([entries[(j, i)] for j in range(n_lab)])
            else:
                n = sizes[i]
            for j in range(n_lab):
                try:
                    arr[i, j] = (entries[(j, i)] / n)
                except ZeroDivisionError:
                    arr[i, j] = n
    # Print heatmap.
    ticks = np.arange(0.5, n_lab, 1)
    plt.figure(figsize=(n_lab, n_lab))
    plt.xticks(ticks, list(labels.keys()), fontsize=10, rotation='vertical')
    plt.yticks(ticks, list(labels.keys()), fontsize=10)
    plt.pcolormesh(arr, cmap='Greys')
    for i in range(n_lab):
        for j in range(n_lab):
            if arr[i, j] > 0.5:
                color = 'white'
            else:
                color = 'black'
            plt.annotate(
                str(round(arr[i, j], 2)), xy=(j+0.25, i+0.5), color=color)
    plt.show()
    return


def main():
    return


if __name__ == '__main__' or __name__ == 'builtins':
    main()
