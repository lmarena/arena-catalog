from fastchat.serve.monitor.monitor import build_leaderboard_tab, build_basic_stats_tab, basic_component_values, leader_component_values
from fastchat.utils import build_logger, get_window_url_params_js

import pandas as pd
import argparse
import glob
import re
import os
import csv
import json
import gradio as gr


def load_demo(url_params, request: gr.Request):
    logger.info(f"load_demo. ip: {request.client.host}. params: {url_params}")
    return basic_component_values + leader_component_values


def join_leaderboard_and_pricing(leaderboard_file, pricing_file):
    # Load CSV file and JSON file
    leaderboard_df = pd.read_csv(leaderboard_file)
    # pricing_df = pd.read_csv(pricing_file)
    pricing_csv_file = 'data/pricing_table.csv'
    price_control_merged_ranking_file = 'data/price_control_merged_ranking.csv'

    csvfile = open(pricing_csv_file, 'w')
    with open(pricing_file, 'r') as jsonfile:
        pricing_json = json.load(jsonfile)
        fieldnames = ['model_key', 'source', 'input_token_price', 'output_token_price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in pricing_json:
            info = pricing_json[i]
            writer.writerow({'model_key': i, 'source': info["source"], 'input_token_price': info["input_token_price"], 'output_token_price': info["output_token_price"]})
        

    pricing_df = pd.read_csv(pricing_csv_file)

    # Merge them based on 'key' and 'model_key'
    merged_df = pd.merge(leaderboard_df, pricing_df, left_on='key', right_on='model_key', how='left').fillna('-')
    
    # Convert "input_token_price" and "output_token_price" to numeric, errors='coerce' will convert non-numeric values to NaN
    merged_df['input_token_price'] = pd.to_numeric(merged_df['input_token_price'], errors='coerce')
    merged_df['output_token_price'] = pd.to_numeric(merged_df['output_token_price'], errors='coerce')

    # Calculate the Average Price column as the mean of input and output token prices
    merged_df['average_price'] = pd.to_numeric(merged_df[['input_token_price', 'output_token_price']].mean(axis=1)).fillna("-")
    
    # Drop the 'model_key' and 'source' columns
    merged_df.drop(columns=['model_key', 'source', 'Knowledge cutoff date', 
                            'input_token_price', 'output_token_price'], inplace=True)
    
    merged_df.to_csv('data/intermediate_merged_df.csv', index=False)
    
    # Merge with price_control_merged_ranking
    price_control_df = pd.read_csv(price_control_merged_ranking_file)
    final_merged_df = pd.merge(merged_df, price_control_df, on='key', how='left').fillna('-')
    final_merged_df["Rank_after"] = pd.to_numeric(final_merged_df["Rank_after"], errors="coerce").fillna("-")
    final_merged_df['Rank_after'] = final_merged_df['Rank_after'].apply(lambda x: ('%.15g' % x) if isinstance(x, float) else x)
    
    final_merged_df.drop(columns=['Price_cntrl_score', 'Rank_before', 'elo_rating'], inplace=True)

    # Save the merged dataframe to a new CSV file (temporary)
    final_merged_file = 'data/merged_leaderboard_pricing.csv'
    final_merged_df.to_csv(final_merged_file, index=False)

    return final_merged_file


def build_demo(elo_results_file, leaderboard_table_file, pricing_table_file):
    from fastchat.serve.gradio_web_server import block_css

    text_size = gr.themes.sizes.text_lg
    # load theme from theme.json
    theme = gr.themes.Default.load("theme.json")
    # set text size to large
    theme.text_size = text_size
    theme.set(
        button_large_text_size="40px",
        button_small_text_size="40px",
        button_large_text_weight="1000",
        button_small_text_weight="1000",
        button_shadow="*shadow_drop_lg",
        button_shadow_hover="*shadow_drop_lg",
        checkbox_label_shadow="*shadow_drop_lg",
        button_shadow_active="*shadow_inset",
        button_secondary_background_fill="*primary_300",
        button_secondary_background_fill_dark="*primary_700",
        button_secondary_background_fill_hover="*primary_200",
        button_secondary_background_fill_hover_dark="*primary_500",
        button_secondary_text_color="*primary_800",
        button_secondary_text_color_dark="white",
    )

    # Join leaderboard and pricing table
    merged_leaderboard_file = join_leaderboard_and_pricing(leaderboard_table_file, pricing_table_file)

    with gr.Blocks(
        title="Chatbot Arena Leaderboard",
        theme=theme,
        css=block_css,
    ) as demo:
        leader_components = build_leaderboard_tab(
            elo_results_file, merged_leaderboard_file, arena_hard_file, show_plot=True, mirror=True
        )
    return demo


def extract_date(file_name):
    return re.search(r"\d{8}", file_name).group()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--share", action="store_true")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()

    logger = build_logger("monitor", "monitor.log")
    logger.info(f"args: {args}")

    elo_result_files = glob.glob("data/elo_results_*.pkl")
    elo_result_files.sort(key=lambda x: extract_date(x))
    elo_result_file = elo_result_files[-1]

    leaderboard_table_files = glob.glob("data/leaderboard_table_*.csv")
    leaderboard_table_files.sort(key=lambda x: extract_date(x))
    leaderboard_table_file = leaderboard_table_files[-1]

    # pricing_table_file = 'data/pricing_table.csv'  # Specify your pricing table file here
    pricing_table_file = 'pricing_table.json'  # Specify your pricing table file here

    arena_hard_files = sorted(
        glob.glob("data/arena_hard_auto_leaderboard_*.csv"), key=os.path.getmtime)
    arena_hard_file = arena_hard_files[-1]

    demo = build_demo(elo_result_file, leaderboard_table_file, pricing_table_file)
    demo.launch(share=args.share, server_name=args.host, server_port=args.port)
