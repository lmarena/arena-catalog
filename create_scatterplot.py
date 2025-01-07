import json
import pandas as pd

""" Restructure pricing data """
# write_to = open('pricing_data_restructured_for_visualizations.json', 'w')

# with open('pricing_table.json', 'r') as jsonfile:
#     all_info = []
#     pricing_json = json.load(jsonfile)
#     for batch in pricing_json:
#         models = list(pricing_json[batch].keys())
#         models_accounted_for = models[:2]
#         # To account for different claude models
#         if batch == 'claude':
#             models_accounted_for = [models[0], models[3]]
#         # To account for different llama models
#         if batch == 'llama':
#             models_accounted_for = [models[1], models[4]]
#         # To grab specific models for yi
#         if batch == "yi":
#             models_accounted_for = [models[0], models[3]]
#         # Grab more gemini models
#         if batch == 'gemini':
#             models_accounted_for = models[:3]
#         # Grab specific qwen models
#         if batch == 'qwen' :
#             models_accounted_for = [models[1], models[2]]
#         # Choose latest model for mistral, reka, glm, qwen2.5, and chatgpt-4o-latest
#         if batch == 'mistral' or batch == 'reka' or batch == 'glm' or batch == 'qwen2.5' or batch == 'chatgpt':
#             models_accounted_for = models[:1]
#         # Choose specific deepseek model so no overlapping
#         if batch == 'deepseek':
#             models_accounted_for = [models[1]]
#         # Disregard glm and gpt models for now (too much overlapping) (& gpt models seem out of date)
#         if batch == 'glm' or batch == "gpt":
#             models_accounted_for = []
#         for model in models_accounted_for:
#             info = {}
#             info["model_key"] = model
#             info["output_token_price"] = pricing_json[batch][model]["output_token_price"]
#             info["batch"] = batch
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

def update_data_with_license(row):
    model_key = row['batch']
    if model_key in ['gpt', 'chatgpt', 'o1', 'gemini', 'yi', 'claude', 'reka', 'qwen']:
        return 'Proprietary'
    return 'Non-proprietary'
pricing_data["license"] = pricing_data.apply(update_data_with_license, axis=1)

""" Graph scatterplot """
import plotly.express as px
import plotly.graph_objects as go

fig = px.scatter(pricing_data[:25], y="score", x="output_token_price", title="Quality vs. Price", labels={
                     "output_token_price": "Output Token Price (USD)",
                     "score": "Arena score", "model_key": "Model", "license": "License"}, color="license", log_x=True, text="model_key")
fig.update_traces(
    textposition="bottom center",  # Change position if needed (e.g., 'top center', 'bottom right')
    textfont=dict(size=15),    # Adjust font size for better readability
    texttemplate='%{text}',   # Control text formatting
    marker=dict(size=9), 
)

fig.update_xaxes(range=[-2.4,
                        2.33])

fig.update_yaxes(range=[1165,
                        1380])
fig.update_layout(
    showlegend=False,
    height=800,  # Set the height to a larger value
    margin=dict(
        l=80,  # Left margin
        r=30,  # Right margin
        t=80,  # Top margin
        b=80   # Bottom margin
    ),
    template="plotly_dark"
)
fig.write_html("figure.html")