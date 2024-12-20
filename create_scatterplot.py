import json
import csv
from os import close
import pandas as pd

""" Restructure pricing data """
# write_to = open('pricing_data_restructured_for_visualizations.json', 'w')

# with open('pricing_table.json', 'r') as jsonfile:
#     all_info = []
#     pricing_json = json.load(jsonfile)
#     for batch in pricing_json:
#         models = list(pricing_json[batch].keys())
#         for model in models[:4]:
#             info = {}
#             info["model_key"] = model
#             info["output_token_price"] = pricing_json[batch][model]["output_token_price"]
#             info["organization"] = batch
#             all_info.append(info)

# json.dump(all_info, write_to, indent = 2)

""" Load in data for scatterplot """

with open('pricing_data_restructured_for_visualizations.json', 'r') as file:
    pricing_data = pd.read_json(file)

with open('rankings.json', 'r') as jsonfile:
    rankings_json = pd.read_json(jsonfile)

def update_data_with_rank(row):
  model_key = row['model_key']
  if model_key in rankings_json:
    return rankings_json[model_key]["elo_rating"]
  return None

pricing_data['score'] = pricing_data.apply(update_data_with_rank, axis=1)
pricing_data.dropna(subset=['output_token_price'], inplace=True)
pricing_data.dropna(subset=['score'], inplace=True)

import plotly.express as px
import plotly.graph_objects as go

fig = px.scatter(pricing_data[:30], y="score", x="output_token_price", title="Quality vs. Cost Effectiveness", labels={
                     "output_tokens_per_USD": "# of output tokens per USD (in thousands)",
                     "score": "Arena score"}, color="organization", log_x=True, text="model_key")
fig.update_traces(
    textposition="bottom center",  # Change position if needed (e.g., 'top center', 'bottom right')
    textfont=dict(size=13.2),    # Adjust font size for better readability
    texttemplate='%{text}',   # Control text formatting
)
fig.update_traces(marker=dict(size=8.5))

fig.update_xaxes(range=[-3,
                        2])

fig.update_yaxes(range=[1230,
                        1380])

fig.update_layout(
    height=1000,  # Set the height to a larger value
    margin=dict(
        l=50,  # Left margin
        r=50,  # Right margin
        t=100,  # Top margin
        b=50   # Bottom margin
    )
)
fig.update_layout(template="plotly_dark")
fig.update_layout(
    legend=dict(
        x=0.01,
        y=1,
        traceorder="reversed",
        font=dict(
            size=12,
            color="black"
        ),
        bgcolor="LightSteelBlue",
        bordercolor="White",
        borderwidth=2
    )
)
# fig.update_traces(showlegend=False)
fig.write_html("figure.html")