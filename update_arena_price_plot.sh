#!/bin/bash

# Run the Python script
cd /home/sophie200/arena-catalog

/home/sophie200/miniconda3/bin/python update_leaderboard_data.py

git add data

# Get the current date for the commit message
data_data=$(date +"%Y-%m-%d %H:%M:%S")

# Commit with a message including the current date
git commit -m "Update leaderboard data ${data_data}"

# Push to the repository
git push
