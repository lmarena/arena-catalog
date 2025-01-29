# Chatbot Arena Leaderboard Visualizations

### Arena Score v. Cost ($/1M Output Tokens) Scatterplot

To update model prices or add a model to the scatterplot feel free to add to `data/scatterplot-data.json`

For example, if I wanted to add test-model to the scatterplot I would add the following object:

```
{
    "name": "Test Model",
    "model_api_key": "test-model",
    "input_token_price": "1",
    "output_token_price": "10",
    "organization": "Test Organization",
    "license": "Proprietary",
    "price_source": "www.pricesource.com",
    "model_source": "www.modelsource.com",
}
```
