#!/bin/bash

FRONTEND_PORT=3000
BACKEND_PORT=8000

RUN_FRONTEND=false
RUN_BACKEND=false
BUILD_FRONTEND=false

# Parse options
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --frontend) RUN_FRONTEND=true ;;              # Command: ./start.sh --frontend
        --backend) RUN_BACKEND=true ;;                # Command: ./start.sh --backend
        --build) BUILD_FRONTEND=true ;;               # Command: ./start.sh --backend --build
        --frontend-port) FRONTEND_PORT="$2"; shift ;; # Command: ./start.sh --frontend-port 4000
        --backend-port) BACKEND_PORT="$2"; shift ;;   # Command: ./start.sh --backend-port 9000
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
    shift
done

# Function to build the frontend
build_frontend() {
    echo "Building frontend using \`npm run build\`..."
    (cd frontend && npm install && npm run build) || { echo "Frontend build failed"; exit 1; }
}

# Start the frontend
start_frontend() {
    echo "Starting frontend on port $FRONTEND_PORT..."
    FRONTEND_CMD="PORT=$FRONTEND_PORT npm start"
    echo "Command :- cd frontend && $FRONTEND_CMD"
    (cd frontend && npm install && eval "$FRONTEND_CMD")
}

# Start the backend
start_backend() {
    echo "Starting backend on port $BACKEND_PORT..."
    BACKEND_CMD="uvicorn server:app --host 0.0.0.0 --port $BACKEND_PORT --reload"
    echo "Command: $BACKEND_CMD"

    # Execute the command and check for failure
    if ! eval "$BACKEND_CMD"; then
        echo "Backend failed to start, did you 'pip install -r requirements.txt'?"
        exit 1
    fi
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

# Default case: No options provided
echo "No valid options provided. Please use '--frontend' or '--backend' or '--backend --build', optionally with '--backend-port' or '--frontend-port' "
