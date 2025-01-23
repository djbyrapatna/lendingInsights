# backend/Dockerfile

# Use an official Node.js runtime as the base image
FROM node:18-alpine

# Install Python and pip
RUN apk add --no-cache python3 py3-pip

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install Node.js dependencies
RUN npm install

# Copy the rest of the backend code
COPY . .

# Install Python dependencies
COPY data_processing/requirements.txt /data_processing/
RUN pip3 install --no-cache-dir -r /data_processing/requirements.txt

# Copy the data_processing scripts
COPY data_processing/pipeline.py /data_processing/

# Expose the backend port
EXPOSE 8000

# Start the backend server
CMD ["npm", "start"]
