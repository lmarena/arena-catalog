# Chatbot Arena Leaderboard Visualizations

### Generating a scatterplot 

Clone this repository to your local machine and run the following commands to update data: 

#### Create a virtual environment and install requirements
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

#### Update leaderboard data
You will need a data dump named `results.pkl` that you add to your local repository before running the `update_leaderboard_data.py` script. This update is handled by the LMArena team currently and you can check the `data` folder to see the last time the leaderboard data was updated.

```
python update_leaderboard_data.py
```

#### Set up local server and view scatterplot
Run `python -m http.server 8000` to set up a local server and navigate to `localhost:8000/scatterplot.html` to view the rendered plot.

You can also view the scatterplot by running `open scatterplot.html` from the root directory but this will not reflect any local changes made to config files like `scatterplot-data.json` and `visibility-data.json`. 

#### scatterplot-data.json
You can add new models or update pricing information of existing models in this file. Models must be in this file to appear in the scatterplot. 

#### visiblity-data.json
Tweak this file to control which models receive labels on the scatterplot and what direction (left / right) they show up in.

### Arena Score v. Cost Scatterplot

To update model prices or add a model to the Arena Score v. Cost scatterplot at feel free to add to `data/scatterplot-data.json`

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
