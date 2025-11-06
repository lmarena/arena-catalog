#!/usr/bin/env python3
"""
Script to find models in results.pkl that are missing from scatterplot-data.json

This helps identify which models need pricing data added to the scatterplot.
"""

import json
import pandas as pd

# Load the pickle file
print("Loading results.pkl...")
battle_info = pd.read_pickle("results.pkl")

# Extract all unique model names from all arena types
all_models = set()

for arena_type in ["text", "vision", "text_to_image"]:
    if arena_type not in battle_info:
        print(f"Warning: {arena_type} not found in pickle file")
        continue

    print(f"\nProcessing {arena_type} arena...")
    for category_name, category_data in battle_info[arena_type].items():
        if "leaderboard_table_df" in category_data:
            df = category_data["leaderboard_table_df"]
            # Model names are in the index
            models = df.index.tolist()
            all_models.update(models)

print(f"\n{'='*60}")
print(f"Total unique models in pickle file: {len(all_models)}")

# Load scatterplot-data.json
print("\nLoading scatterplot-data.json...")
with open("data/scatterplot-data.json", "r") as f:
    scatterplot_data = json.load(f)

# Extract model API names from scatterplot data
scatterplot_models = set()
for model_info in scatterplot_data:
    scatterplot_models.add(model_info["model_api_name"])

print(f"Total models in scatterplot-data.json: {len(scatterplot_models)}")

# Find models in pickle but not in scatterplot
missing_models = all_models - scatterplot_models

if not missing_models:
    print("✓ All models from results.pkl have pricing data in scatterplot-data.json!")
else:
    # Sort for easier reading
    sorted_missing = sorted(missing_models)

    print(f"\n{'='*60}")
    print(f"Total missing models: {len(missing_models)}")

    # Categorize by arena type
    print(f"\n{'='*60}")
    print("Breakdown by arena type:")
    print(f"{'='*60}")

    for arena_type in ["text", "vision", "text_to_image"]:
        arena_missing = []
        for category_name, category_data in battle_info[arena_type].items():
            if "leaderboard_table_df" in category_data:
                df = category_data["leaderboard_table_df"]
                models = df.index.tolist()
                for model in models:
                    if model in missing_models and model not in arena_missing:
                        arena_missing.append(model)

        if arena_missing:
            print(f"\n{arena_type.upper()} ({len(arena_missing)} missing):")
            for model in sorted(arena_missing):
                print(f"  - {model}")    

# Also check the reverse - models in scatterplot but not in pickle
extra_models = scatterplot_models - all_models

if extra_models:
    print(f"\n{'='*60}")
    print(f"Models in scatterplot-data.json but NOT in data.pkl:")
    print(f"{'='*60}")
    for i, model in enumerate(sorted(extra_models), 1):
        print(f"{i:3d}. {model}")
    print(f"\nTotal: {len(extra_models)}")
    print("(These might be outdated/deprecated models that can be removed)")

print(f"\n{'='*60}")
print("Done!")
