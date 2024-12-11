import gradio as gr

def build_visualizer():
    visualizer_markdown = """
    # 🧭 Arena Visualizer
    Data explorer provides interactive tools to explore and draw insights from our leaderboard data. 
    """

    gr.Markdown(visualizer_markdown, elem_id="visualizer_markdown")

    with gr.Tabs() as tabs:
        with gr.Tab("Topic Explorer", id=0):
            topic_markdown = """
            ## *Welcome to the Topic Explorer*
            This tool lets you dive into user-submitted prompts, organized into general categories and detailed subcategories. Using the sunburst chart, you can easily explore the data and understand how different topics are distributed.

            ### How to Use:
            - Hover Over Segments: View the category name, the number of prompts, and their percentage.
            - Click to Explore: 
                - Click on a main category to see its subcategories.
                - Click on subcategories to see example prompts in the sidebar.
            - Undo and Reset: Click the center of the chart to return to the top level.

            Start exploring and discover interesting trends in the data!
            
            """
            gr.Markdown(topic_markdown)

            frame = """
                <iframe width="100%" scrolling="no" style="height: 800px; border: 1px solid lightgrey; border-radius: 10px;" 
                        src="https://storage.googleapis.com/public-arena-no-cors/index.html">
                </iframe>
            """
            gr.HTML(frame)


        with gr.Tab("Price Analysis", id=1):
            price_markdown = """
            ## *Price Control Data Visualizations*
            Below are scatter-plots depicting a model's arena score against its cost effectiveness 
            and output token price.
            """
            gr.Markdown(price_markdown)