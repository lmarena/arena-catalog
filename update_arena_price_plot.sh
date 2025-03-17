#!/bin/bash

# Run the Python script
python update_leaderboard_data.py

git add data/leaderboard-data.json

git add data/leaderboard-data-style-control.json

# Get the current date for the commit message
data_data=$(date +"%Y-%m-%d %H:%M:%S")

# Commit with a message including the current date
git commit -m "Update leaderboard data ${data_data}"

# Push to the repository
git push