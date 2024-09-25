#!/bin/bash

FRONTEND_PORT=3000
BACKEND_PORT=8000

RUN_FRONTEND=false
RUN_BACKEND=false
BUILD_FRONTEND=true  # Default to building the frontend

# Parse options
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --frontend) RUN_FRONTEND=true ;;              # Command: ./start.sh --frontend
        --backend) RUN_BACKEND=true ;;                # Command: ./start.sh --backend
        --nobuild) BUILD_FRONTEND=false ;;            # Command: ./start.sh --backend --nobuild
        --frontend-port) FRONTEND_PORT="$2"; shift ;; # Command: ./start.sh --frontend-port 4000
        --backend-port) BACKEND_PORT="$2"; shift ;;   # Command: ./start.sh --backend-port 9000
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
    shift
done

# Check for conflicting options
if [ "$RUN_FRONTEND" = true ] && [ "$RUN_BACKEND" = true ]; then
    echo "ERROR: Cannot run both frontend and backend in same terminal. Please choose one and open a new terminal for the other"
    exit 1
fi

# Function to build the frontend
build_frontend() {
    echo "Building frontend static files using \`npm run build\`..."
    (cd frontend && npm install && npm run build) || { echo "Frontend build failed"; exit 1; }
}

# Start the frontend
start_frontend() {
    echo "Starting frontend on port $FRONTEND_PORT..."
    FRONTEND_CMD="PORT=$FRONTEND_PORT npm start"
    echo "Command: cd frontend && $FRONTEND_CMD"
    (cd frontend && npm install && eval "$FRONTEND_CMD")
}

# Start the backend
start_backend() {
    echo "Starting backend on port $BACKEND_PORT..."
    BACKEND_CMD="uvicorn server:app --host 0.0.0.0 --port $BACKEND_PORT --reload"
    echo "Command: $BACKEND_CMD"

    # Execute the command and check for failure
    if ! eval "$BACKEND_CMD"; then
        echo "Backend failed to start, have you 'pip install -r requirements.txt'?"
        exit 1
    fi
}

# Backend only with or without build
if [ "$RUN_BACKEND" = true ]; then
    if [ "$BUILD_FRONTEND" = true ]; then
        build_frontend                             # Command: ./start.sh --backend
    fi
    start_backend                                  # Command: ./start.sh --backend or ./start.sh --backend --nobuild
    exit 0
fi

# Frontend only
if [ "$RUN_FRONTEND" = true ]; then
    start_frontend                                 # Command: ./start.sh --frontend
    exit 0
fi

# Default case: No options provided
echo "No valid options provided. Please use '--frontend' or '--backend' or '--backend --nobuild', optionally with '--backend-port' or '--frontend-port' "
