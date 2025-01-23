# backend/Dockerfile

# Use a Debian-based Node.js runtime as the base image
FROM node:18-slim

# Install Python and pip along with necessary build tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install Node.js dependencies
RUN npm install

# Copy the rest of the backend code
COPY . .

# Copy Python dependencies and install them
COPY data_processing/requirements.txt /app/data_processing/
RUN pip3 install --no-cache-dir -r /app/data_processing/requirements.txt --break-system-packages

# Copy the Python pipeline script
COPY data_processing/pipeline.py /app/data_processing/

# Expose the backend port
EXPOSE 8000

# Start the backend server
CMD ["npm", "start"]
