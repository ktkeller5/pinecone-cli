import os

import plotly.express as px
import gradio as gr
import pandas as pd
from collections import defaultdict

import pinecone

"""
(Pdb) pp data.describe()
       Category  Name                   URL    $ Raised     Investors Founded                 HQ            Focus
count       540   540                   540         366           382     511                509              540
unique       17   540                   540         203           366      19                217              365
top        Text  Seek  https://www.seek.ai/  $2,000,000  Y Combinator    2021  San Francisco, CA  Writing/Editing
freq        132     1                     1          18             8     106                 75               12
"""

def get_data(num_names_per_category=2):
    # The following code reads the CSV and returns it the way I want it
    data = pd.read_csv('./market_map.csv')
    out = defaultdict(list)
    for category in data['Category'].value_counts().index[:2]:
        random_names = data[data['Category'] == category].sample(num_names_per_category)
        out[category] = random_names['Name'].values.tolist()

    return out


def make_plot(plot_type):
    del plot_type

    pinecone.init(
        api_key=os.getenv('PINECONE_API_KEY'),
        environment=os.getenv('PINECONE_ENVIRONMENT'),
    )
    index = pinecone.Index("vc-content-oracle-big")
    print(index)
    import pdb; pdb.set_trace()

    data = get_data()
    names = []
    parents = []
    for category, names_list in data.items():
        names.extend(names_list)
        parents.extend([category] * len(names_list))

    unique_parents = list(set(parents))
    names += unique_parents
    parents += [''] * len(unique_parents)

    print(names, parents)
    fig = px.treemap(
        names=names,
        parents=parents,
    )
    fig.update_traces(root_color="lightgrey")
    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    print('Done')
    return fig

with gr.Blocks() as demo:
    button = gr.Radio(label="Plot type", choices=['generative AI'], value='scatter_plot')
    plot = gr.Plot(label="Plot")
    button.change(make_plot, inputs=button, outputs=[plot])
    demo.load(make_plot, inputs=[button], outputs=[plot])
    demo.launch()