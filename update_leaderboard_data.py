from collections import defaultdict
import json, math, gdown
import numpy as np
import pandas as pd
import plotly.express as px
from tqdm import tqdm
import requests
pd.options.display.float_format = '{:.2f}'.format

url = "https://huggingface.co/api/spaces/lmarena-ai/chatbot-arena-leaderboard/tree/main"
response = requests.get(url)

if response.status_code == 200:
    file_data = response.json()
    file_names = [file["path"] for file in file_data if file["type"] == "file" and ".pkl" in file["path"]]
    print("Files found:", file_names)
else:
    print(f"Failed to access API: {response.status_code}")

url = "https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard/resolve/main/" + file_names[-1]
response = requests.get(url)

print(file_names[-1])
with open("data.pkl", "wb") as file:
    file.write(response.content)

battle_info = pd.read_pickle("data.pkl")
deprecated_models = [
    "gemini-1.5-pro-exp-0801",
    "gemini-1.5-pro-api-0409-preview",
    "bard-jan-24-gemini-pro",
    "chatgpt-4o-latest-20240808",
    "gemini-1.5-pro-exp-0827",
    "gemini-1.5-flash-exp-0827",
    "chatgpt-4o-latest-20240903",
]

def recompute_final_ranking(arena_df, use_deprecated=False):
    arena_df = arena_df.copy()
    if not use_deprecated:
        arena_df = arena_df[~arena_df["deprecated"]]
    # Extract the 'rating_q025' and 'rating_q975' columns as NumPy arrays
    q025 = arena_df["rating_q025"].values
    q975 = arena_df["rating_q975"].values

    # Sort the 'rating_q025' array once
    sorted_q025 = np.sort(q025)

    # For each 'rating_q975_a', find the number of 'rating_q025_b' > 'rating_q975_a'
    # Using searchsorted with side='right' to find the insertion point
    # The number of elements greater than 'rating_q975_a' is len(sorted_q025) - insertion_index
    insertion_indices = np.searchsorted(sorted_q025, q975, side="right")
    counts = len(sorted_q025) - insertion_indices

    # Initialize rankings by adding 1 as per the original logic
    rankings = 1 + counts

    # (Optional) If you want to map rankings back to the model names, you can create a Series
    ranking_series = pd.Series(rankings, index=arena_df.index)

    return ranking_series.tolist()


def get_df(battle_info, key):
    df = pd.DataFrame()
    for k in battle_info[key].keys():
        sc = True if "style_control" in k else False
        df2 = battle_info[key][k]["leaderboard_table_df"]
        df2["category"] = k.replace("_style_control", "")
        df2["style_control"] = sc
        df2 = df2.reset_index()
        # rename index
        df2 = df2.rename(columns={"index": "model_name"})

        df2["deprecated"] = False
        df2.loc[df2["model_name"].isin(deprecated_models), "deprecated"] = True
        df2.loc[df2["deprecated"] == False, "final_ranking"] = recompute_final_ranking(df2, use_deprecated=False)
        df2.loc[df2["deprecated"] == True, "final_ranking"] = 0

        df2["final_ranking_deprecated"] = recompute_final_ranking(df2, use_deprecated=True)

        df = pd.concat([df, df2])
    # add a deprecated column to all rows
    # df.loc[df["model"].isin(deprecated_models), "deprecated"] = True
    # df = df.sort_values("rating", ascending=False)

    # print(df.iloc[0])
    return df

df_text = get_df(battle_info, "text")
df_vision = get_df(battle_info, "vision")
df_image = get_df(battle_info, "image")

# Update language data
text_filtered_df = df_text[
    (df_text['style_control'] == False) &
    (df_text['deprecated'] == False)
]
result = (
    text_filtered_df.groupby('category')
    .apply(
        lambda group: {
            category: group[group['model_name'] == category][['rating','rating_q975', 'rating_q025']].iloc[0].to_dict()
            for category in group['model_name']
        }
    )
    .to_dict()
)
with open('data/leaderboard-text.json', 'w') as file:
    json.dump(result, file, indent=4)

text_filtered_df_style_control = df_text[
    (df_text['style_control'] == True) &
    (df_text['deprecated'] == False)
]
result = (
    text_filtered_df_style_control.groupby('category')
    .apply(
        lambda group: {
            category: group[group['model_name'] == category][['rating','rating_q975', 'rating_q025']].iloc[0].to_dict()
            for category in group['model_name']
        }
    )
    .to_dict()
)
with open('data/leaderboard-text-style-control.json', 'w') as file:
    json.dump(result, file, indent=4)

# Update vision data
vision_filtered_df = df_vision[
    (df_vision['style_control'] == False) &
    (df_vision['deprecated'] == False)
]
result = (
    vision_filtered_df.groupby('category')
    .apply(
        lambda group: {
            category: group[group['model_name'] == category][['rating','rating_q975', 'rating_q025']].iloc[0].to_dict()
            for category in group['model_name']
        }
    )
    .to_dict()
)
with open('data/leaderboard-vision.json', 'w') as file:
    json.dump(result, file, indent=4)

vision_filtered_df_style_control = df_vision[
    (df_vision['style_control'] == True) &
    (df_vision['deprecated'] == False)
]
result = (
    vision_filtered_df_style_control.groupby('category')
    .apply(
        lambda group: {
            category: group[group['model_name'] == category][['rating','rating_q975', 'rating_q025']].iloc[0].to_dict()
            for category in group['model_name']
        }
    )
    .to_dict()
)
with open('data/leaderboard-vision-style-control.json', 'w') as file:
    json.dump(result, file, indent=4)

# Update text2img data
image_filtered_df = df_image[
    (df_image['style_control'] == False) &
    (df_image['deprecated'] == False)
]
result = (
    image_filtered_df.groupby('category')
    .apply(
        lambda group: {
            category: group[group['model_name'] == category][['rating','rating_q975', 'rating_q025']].iloc[0].to_dict()
            for category in group['model_name']
        }
    )
    .to_dict()
)
with open('data/leaderboard-image.json', 'w') as file:
    json.dump(result, file, indent=4)