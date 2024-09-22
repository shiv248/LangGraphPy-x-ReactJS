#!/bin/bash

# Default values
FRONTEND_PORT=3000
RUN_FRONTEND=false
RUN_BACKEND=false
BUILD_FRONTEND=false

# Parse options
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --frontend) RUN_FRONTEND=true ;;              # Command: ./start.sh --frontend
        --backend) RUN_BACKEND=true ;;                # Command: ./start.sh --backend
        --build) BUILD_FRONTEND=true ;;                # Command: ./start.sh --backend --build
        --frontend-port) FRONTEND_PORT="$2"; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
    shift
done

# Function to build the frontend
build_frontend() {
    echo "Building frontend..."
    (cd frontend && npm install && npm run build) || { echo "Frontend build failed"; exit 1; }
}

# Start the frontend
start_frontend() {
    echo "Starting frontend on port $FRONTEND_PORT..."
    (cd frontend && npm start) &
}

# Start the backend
start_backend() {
    echo "Starting backend..."
    uvicorn server:app --host 0.0.0.0 --port 8000
}

# Backend only with or without build
if [ "$RUN_BACKEND" = true ]; then
    if [ "$BUILD_FRONTEND" = true ]; then
        build_frontend                             # Command: ./start.sh --backend --build
    fi
    start_backend                                  # Command: ./start.sh --backend
    exit 0
fi

# Frontend only without building
if [ "$RUN_FRONTEND" = true ]; then
    start_frontend                                 # Command: ./start.sh --frontend
    exit 0
fi

# Default case: Build frontend, start frontend, and then start backend
build_frontend                                     # Command: ./start.sh (no options)
start_frontend
start_backend
