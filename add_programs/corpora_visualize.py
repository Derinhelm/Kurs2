import xml.dom.minidom
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout

def processNode(graph, parentName, children, idName, idChild):
    for (childId, l_type) in children:
        childName = idName[childId]
        graph.add_node(childName)
        graph.add_edge(parentName, childName, link_type = l_type)
        if childId in idChild.keys():
            processNode(graph, childName, idChild[childId], idName, idChild)

def processOneFile(nameFile):
    doc = xml.dom.minidom.parse(nameFile)
    parent = doc.getElementsByTagName('S')
    graph_list = []
    for item in parent:
        idName = {}
        idChild = {}
        title = ""
        for child in item.getElementsByTagName('W'):  # слова с пробелами пока не учитываем
            (id1, dom, feat, normWord, link_type) = (child.getAttribute('ID'), child.getAttribute('DOM'),
                                                child.getAttribute('FEAT'), child.getAttribute('LEMMA'),
                                                child.getAttribute('LINK'))
            if len(child.childNodes) != 0:
                word = child.childNodes[0].nodeValue
                word = word.lower()
            else:
                word = "None"
            title += " " + word
            name = str(id1) + "_" + word
            idName[id1] = name
            if dom in idChild.keys():
                idChild[dom].append((id1, link_type))
            else:
                idChild[dom] = [(id1, link_type)]
        graph = nx.DiGraph()
        rootId = idChild["_root"][0][0]
        rootName = idName[rootId]
        graph.add_node(rootName)
        processNode(graph, rootName, idChild[rootId], idName, idChild)
        graph_list.append((graph, title))
    return graph_list

def visualize(graph, title):
    #global number_windows
    #number_windows += 1
    fig = plt.figure(0)#(number_windows)
    pos = graphviz_layout(graph, prog='dot')
    x_values, y_values = zip(*pos.values())
    x_max = max(x_values)
    x_min = min(x_values)
    x_margin = (x_max - x_min) * 0.25
    plt.xlim(x_min - x_margin, x_max + x_margin)
    y_max = max(y_values)
    y_min = min(y_values)
    y_margin = (y_max - y_min) * 0.25
    plt.ylim(y_min - y_margin, y_max + y_margin)
    nx.draw(graph, pos, with_labels=True, arrows=False, node_size=200, node_color='w',
            horizontalalignment='center', verticalalignment='top', font_size=14, font_color = 'b')
    grafo_labels = nx.get_edge_attributes(graph, 'link_type')
    nx.draw_networkx_edge_labels(graph, pos, font_size=10, edge_labels=grafo_labels, label_pos=0.5,
                                 rotate=False)
    fig.canvas.draw_idle()
    plt.title(title, fontsize = 10)
    plt.show()

g = processOneFile('Algoritm.tgt')
print(len(g))
for i in range(20):
    visualize(*g[i])