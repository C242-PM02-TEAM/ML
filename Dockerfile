# Use a lightweight Python base image
FROM python:3.11-slim

# Set a working directory
WORKDIR /app

# Install system dependencies if needed (e.g. for 'dotenv' or others)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the application files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your Flask app runs on
EXPOSE 8080

# Set environment variables
# If you're using dotenv, you can provide environment variables via Cloud Run environment settings.
ENV PORT=8080

# Run the Flask app
CMD ["python", "app.py"]
