import plotly.graph_objects as go


def visualize_price_control(models, overall_scores, price_control_scores, lower_bound, upper_bound, reverse):
    # Create traces for each model
    fig = go.Figure()

    for i, model in enumerate(models):
        fig.add_trace(go.Scatter(
            x=["Overall", "Overall + Price Control"],
            y=[overall_scores[i], price_control_scores[i]],
            mode='lines+markers',
            name=model,
            line=dict(width=2),
            marker=dict(size=10)
        ))
        # Update layout for aesthetics
    bounds = [lower_bound, upper_bound]
    if reverse:
        bounds = [upper_bound, lower_bound]
    fig.update_layout(
        title="Overall Ranking + Price Control",
        xaxis_title="Category",
        yaxis_title="Performance (Arena Score)",
        xaxis=dict(tickmode='array', tickvals=["Overall", "Overall + Price Control"]),
        yaxis=dict(range=bounds),
        plot_bgcolor='black',
        paper_bgcolor='black',
        title_font=dict(size=20, color='white'),
        font=dict(color='white'),
        legend=dict(font=dict(size=10)),
        width=600,  # Adjust width here to make it narrower
        height=700  # You can adjust the height as well if needed
    )

    # Show the figure
    fig.show()


# +
# import plotly.graph_objects as go

# Ranking change for the top models BEFORE price control is applied
models = [
    "gemini-1.5-pro-exp-0827", "gpt-4o-2024-05-13", "gpt-4o-mini-2024-07-18", "claude-3-5-sonnet-20240620", 
    "gemini-1.5-flash-exp-0827", "llama-3.1-405b-instruct", "gpt-4o-2024-08-06", "gemini-1.5-pro-api-0514",
    "gpt-4-turbo-2024-04-09", "gpt-4-1106-preview"
]
overall_scores = [1299.05, 1286.49, 1274.06, 1270.62, 1270.09, 1266.46, 1262.54, 1259.56, 1257.46, 1251.57]
price_control_scores = [1243.02, 1200, 1283.84, 1188.3, 1296.86, 1214.66, 1192.53, 1208.59, 1156.26, 1148.69]

visualize_price_control(models, overall_scores, price_control_scores, 1140, 1310, False)


# +
# Ranking change for the top models AFTER price control is applied
top_models = ['gemini-1.5-flash-exp-0827', 'gpt-4o-mini-2024-07-18', 'gemini-1.5-flash-api-0514',
 'deepseek-v2-api-0628', 'gemini-1.5-pro-exp-0827', 'athene-70b-0725', 'llama-3.1-70b-instruct',
 'deepseek-coder-v2-0724', 'reka-flash-20240722', 'gemma-2-27b-it']
top_overall_scores = [1270.09, 1274.06, 1227.15, 1220.17, 1299.05, 1248.64, 1248.32, 1216.13, 1199.34, 1218.55]
top_price_control_scores = [1296.857936, 1283.841603, 1261.443247, 1253.151069, 1243.015784, 1241.946454,
 1240.487616, 1239.54148, 1218.872415, 1216.253038]

visualize_price_control(top_models, top_overall_scores, top_price_control_scores, 1190, 1310, False)
# -
# Ranking change with ranking on the y-axis rather than scores

models = ['gemini-1.5-flash-exp-0827', 'gpt-4o-mini-2024-07-18', 'gemini-1.5-flash-api-0514',
 'deepseek-v2-api-0628', 'gemini-1.5-pro-exp-0827', 'athene-70b-0725', 
 'llama-3.1-70b-instruct', 'deepseek-coder-v2-0724', 'reka-flash-20240722', 
 'gemma-2-27b-it']
ranks_before = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
ranks_after = [5, 3, 18, 19, 1, 12, 13, 21, 30, 20]

visualize_price_control(models, ranks_before, ranks_after, 0, 35, True)

models = ['gemini-1.5-flash-exp-0827', 'gpt-4o-mini-2024-07-18', 'gemini-1.5-flash-api-0514',
 'deepseek-v2-api-0628', 'gemini-1.5-pro-exp-0827', 'athene-70b-0725', 
 'llama-3.1-70b-instruct', 'deepseek-coder-v2-0724', 'reka-flash-20240722', 
 'gemma-2-27b-it']
ranks_before = [5, 3, 18, 19, 1, 12, 13, 21, 30, 20]
ranks_after = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
visualize_price_control(models, ranks_before, ranks_after, 0, 35, True)


