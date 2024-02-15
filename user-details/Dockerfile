# # Use an official Python runtime as a parent image
# FROM python:3.10-slim

# # Set the working directory in the container
# # This creates the /app directory if it doesn't exist
# WORKDIR /app

# # Copy the entire project into the container at /app
# # This includes api, helpers, tests, and any other files or directories
# COPY . .

# # Install any needed packages specified in api/requirements.txt
# RUN pip install --no-cache-dir -r api/requirements.txt

# # Make port 5000 available to the world outside this container
# EXPOSE 5000

# # Define environment variable
# ENV PORT=5000

# # Command to run the Flask application
# CMD ["python", "api/app.py"]

# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies for PyODBC
RUN apt-get update \
    && apt-get install -y --no-install-recommends gnupg curl unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    # Clean up
    && apt-get clean \
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

# Command to run the Flask application
CMD ["python", "api/app.py"]

