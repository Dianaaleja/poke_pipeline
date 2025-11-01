# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Expose port if needed (for Streamlit or Flask apps)
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the pipeline
CMD ["python", "app.py"]
