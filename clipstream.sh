#!/bin/bash

LOG_DIR="./logs"
REDIS_PID_FILE="$LOG_DIR/redis.pid"
CELERY_PID_FILE="$LOG_DIR/celery.pid"
DJANGO_PID_FILE="$LOG_DIR/django.pid"
NGINX_PID_FILE="/opt/homebrew/var/run/nginx.pid"

function setup() {
    echo "Setting up ClipStream..."

    # Check platform
    PLATFORM=$(uname)
    echo "Detected platform: $PLATFORM"

    # Install necessary dependencies
    echo "Installing dependencies..."
    if [[ "$PLATFORM" == "Darwin" ]]; then
        brew install wget pcre zlib redis ffmpeg denji/nginx/nginx-full
    elif [[ "$PLATFORM" == "Linux" ]]; then
        sudo apt-get update
        sudo apt-get install -y wget pcre zlib1g-dev redis ffmpeg nginx
    else
        echo "Unsupported platform: $PLATFORM"
        exit 1
    fi

    # Configure Nginx for RTMP (if necessary)
    echo "Configuring Nginx..."
    NGINX_CONF="/opt/homebrew/etc/nginx/nginx.conf"
    if [[ ! -f "$NGINX_CONF" ]]; then
        echo "RTMP module configuration not found. Adding RTMP configuration..."
        cat <<EOT | sudo tee -a "$NGINX_CONF"
rtmp {
    server {
        listen 1935;
        chunk_size 4096;
        application live {
            live on;
            record off;
        }
    }
}
EOT
        sudo nginx -s reload
    fi

    # Python virtual environment setup
    echo "Setting up Python environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
}

function start() {
    echo "Starting ClipStream services..."

#    # Start Redis
#    if pgrep redis-server > /dev/null; then
#        echo "Redis is already running."
#    else
#        redis-server &> "$LOG_DIR/redis.log" &
#        echo $! > "$REDIS_PID_FILE"
#        echo "Redis started."
#    fi
#
#    # Start Celery
#    if pgrep -f "celery" > /dev/null; then
#        echo "Celery is already running."
#    else
#        celery -A "$CELERY_APP" worker --loglevel=info &> "$LOG_DIR/celery.log" &
#        echo $! > "$CELERY_PID_FILE"
#        echo "Celery started."
#    fi

#    # Check for existing Django processes
#    echo "Checking for existing Django processes..."
#    DJANGO_PIDS=$(ps aux | grep "[m]anage.py runserver" | awk '{print $2}')
#    if [[ -n "$DJANGO_PIDS" ]]; then
#        echo "Django is already running with the following PIDs: $DJANGO_PIDS"
#        echo "Ports in use by Django:"
#        lsof -iTCP -sTCP:LISTEN -n | grep manage.py | awk '{print $9}' || echo "No ports found."
#    else
#        # Start Django on the first available port
#        DJANGO_PORT=8000
#        while lsof -iTCP:$DJANGO_PORT -sTCP:LISTEN &> /dev/null; do
#            echo "Port $DJANGO_PORT is in use. Checking what is using it..."
#            lsof -iTCP:$DJANGO_PORT -sTCP:LISTEN || echo "No detailed process information found."
#            echo "Trying port $((DJANGO_PORT + 1))..."
#            DJANGO_PORT=$((DJANGO_PORT + 1))
#        done
#        python manage.py runserver 0.0.0.0:$DJANGO_PORT &> "$LOG_DIR/django.log" &
#        echo $! >> "$DJANGO_PID_FILE"
#        echo "Django started on port $DJANGO_PORT."
#    fi

    # Start Nginx
    if pgrep nginx > /dev/null; then
        echo "Nginx is already running."
    else
        sudo nginx &> "$LOG_DIR/nginx.log"
        echo "Nginx started."
    fi

    echo "All services are now running."
}




function stop() {
    echo "Stopping ClipStream services..."

#    # Stop Redis
#    if [[ -f "$REDIS_PID_FILE" ]]; then
#        if kill "$(cat "$REDIS_PID_FILE")" &> /dev/null; then
#            rm "$REDIS_PID_FILE"
#            echo "Redis stopped."
#        else
#            echo "Failed to stop Redis. Please check the process manually."
#        fi
#    else
#        echo "Redis is not running."
#    fi
#
#    # Stop Celery
#    if [[ -f "$CELERY_PID_FILE" ]]; then
#        if kill "$(cat "$CELERY_PID_FILE")" &> /dev/null; then
#            rm "$CELERY_PID_FILE"
#            echo "Celery stopped."
#        else
#            echo "Failed to stop Celery. Please check the process manually."
#        fi
#    else
#        echo "Celery is not running."
#    fi

#    # Stop Django
#    echo "Checking for Django processes..."
#    DJANGO_PIDS=""
#
#    # Attempt detection with lsof
#    if command -v lsof &> /dev/null; then
#        DJANGO_PIDS=$(lsof -iTCP -sTCP:LISTEN -n | grep manage.py | awk '{print $2}')
#    fi
#
#    # Fallback to ps aux
#    if [[ -z "$DJANGO_PIDS" ]]; then
#        DJANGO_PIDS=$(ps aux | grep "[m]anage.py runserver" | awk '{print $2}')
#    fi
#
#    if [[ -n "$DJANGO_PIDS" ]]; then
#        for PID in $DJANGO_PIDS; do
#            if kill "$PID" &> /dev/null; then
#                echo "Stopped Django process with PID $PID."
#            else
#                echo "Failed to stop Django process with PID $PID."
#            fi
#        done
#    else
#        echo "No Django processes found."
#    fi

    # Stop Nginx
    if pgrep nginx > /dev/null; then
        if sudo nginx -s stop &> /dev/null; then
            echo "Nginx stopped."
        else
            echo "Failed to stop Nginx. Please check the process manually."
        fi
    else
        echo "Nginx is not running."
    fi

    echo "All services have been stopped."
}





function restart() {
    echo "Restarting ClipStream services..."
    stop
    start
}

function help() {
    echo "Usage: $0 {setup|start|stop|restart}"
}

# Main logic
case "$1" in
    setup)
        setup
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    *)
        help
        ;;
esac
