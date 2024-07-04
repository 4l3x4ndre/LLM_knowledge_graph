import streamlit as st
from datetime import datetime
import plotly.graph_objs as go
import networkx as nx


def convert_string_data(file_content:list[str]) -> list[dict]:
    """
    Params:
    file_content: relations line by line

    Returns:
    dict of relations
    """
    data = []
    for line in file_content:
        parts = line.split(' -> ')
        if len(parts) != 3:
            continue
        subject, predicate, obj = parts
        data.append({
            'subject': {'name': subject.strip()},
            'predicate': predicate.strip(),
            'object': {'name': obj.strip()}
        })
    return data

# Load data from file
def open_file_data(filename:str) -> list[dict]:
    """
    Open the file of relations and returns its data.
    Params:
    filename: with the extension and correct location
    """
    with open(filename, 'r') as f:
       file_content = f.readlines() 

    return convert_string_data(file_content)
    

# Preprocess nodes and edges
def preprocess_data(data):
    """
    Joins similar nodes and assigns red color to decomposed links.

    Decomposition happens if the predicat ressembles a node name.
    Thus, in "subject -> predicate -> object", if predicate is a subject/object, it 
    will be decomposed as subject -> prepredicat -> node_name -> postpredicat -> object.
    prepredicat and postpredicat links are assigned the red color to allow the full statement
    to be read in the graph.

    Params:
    data: list(dict), list of links from subject to object

    Returns:
    list, list, list: unique_nodes, updated_edges, edge_colors 
    """
    nodes = set()
    edges = []

    # Extract nodes and edges from data
    for entry in data:
        nodes.add(entry['subject']['name'].lower())
        nodes.add(entry['object']['name'].lower())
        edges.append((entry['subject']['name'].lower(), entry['predicate'].lower(), entry['object']['name'].lower()))

    # Create a mapping for merged nodes
    # The key is the longest node name,
    # the value is the shortest node name.
    merged_nodes = {}
    node_list = list(nodes)

    # Check for substrings and merge nodes
    for i in range(len(node_list)):
        for j in range(len(node_list)):
            if i != j:
                if node_list[i] in node_list[j]:
                    if node_list[i].endswith("\n"):node_list[i].replace("\n", '')
                    merged_nodes[node_list[j]] = node_list[i]
                    
                elif node_list[j] in node_list[i]:
                    if node_list[j].endswith("\n"):node_list[j].replace("\n", '')
                    merged_nodes[node_list[i]] = node_list[j]

    # Update edges based on merged nodes
    updated_edges = []
    edge_colors = []
    for subject, predicate, obj in edges:
        if subject in merged_nodes:
            # eAc -> b -> D 
            # should be A -> e ... cb -> D 
            parts = subject.split(merged_nodes[subject])
            pre_subject = parts[0]
            post_subject = parts[1] if len (parts)> 1 else''
            predicate = pre_subject + ' (s) ' + post_subject + ' ' + predicate

            #st.write(f"{subject} {predicate} {obj} : is subject in  {merged_nodes[subject]}")
            subject = merged_nodes[subject]

        if obj in merged_nodes:
            # A -> b -> cDe
            # should be A -> bc ... d -> D 
            parts = obj.split(merged_nodes[obj])
            pre_obj = parts[0]
            post_obj = parts[1] if len (parts)> 1 else''
            predicate = predicate + ' ' + pre_obj
            if post_obj:
                if obj in merged_nodes[obj]:
                    #st.write(f"{subject} {predicate} - {obj} : obj in  {merged_nodes[obj]}")
                    predicate += ' (o) ' + post_obj
                else:
                    #st.write(f"{subject} {predicate} - {obj} : something exists in {merged_nodes[obj]}")
                    predicate +=  merged_nodes[obj] + ' ' + post_obj


            obj = merged_nodes[obj]

       
        updated_edges.append((subject, predicate, obj))
        edge_colors.append('lightgrey')


    return list(set(merged_nodes.values())), updated_edges, edge_colors




