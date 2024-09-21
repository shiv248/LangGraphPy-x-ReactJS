##This file will build frontend and copy static files to backend everytime

# Step 1: Build the React frontend
FROM node:16 AS build-frontend

# Set working directory inside the container for the frontend
WORKDIR /app/frontend

# Copy the package.json and package-lock.json (or yarn.lock) to install dependencies
COPY ./frontend/package.json ./frontend/package-lock.json* ./

# Install frontend dependencies
RUN npm install

# Copy the rest of the frontend source code
COPY ./frontend/ ./

# Build the React frontend
RUN npm run build

# Step 2: Set up the FastAPI backend
FROM python:3.9-slim

# Set the working directory for the backend
WORKDIR /app

# Copy the requirements.txt or equivalent for backend dependencies
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code (server.py, etc.) to the working directory
COPY . .

# Copy the React build from the previous build stage
COPY --from=build-frontend /app/frontend/build ./frontend/build

# Expose the default FastAPI port
EXPOSE 8000

# Start the FastAPI server using Uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
