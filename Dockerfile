# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y gcc git nginx && \
    apt-get clean

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any dependencies specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .


# Conditional copy of /etc/gitconfig and /etc/.git-credentials
RUN if [ -f /etc/gitconfig ]; then cp /etc/gitconfig /etc/gitconfig; fi
RUN if [ -f /etc/.git-credentials ]; then cp /etc/.git-credentials /etc/.git-credentials; fi


# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV FLASK_APP=coupling.main

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Run the application
CMD service nginx start && python -m coupling.main
