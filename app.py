from fastchat.serve.monitor.monitor import build_leaderboard_tab, build_basic_stats_tab, basic_component_values, leader_component_values
from fastchat.utils import build_logger, get_window_url_params_js

import argparse
import glob
import re
import os
import gradio as gr


def load_demo(url_params, request: gr.Request):
    logger.info(f"load_demo. ip: {request.client.host}. params: {url_params}")
    return basic_component_values + leader_component_values

def build_demo(elo_results_file, leaderboard_table_file):
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

    with gr.Blocks(
        title="Chatbot Arena Leaderboard",
        theme=theme,
        css=block_css,
    ) as demo:
        leader_components = build_leaderboard_tab(
            elo_results_file, leaderboard_table_file, arena_hard_file, show_plot=True, mirror=True
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

    arena_hard_files = sorted(
        glob.glob("data/arena_hard_auto_leaderboard_*.csv"), key=os.path.getmtime)
    arena_hard_file = arena_hard_files[-1]

    demo = build_demo(elo_result_file, leaderboard_table_file)
    demo.launch(share=args.share, server_name=args.host, server_port=args.port)