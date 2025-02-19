# Use Python's official image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Expose the port on which Flask will run
EXPOSE 3001

# Run the Flask application
CMD ["python", "app.py"]
