# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port 8080
EXPOSE 8080

# Command to run the application
CMD ["python", "main.py"]
