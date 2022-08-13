#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 22:53:13 2022

@author: milasiunaite
"""

import networkx as nx
import mysql.connector
import labelling as lb
import stat_fig as sf


def label_counts(G):
    """
    Print how many nodes have one, two, three or multiple labels.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Graph whose properties we need to describe.

    Returns
    -------
    None.

    """
    counts = {'NONE': 0}
    multiple_level1 = 0
    two_labels = 0
    three_labels = 0
    more_than_three = 0
    for key in lb.keywords:
        counts[key] = 0
    counts_total = counts.copy()
    counts_single = counts.copy()
    for n in G:
        labels = G.nodes[n]['primary'].split(',')
        m = len(labels)
        if m > 1:
            if m > 3:
                more_than_three += 1
            elif m == 3:
                three_labels += 1
            elif m == 2:
                two_labels += 1
            for lab in labels:
                counts_total[lab] += 1
            if sum([lab in labels for lab in lb.concepts_level1]) > 1:
                multiple_level1 += 1
        else:
            counts_total[labels[0]] += 1
            counts_single[labels[0]] += 1
    multiple_total = two_labels + three_labels + more_than_three
    print('Works that have a single label:', len(G.nodes)-multiple_total)
    print('Works that have two labels:', two_labels)
    print('Works that have three labels:', three_labels)
    print('Works that have more than three labels:', more_than_three)
    print('Works that have more than one label:', multiple_total)
    # print('Works that have more than one level 1 label:', multiple_level1)
    # print('Works that have only one label:', counts_single)
    # print(counts_total)
    return


def citation_network():
    """
    Generate citation network using tha data from the database.

    Returns
    -------
    G : nx.DiGraph
        Citation network.

    """
    counts = {}
    for key in lb.keywords:
        counts[key] = 0
    # Initiate citation network.
    G = nx.DiGraph()
    # Add nodes to the graph and label them.
    nodes = set()
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='RunTheNum6!',
        database='draft',
        auth_plugin='mysql_native_password',
    )
    mycursor = mydb.cursor()
    mycursor.execute('SELECT id, title, concepts FROM works')
    temp = list(mycursor.fetchall())
    nodes = [ele[0] for ele in temp]
    G.add_nodes_from(nodes)
    lb.label_nodes(G, temp)
    # Add edges to the graph.
    edges = set()
    cit = {}
    mycursor.execute(
        'SELECT id, openalex_id, cited_ids, cited_by_count, author_ids FROM works')
    temp = list(mycursor.fetchall())
    mycursor.close()
    for entry in temp:
        # This dictionary converts openalex_id to a corresponding id,
        # which is a unique number.
        cit[entry[1]] = entry[0]
        G.nodes[entry[0]]['number_of_authors'] = len(entry[4].split(','))
    for entry in temp:
        cited = entry[2].split(',')
        for ele in cited:
            try:
                edges.add((entry[0], cit[ele]))
            except KeyError:
                # Ignore cited works that are not in the database,
                # that is, those that are outside relevant subfields.
                continue
    G.add_edges_from(edges)
    # Remove nodes that are neither cited nor cite other works.
    G_copy = G.copy()
    for n in G_copy:
        if G.nodes[n]['primary'] == 'NONE' or G.in_degree(n) + G.out_degree(n) == 0:
            G.remove_node(n)
    return G


def coauthorship_network(citN):
    """
    Generate co-authorship network using tha data from the database.

    Parameters
    ----------
    citN : nx.DiGraph
        Citation network.

    Returns
    -------
    G : nx.Graph
        Co-authorship network.

    """
    edges, nodes = set(), set()
    ad, paper_count, author_concepts, edge_weights, counts = {}, {}, {}, {}, {}
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='RunTheNum6!',
        database='draft',
        auth_plugin='mysql_native_password',
    )
    mycursor = mydb.cursor()
    mycursor.execute('SELECT author_id, alt_id FROM authors')
    strings = mycursor.fetchall()
    # Make a dictionary to convert author id to alternative id.
    for t in strings:
        ad[str(t[0])] = str(t[1])
    mycursor.execute('SELECT id, author_ids FROM works')
    strings = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    for key in lb.keywords:
        counts[key] = 0
    for string in strings:
        try:
            cpts = citN.nodes[string[0]]['primary'].split(',')
        except KeyError:
            # Ignore works that were removed.
            continue
        authors = string[1].split(',')
        authors = [ad[auth] for auth in authors if auth != '']
        authors.sort()
        for i in range(len(authors)):
            if authors[i] not in nodes:
                nodes.add(authors[i])
                paper_count[authors[i]] = 1
                author_concepts[authors[i]] = counts.copy()
            else:
                paper_count[authors[i]] += 1
            for j in range(i+1, len(authors)):
                if (authors[i], authors[j]) in edges:
                    # The more papers two people co-author,
                    # the higher the edge weight between them.
                    edge_weights[(authors[i], authors[j])] += 1
                else:
                    edges.add((authors[i], authors[j]))
                    edge_weights[(authors[i], authors[j])] = 1
            for c in cpts:
                author_concepts[authors[i]][c] += 1
    # Initiate co-authorship network, add nodes and edges.
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    nx.set_edge_attributes(G, edge_weights, 'weight')
    nx.set_node_attributes(G, paper_count, 'papers_published')
    # Remove slef-loop edges.
    G.remove_edges_from(nx.selfloop_edges(G))
    # Label the nodes.
    attributes = {}
    for entry in author_concepts:
        td = author_concepts[entry]
        attributes[entry] = ''
        for entr in td:
            if td[entr] > 0:
                attributes[entry] = attributes[entry] + ',' + entr
        attributes[entry] = attributes[entry].strip(',')
    nx.set_node_attributes(G, attributes, 'primary')
    return G


def get_partition(G, algorithm):
    """
    Generate a partition of the network using community detection algorithms.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph
        Graph whose properties we need to describe.
    algorithm : string
        Name of the algorithm to apply.

    Returns
    -------
    partition : dict
        Partition of the network. Node as key, group id as value.

    """
    partition = {}
    directed = nx.is_directed(G)
    if directed:
        # Treat citation network as undirected,
        # since community detection algorithms do not work on directed graphs.
        uG = nx.to_undirected(G)
        weight = None
    else:
        uG = G.copy()
        weight = 'weight'
    # Get the connected components of the network.
    components = [comp for comp in nx.connected_components(uG)]
    components.sort(reverse=True, key=len)
    last_index = 0
    # Apply community detection algorithm on each component separately.
    if algorithm == 'louvain':
        from community import best_partition
        for comp in components:
            ins = nx.induced_subgraph(uG, comp)
            part = best_partition(ins)
            for ele in part:
                part[ele] += last_index
            partition.update(part)
            last_index = max(part.values()) + 1
    elif (algorithm == 'infomap' or
            algorithm == 'leiden_CPM' or algorithm == 'leiden'):
        import igraph as ig
        for comp in components:
            iG = ig.Graph.from_networkx(nx.induced_subgraph(uG, comp))
            if len(iG.vs['primary']) > 1:
                if algorithm == 'leiden':
                    groups = iG.community_leiden(
                        objective_function='modularity', weights=weight,
                        resolution_parameter=0.1, n_iterations=5)
                elif algorithm == 'leiden_CPM':
                    groups = iG.community_leiden(
                        objective_function='CPM', weights=weight,
                        resolution_parameter=0.02, n_iterations=5)
                else:
                    groups = iG.community_infomap(edge_weights=weight, trials=5)
                for c in groups:
                    for n in c:
                        partition[iG.vs[n]['_nx_name']] = last_index
                    last_index += 1
            else:
                partition[iG.vs['_nx_name'][0]] = last_index
                last_index += 1
    return partition


def main():
    # Citation network
    citG = citation_network()
    # Print info about the size of the network
    print('Citation Network')
    print('Number of nodes:', citG.order())
    print('Number of edges:', citG.number_of_edges())
    # The above is also the total number of indegrees/outdegrees.
    # Print simple stats about the network.
    if False:
        label_counts(citG)
        sf.pub_per_year(citG, y=5)
        acc, deg_out, deg_in = sf.props_per_cpt(citG)
        sf.graph_stats(citG, name='outdegree', plot=True)
        print('Outdegrees in each concept')
        sf.print_table(deg_out)
        sf.graph_stats(citG, name='indegree', plot=True)
        print('Indegrees in each concept')
        sf.print_table(deg_in)
        sf.graph_stats(citG, name='number of authors per paper', plot=True)
        print('Number of authors per paper in each concept')
        sf.print_table(acc)
    # Coauthorship network
    coG = coauthorship_network(citG)
    # Print info about the size of the network
    print('\nCo-authorship network')
    print('Number of nodes:', coG.number_of_nodes())
    print('Number of edges:', coG.number_of_edges())
    # Print simple stats about the network.
    if False:
        ppp, deg = sf.props_per_cpt(coG)
        sf.graph_stats(coG, name='degree', plot=True)
        print('Node degrees in each concept')
        sf.print_table(deg)
        sf.graph_stats(coG, name='papers per author', plot=True)
        print('Number of papers per author in each concept')
        sf.print_table(ppp)
        print('Frequency of collaboration')
        sf.graph_stats(coG, name='edge weight', plot=True)
        sf.correlation_plot(
            x=[d for n, d in coG.degree()], xlabel='Node degree',
            y=[weight for u, weight in coG.nodes.data("papers_published")],
            ylabel='Number of papers published')
    # Partition the network.
    # Print simple stats and the heatmap relating to the partition.
    if False:
        part = get_partition(coG, algorithm='louvain')
        sf.comm_heatmap(coG, part)
    return


if __name__ == '__main__' or __name__ == 'builtins':
    main()