# Convert NetworkX graph to Plotly graph
def nx_to_plotly(nx_graph, edge_colors):
    #pos = nx.spring_layout(nx_graph)
    if nx.is_planar(nx_graph):
        pos = nx.planar_layout(nx_graph)
        #pos = nx.kamada_kawai_layout(nx_graph)
    else:
        pos = nx.kamada_kawai_layout(nx_graph)

    annotations = []
    edge_traces = []
    
    for edge in nx_graph.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        color = edge[2]['color']
        
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            line=dict(width=2, color=color),
            hoverinfo='none',
            mode='lines'
        )
        edge_traces.append(edge_trace)
        
        # Create annotations for arrows
        annotations.append(
            dict(
                ax=x0, ay=y0,
                x=x1, y=y1,
                xref='x', yref='y',
                axref='x', ayref='y',
                showarrow=True,
                arrowhead=2,
                arrowsize=2,
                arrowwidth=1,
                arrowcolor=color
            )
        )
    
    node_x = []
    node_y = []
    node_labels = []
    for node in nx_graph.nodes(data=True):
        x, y = pos[node[0]]
        node_x.append(x)
        node_y.append(y)
        node_labels.append(node[0])  # node[0] is its name
    

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(
            color='DarkSeaGreen'
        ),
        text=node_labels,
        textposition="top center",
        hoverinfo='text',
        textfont=dict(
            family="sans serif",
            size=13,
            color="Black"
        )
    )

    # Changes the positions of the link-label according the the direction of 
    # the links. If -> then text is above otherwise under the arrow. If 
    # arrow is up then text is left to the arrow, otherwise right.
    # (currently position are not changed as +/- are commented)
    pos_x = []
    pos_y = []
    for edge in nx_graph.edges():
        # --> 
        if pos[edge[0]][0] < pos[edge[1]][0]:
            pos_y.append((pos[edge[0]][1] + pos[edge[1]][1]) / 2)# + 0.01)
        else: # <-- 
            pos_y.append((pos[edge[0]][1] + pos[edge[1]][1]) / 2)# - 0.01)

        # Up
        if pos[edge[0]][1] < pos[edge[1]][1]:
            pos_x.append((pos[edge[0]][0] + pos[edge[1]][0]) / 2)# - 0.01)
        else: # Down
            pos_x.append((pos[edge[0]][0] + pos[edge[1]][0]) / 2)# + 0.01)


    edge_trace_text = go.Scatter(
        x=pos_x,
        y=pos_y,
        text=[edge[2]['label'] for edge in nx_graph.edges(data=True)],
        mode='text',
        textposition="middle center",
        hoverinfo='text',
        textfont=dict(
            family="sans serif",
            size=12,
            color="DarkBlue"
        )

    )
    
    return edge_traces + [node_trace, edge_trace_text], annotations


def create_graphs_from_content(file_content:list[str]):
    """
    Creates graph from list of relation.

    Params:
    file_content: list of lines
    """

    parts = [[]] # 0 line in 0 part

    for line in file_content:
        # '---' delimits the fragments/parts of a decomposed document. 
        # If the document is not decomposed, parts will have one item only.
        if '---' in line:
            parts.append([])
        parts[-1].append(line)
    
    index = 0
    for sub_content in parts:
        index += 1
        if len(parts) > 1:
            st.title(f'Part {index}/{len(parts)}')


        # Transform content to data form
        data = convert_string_data(sub_content)

        # Process the data
        unique_nodes, updated_edges, edge_colors = preprocess_data(data)

        # Create a directed graph
        G = nx.DiGraph()

        # Add nodes and edges based on the processed data
        for node in unique_nodes:
            G.add_node(node)
        for i, (subject, predicate, obj) in enumerate(updated_edges):
            G.add_edge(subject, obj, label=predicate, color=edge_colors[i])
        
        
        G_is_planar = nx.is_planar(G)
        # If G is planar, then only one planar graph (that is, G) will be plotted. 
        # If G is not planar, G will be plotted, and each individual connected components
        # will then be plotted. 
        # The mention "full graph:" will only appear if the CC are plotted to guide the user.

        # ----- Full graph -----
        if not G_is_planar: st.write("Full graph:")

        plotly_data, annotations = nx_to_plotly(G, edge_colors)
        fig = go.Figure(data=plotly_data)
        fig.update_layout(showlegend=False, annotations=annotations)
        st.plotly_chart(fig)


        if not G_is_planar: 
            # Connected Component are not plotted if G is planar. 

            # ----- Connected graphs ----
            st.write("Connected graphs:")
            # Plot graphs to streamlit
            for c in nx.connected_components(G.to_undirected()):
                _g = G.subgraph(c)
                # Convert NetworkX graph to Plotly data
                plotly_data, annotations = nx_to_plotly(_g, edge_colors)

                # Create a Plotly figure
                fig = go.Figure(data=plotly_data)
                fig.update_layout(showlegend=False, annotations=annotations)

                # Display Plotly graph in Streamlit
                st.plotly_chart(fig)

       

if __name__ == '__main__':
    create_graphs_from_file('demo_relations.txt')
