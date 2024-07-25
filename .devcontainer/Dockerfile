# Use the specified Python image as a base
FROM --platform=linux/amd64 python:3.10-slim-buster

# Upgrade pip
RUN pip3 install --upgrade pip

# Install necessary packages and Microsoft SQL Server tools
RUN apt-get update && apt-get install -y \
    gnupg2 \
    curl \
    apt-transport-https \
    jq && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

# Copy the requirements.txt file into the image
COPY requirements.txt /requirements.txt
COPY pytest_requirements.txt /pytest_requirements.txt
# Install the Python dependencies
RUN pip install -r /requirements.txt
RUN pip install -r /pytest_requirements.txt