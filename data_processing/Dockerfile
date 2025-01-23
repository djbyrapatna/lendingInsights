# Use official Python image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the data_processing code
COPY . .

# Expose any necessary ports (if applicable)
# EXPOSE 5000

# Start the data processing pipeline
CMD ["python", "pipeline/main.py"]
