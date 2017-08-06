#!/usr/bin/env python3

from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, cophenet, to_tree
import numpy as np
import json
import sys

SHOWPLOT = int(sys.argv[1])

with open('matrix') as f:
    matrixNetwork = json.load(f)

matrixNetwork = np.array(matrixNetwork)
compressedMatrixNetwork = matrixNetwork[np.triu_indices(len(matrixNetwork), 1)]

hcMethods = ['single', 'complete', 'average', 'weighted', 'centroid', 'median', 'ward']
# centroid, median, ward will only work if euclidean distance is used that is an embedding of distances between parsetrees is possible in k-dim vector space with l2 norm
mx = 0.0
method = 'single'
for method_ in hcMethods:
    linked = linkage(compressedMatrixNetwork, method_)
    coph_var, _ = cophenet(linked, compressedMatrixNetwork)
    if mx < coph_var:
        mx = coph_var
        method = method_

if method in ['centroid', 'median', 'ward']:
    print('** [warning] ' + method + ' method will work only when euclidean distance exists for set of points')

print(method, mx)

def fancy_dendrogram(*args, **kwargs):
    max_d = kwargs.pop('max_d', None)
    if max_d and 'color_threshold' not in kwargs:
        kwargs['color_threshold'] = max_d
    annotate_above = kwargs.pop('annotate_above', 0)

    ddata = dendrogram(*args, **kwargs)

    if not kwargs.get('no_plot', False):
        plt.title('Dendrogram for matrixNetwork')
        plt.xlabel('cluster size')
        plt.ylabel('distance')
        for i, d, c in zip(ddata['icoord'], ddata['dcoord'], ddata['color_list']):
            x = 0.5 * sum(i[1:3])
            y = d[1]
            if y > annotate_above:
                plt.plot(x, y, 'o', c = c)
                plt.annotate("%.3g" % y, (x, y), xytext = (0, -5),
                             textcoords = 'offset points',
                             va = 'top', ha='center')

        if max_d:
            plt.axhline(y = max_d, c = 'k')
    return ddata

linked = linkage(compressedMatrixNetwork, method)
#plt.figure(figsize=(25,10))
#plt.title('Dendrogram for Matrix')
#plt.xlabel('codes')
#plt.ylabel('distance')
dend = fancy_dendrogram(linked,
                        leaf_rotation = 90,
                        leaf_font_size = 8,
                      # truncate_mode = 'lastp',
                      # p = 12,
                        show_contracted = True,
                        annotate_above = 1000,
                        max_d = 600)

if SHOWPLOT == 1:
    plt.show()

hierarchicalTree = to_tree(linked)

clusters = [(i, -1) for i in range(0, len(matrixNetwork))]
outliers = []
clusterCount = 0
thresholdDist = 700.0
thresholdCount = (4, 15) # (min, max)

def assign(rootnode):
    if rootnode is None:
        return
    elif rootnode.count == 1:
        clusters[rootnode.id] = (rootnode.id, clusterCount)
    else:
        assign(rootnode.left)
        assign(rootnode.right)

def markAsOutlier(rootnode):
    if rootnode is None:
        return
    elif rootnode.count == 1:
        outliers.append(rootnode.id)
    else:
        markAsOutlier(rootnode.left)
        markAsOutlier(rootnode.right)

def dfs(rootnode, parentnode = None):
    global clusterCount
    if rootnode is None:
        return
    elif rootnode.count >= 1 and rootnode.count <= 3:
        if parentnode is not None and parentnode.dist >= thresholdDist:
            markAsOutlier(rootnode)
        else:
            assign(rootnode)
            clusterCount += 1
    elif rootnode.count >= thresholdCount[0] and rootnode.count <= thresholdCount[1]:
        assign(rootnode)
        clusterCount += 1
        if parentnode.dist >= thresholdDist:
            print("[warning] a cluster was made before thresholdDist")
    else:
        dfs(rootnode.left, rootnode)
        dfs(rootnode.right, rootnode)

dfs(hierarchicalTree)

print(clusterCount)
print(thresholdDist, thresholdCount)
print(clusters)
print(outliers)

for i in outliers:
    clusters[i] = (i, clusterCount)

with open('hierarchicalClusters', 'w') as f:
    f.write(', '.join(map(str, clusters)))
