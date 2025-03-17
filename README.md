# Chatbot Arena Leaderboard Visualizations

### Arena Score v. Cost Scatterplot

To update model prices or add a model to the Arena Score v. Cost scatterplot feel free to add to `data/scatterplot-data.json`

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

Note: for text2img models, "input_token_price" and "output_token_price" refer to the price per input image and the price per output image.

After adding to `data/scatterplot-data.json` feel free to make a PR and we will get to it promptly!