# Lending Insights
Getting Started  
Follow these steps to set up and run the Lending Insights application locally using Docker.  
  
# 🚀 Prerequisites  
Docker: Ensure you have Docker installed. If not, download it from here.  
Docker Compose: Typically included with Docker Desktop. Verify installation by running:  
```
docker-compose --version  
```
# 📦 Installation
Clone the Repository  

```
git clone https://github.com/your-username/lending-insights.git  
cd lending-insights  
```
# Configure Environment Variables

Create a .env file in the project root to manage sensitive configurations:  
```
touch .env
```
Required .env Content:  

```
DB_HOST=db  
DB_PORT=5432  
DB_USER=your_username  
DB_PASSWORD=your_password  
DB_NAME=loan_evaluator_db  
NODE_ENV=production  
```
# Build and Start Docker Containers

Execute the following command to build the Docker images and start the services in detached mode:  

```
docker-compose up -d --build
```
# Services Included:

Backend: Node.js server with integrated Python data processing.  
Frontend: React application accessible at http://localhost:3000.  
Database: PostgreSQL instance.  
# Verify Everything is Running  
  
Check the status of the containers:  

```
docker-compose ps
```
Expected Output:

```
Name                      Command               State                 Ports
-----------------------------------------------------------------------------------
lendinginsights-backend   "npm start"            Up                    0.0.0.0:8000->8000/tcp
lendinginsights-frontend  "serve -s build -l…"  Up                    0.0.0.0:3000->3000/tcp
lendinginsights-db        "docker-entrypoint.…" Up                    0.0.0.0:5432->5432/tcp
```

# 🖥️ Access the Application
Frontend: Open your browser and navigate to http://localhost:3000 to interact with the application.  
Backend API: Accessible at http://localhost:8000.  
# 🛑 Stopping the Application
When you're done, gracefully shut down the Docker containers:  
```
docker-compose down
```
To remove all containers, networks, and volumes defined in the docker-compose.yml, use:  
  
```
docker-compose down -v  
```
# 📚 Additional Information
Database Initialization: The PostgreSQL database initializes with the required loan_evaluations table using the db/init/init.sql script.  
File Uploads: Uploaded PDFs are stored in the backend/pdfData/ directory and processed by the integrated Python pipeline.  
CORS Configuration: The backend is configured to accept requests from http://localhost:3000.  
Feel free to reach out or open an issue if you encounter any problems during setup. Have Fun! 🎉  
