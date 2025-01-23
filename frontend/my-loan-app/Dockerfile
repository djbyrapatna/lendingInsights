# Stage 1: Build the React application
FROM node:18-alpine AS build

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Ensure vite.config.ts outputs to 'build' directory
# (Assuming you've already set "outDir": "build" in vite.config.ts)

# Build the React app
RUN npm run build

# Stage 2: Serve the build using a lightweight server
FROM node:18-alpine

# Install serve globally
RUN npm install -g serve

# Set the working directory inside the container
WORKDIR /app

# Copy the build output from the build stage
COPY --from=build /app/build ./build

# Expose port 3000
EXPOSE 3000

# Start the static server
CMD ["serve", "-s", "build", "-l", "3000"]
