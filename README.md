# SEI-Analysis-of-authorship-and-citation-networks
Short description of each file below.

### cit_network_charts.py
Primary label pairs are used as labels. Generates heatmap, histogram and chord diagram for outgoing/incoming citations, heatmap and histogram for difference in proportions.

### concepts.csv
Table of concepts and their ids which are used to get data from openalex database.

### filtering.py
Collection of functions to standartize names in the database, identify duplicate author records, and remove irrelevant entries.

### get_data.py
Loads data of concepts specified in the concepts.csv file from the openalex database to local database on the computer.

### labelling.py
Functions to assign primary labels to nodes in a citation network.

### network_stats.py
Program to print basic charts and statistics about co-authorship and citation networks. Primary labels only are considered. Includes functions to create citation and co-authorship networks and get a partition of the set of vertices based on a particular community detedtion algorithm.

### optimise.pyx
Generates community heatmap. Uses [Cython](https://cython.readthedocs.io/en/latest/src/quickstart/overview.html).

### setup.py
In most cases optimise.pyx will need to be compiled before running. This can be done in the terminal using the command shown below.

> python setup.py build_ext --inplace

### stat_fig.py
Collection of functions to print tables, charts and heatmaps for given data.
