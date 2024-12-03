from flask import Flask, render_template, request, redirect
import pandas as pd
from igraph import *
import igraph as ig
from cairo import *
import numpy as np
from functions import add_edge, add_edge2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

@app.route('/',methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the input data from the form
        input1 = request.form.get('selectedTopic', '')
        if not input1:
            input1 = None

        # Call your main function with the inputs
        main_df = pd.read_csv('data.csv')
        main_df2 = pd.read_csv('data2.csv')

        if input1:
        # Check if selected choice exists in any of the tags in main_df
            matching_rows = main_df[main_df['tags'].apply(lambda x: input1.lower() in map(str.strip, x.lower().split(',')))]

            # Save matching rows to tags_df
            tags_df = matching_rows.copy()

            # Save tags_df as a CSV file
            tags_df.to_csv('tags.csv', index=False)

        if input1:
        # Check if selected choice exists in any of the tags in main_df
            matching_rows = main_df2[main_df2['tags'].apply(lambda x: input1.lower() in map(str.strip, str(x).lower().split(',')))]

            # Save matching rows to tags_df
            tags_df2 = matching_rows.copy()

            # Save tags_df as a CSV file
            tags_df2.to_csv('tags2.csv', index=False)
        # Save the dataframe as a CSV file

        return redirect('/choice')
    else:
        return render_template('index.html')

@app.route('/choice')
def choice():
    return render_template('choice.html')

@app.route('/references')
def references():
    tags_df = pd.read_csv("tags.csv")
    reference_doc = pd.concat([tags_df.loc[:,['id', 'doc_type']].drop_duplicates(), tags_df[tags_df['references'].notna()].loc[:, ['references', 'doc_type']].rename(columns = {'references': 'id'})],axis = 0).sort_values(by=['id'])
    reference_list = list(reference_doc['id'].values)
    doc_list = list(reference_doc['doc_type'].values)
    count = len(reference_list)
    references_graph = Graph(directed=False)
    references_graph.add_vertices(count)
    references_graph.vs['id_reference'] = reference_list
    references_graph.vs['doc_type'] = doc_list
    tags_df[tags_df['references'].notna()].apply(lambda x: add_edge(x, references_graph, reference_list), axis=1)

    reference_df = pd.DataFrame(columns=['Node', 'Degree Centrality'])
    for reference_id in reference_list:

        # Get the index of the reference_id in the graph
        reference_index = references_graph.vs.find(id_reference=reference_id).index

        # Calculate node centrality measures for the reference
        node_degree = references_graph.degree(reference_index)

        # Add the data to the DataFrame
        reference_df = reference_df.append({
            'Node': reference_id,
            'Degree Centrality': node_degree
        }, ignore_index=True)
    reference_df=reference_df.sort_values('Degree Centrality', ascending=False)
    betweenness_df = pd.DataFrame(references_graph.edge_betweenness())
    centrality_dfs = []
    centrality_dfs.append(reference_df.head(10))
    centrality_dfs.append(betweenness_df)

    color_dict = {"Conference": "yellow", 
                  "Journal": "darkblue", 
                  "Repository": "red",
                  np.nan: "pink",
                  'Patent': 'orange',
                  'Other': 'black'}
    x = list(str(i) for i in color_dict.keys())
    y = [5 for i in range(len(x))]
    fig = plt.figure(figsize=(3, 1.5))
    ax1 = plt.axes(frameon=False)
    ax1.axes.get_xaxis().set_visible(False)
    plt.barh(x, y, color=list(color_dict.values()))
    
    references_graph.vs["color"] = [color_dict.get(doc_type, 'black') for doc_type in references_graph.vs["doc_type"]]
    ig_plot_references = ig.plot(references_graph, vertex_size=7)

    ig_plot_references.save("static/references.png")
    ig_plot_references.save("references.png")
    return render_template('references.html', centrality_dfs=centrality_dfs)

@app.route('/author')
def author():
    tags_df = pd.read_csv("tags2.csv")
    author_doc = pd.concat([tags_df.loc[:,['author_id', 'doc_type']].drop_duplicates(), tags_df[tags_df['author_id'].notna()].loc[:, ['author_id', 'doc_type']].rename(columns = {'author_id': 'id'})],axis = 0).sort_values(by=['id'])
    author_list = list(author_doc['id'].values)
    doc_list = list(author_doc['doc_type'].values)
    count = len(author_list)
    author_graph = Graph(directed = False)
    author_graph.add_vertices(count)
    author_graph.vs['id_author'] = author_list
    author_graph.vs['doc_type'] = doc_list
    temp = tags_df[tags_df['author_id'].notna()]
    temp2 = temp
    temp = temp2.apply(lambda x:add_edge2(x,temp,author_graph,author_list),axis=1)
    # Calculate node and edge centrality measures for references_graph
    author_df = pd.DataFrame(columns=['Node_id','Node_name', 'Degree Centrality'])
    
    for author_id in author_list:
        try:
            # Get the index of the author_id in the graph
            author_index = author_graph.vs.find(id_author=author_id).index
            current = tags_df.loc[lambda tags_df:tags_df['author_id'] == author_id]
            # Calculate node centrality measures for the reference
            node_degree = author_graph.degree(author_index)
            current.reset_index(inplace=True)
            print(current)
            print('reset')
            # Add the data to the DataFrame
            author_df = author_df.append({
                'Node_id': author_id,
                'Node_name':current.loc[0,'authors'],
                'Degree Centrality': node_degree
            }, ignore_index=True)
        except:
            print()
    author_df = author_df.sort_values('Degree Centrality',ascending=False)
    author_df = author_df.head(10)

    # Create a DataFrame for display
    
    color_dict = {"Conference": "yellow", 
              "Journal": "darkblue", 
              "Repository": "red",
               np.nan: "pink",
              'Patent': 'orange',
              'Other': 'black'}

    x = list(str(i) for i in color_dict.keys())
    y = [5 for i in range(len(x))]
    fig = plt.figure(figsize = (5,2.5))
    ax1 = plt.axes(frameon=False)
    ax1.axes.get_xaxis().set_visible(False)
    plt.barh(x,y, 
         color = list(color_dict.values()))

    author_graph.vs["color"] = [color_dict.get(doc_type,'black') for doc_type in author_graph.vs["doc_type"]]
    ig_plot=ig.plot(author_graph,
        vertex_size=5)
    ig_plot.save("author.png")
    ig_plot.save("static/author.png")
    return render_template('author.html',author_df = author_df)

if __name__ == '__main__':
    app.run()