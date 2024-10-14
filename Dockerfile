# Use the official Python image from the Docker Hub.
FROM python:3.10-slim

# Set the working directory inside the container.
WORKDIR /app

# Install git and any other dependencies needed.
RUN apt-get update && apt-get install -y git && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the working directory.
COPY requirements.txt .

# Install any dependencies specified in requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the working directory.
COPY . .

# Expose the port that Gradio will be running on.
EXPOSE 7860

# Define the command to run the Gradio app. Replace 'app.py' with the entry
# point of your Gradio application if it's named differently.
CMD ["python", "app.py"]