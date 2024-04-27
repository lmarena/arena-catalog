from fastchat.serve.monitor.monitor import build_leaderboard_tab, build_basic_stats_tab, basic_component_values, leader_component_values
from fastchat.utils import build_logger, get_window_url_params_js

import argparse
import glob
import re
import gradio as gr

def load_demo(url_params, request: gr.Request):
    logger.info(f"load_demo. ip: {request.client.host}. params: {url_params}")
    return basic_component_values + leader_component_values

def build_demo(elo_results_file, leaderboard_table_file):
    from fastchat.serve.gradio_web_server import block_css

    text_size = gr.themes.sizes.text_lg
    theme = gr.themes.Base(text_size=text_size)
    theme.set(button_secondary_background_fill_hover="*primary_300", 
              button_secondary_background_fill_hover_dark="*primary_700")
    with gr.Blocks(
        title="Chatbot Arena Leaderboard",
        theme=theme,
        css=block_css,
    ) as demo:
        leader_components = build_leaderboard_tab(
            elo_results_file, leaderboard_table_file, show_plot=True, mirror=True
        )
    return demo

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--share", action="store_true")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()

    logger = build_logger("monitor", "monitor.log")
    logger.info(f"args: {args}")

    elo_result_files = glob.glob("elo_results_*.pkl")
    elo_result_files.sort(key=lambda x: int(x[12:-4]))
    elo_result_file = elo_result_files[-1]

    leaderboard_table_files = glob.glob("leaderboard_table_*.csv")
    leaderboard_table_files.sort(key=lambda x: int(x[18:-4]))
    leaderboard_table_file = leaderboard_table_files[-1]

    demo = build_demo(elo_result_file, leaderboard_table_file)
    demo.launch(share=args.share, server_name=args.host, server_port=args.port)