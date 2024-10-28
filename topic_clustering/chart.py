from fastchat.utils import build_logger

import gradio as gr
import plotly.graph_objects as go
import pandas as pd
import argparse


file_path = "/home/ygtang/arena-leaderboard-v2/topic_clustering/data"
cat_df = pd.read_csv(f"{file_path}/recent_english_category_summary.csv")

def pie_chart():
    fig = go.Figure(go.Pie(
        labels=cat_df['broad_category'].unique(),
        values=cat_df['broad_category_percentage'].unique(),
        text=cat_df['broad_category_count'].unique(),
        hole=.3,  
        hovertemplate="<b>%{label}</b><br>Count: %{text}<br>Percentage: %{value}%",
        textinfo="label",
        textposition='outside'
    ))

    fig.update_layout(
        title="Broad Category Distribution",
    )

    return fig

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--share", action="store_true")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()

    logger = build_logger("monitor", "monitor.log")
    logger.info(f"args: {args}")

    with gr.Blocks() as demo:
        chart = gr.Plot(label="Broad Category Pie Chart")
        demo.load(pie_chart, [], chart)

    demo.launch()