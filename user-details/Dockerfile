# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set noninteractive to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install prerequisites for SQL Server command-line tools and Python application
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    gnupg \
    software-properties-common \
    unixodbc-dev
    screen

# Add Microsoft repository for SQL Server command-line tools
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/msprod.list

# Accept the EULA and install SQL Server command-line tools
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y mssql-tools

# Include SQL Server tools in PATH
ENV PATH="$PATH:/opt/mssql-tools/bin"

# Clean up to keep the container slim
RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the entire project into the container at /app
COPY . .

# Install any needed packages specified in api/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV PORT=5000

# Reset the frontend (optional, for cleanup)
ENV DEBIAN_FRONTEND=

# Command to run the Flask application
CMD ["python", "api/app.py"]
