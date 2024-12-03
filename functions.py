
def add_edge(x,references_graph,reference_list):
    references_graph.add_edge(reference_list.index(x.id),reference_list.index(x.references))
    return x.id,x.references

def add_edge2(x,temp,author_graph,author_list):
    for ind,row in temp.iterrows():
        if row.id == x.id and row.author_id != x.author_id and ind<author_list.index(x.author_id):
            author_graph.add_edge(ind,author_list.index(x.author_id))
    return x.id,x.author_id