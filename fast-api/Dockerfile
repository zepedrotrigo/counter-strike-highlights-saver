# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . /app

# Expose port 8081 for the application
EXPOSE 8081

# Set environment variables for the application
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
