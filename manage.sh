#!/bin/bash

# manage.sh - Helper script to manage the CstoreStudio environment

# Default configurations
COMPOSE_FILE="docker-compose.yml"
LOCALSTACK_URL="http://localhost:4566"

# Ensure we are in the root directory where the script is located
cd "$(dirname "$0")"

function show_help() {
    echo "Usage: ./manage.sh [command]"
    echo ""
    echo "Commands:"
    echo "  up      : Start the entire environment (Docker containers) and seed the database"
    echo "  down    : Stop the environment and remove volumes (clears database)"
    echo "  seed    : Manually run the seed_db.py script to populate the database"
    echo "  restart : Restart the entire environment"
    echo "  restart-agent : Rebuild and restart only the ai-agent service"
    echo "  restart-ui : Rebuild and restart only the ui-app service"
    echo "  logs    : View logs from all containers"
    echo "  help    : Show this help message"
}

function wait_for_localstack() {
    echo "Waiting for LocalStack to be ready..."
    # Wait until localstack health check returns 200/OK 
    while ! curl -s $LOCALSTACK_URL/_localstack/health | grep -q "\"dynamodb\": \"\(available\|running\)\""; do
        sleep 2
        echo -n "."
    done
    echo -e "\nLocalStack DynamoDB is ready!"
    
    echo "Waiting for DynamoDB tables to be created..."
    REQUIRED_TABLES=("Users" "Tickets" "Vendors" "Bids" "Stores")
    TABLES_CREATED=0
    while [ $TABLES_CREATED -eq 0 ]; do
        CURRENT_TABLES=$(docker compose exec localstack awslocal dynamodb list-tables --region us-east-1 --query 'TableNames' --output text)
        ALL_PRESENT=1
        for TABLE_NAME in "${REQUIRED_TABLES[@]}"; do
            if ! echo "$CURRENT_TABLES" | grep -w "$TABLE_NAME" > /dev/null; then
                ALL_PRESENT=0
                break
            fi
        done
        if [ $ALL_PRESENT -eq 1 ]; then
            TABLES_CREATED=1
        else
            sleep 2
            echo -n "."
        fi
    done
    echo -e "\nAll DynamoDB tables are created!"
}

function wait_for_service() {
    SERVICE_NAME=$1
    echo "Waiting for $SERVICE_NAME service to be ready..."
    # Loop until the service is reported as 'running'
    while ! docker compose ps --filter "name=cstorestudio-${SERVICE_NAME}-1" --filter "status=running" | grep -q "cstorestudio-${SERVICE_NAME}-1"; do
        sleep 2
        echo -n "."
    done
    echo -e "\n$SERVICE_NAME service is ready!"
}

function run_seed() {
    echo "Running database seed script..."
    # No need to build ai-agent here, it's built by env_up --build.
    # We run this inside the ai-agent container so that boto3 is available
    # and it has access to the localstack service via the docker network.
    if docker compose exec ai-agent python seed_db.py; then
        echo "Database seeding successful!"
    else
        echo "Database seeding failed. Note: if ai-agent is crash-looping, you can run locally:"
        echo "  cd services/ai-agent && pip install boto3 && python seed_db.py"
    fi
}

function env_up() {
    echo "Starting environment..."
    docker compose up -d --build # Always rebuild to ensure latest code is used

    if [ $? -eq 0 ]; then
        echo ""
        wait_for_localstack
        wait_for_service ai-agent # Wait for ai-agent to be running before seeding
        run_seed
        echo ""
        echo "Environment is up and running!"
        echo "- UI App: http://localhost:3000"
        echo "- AI Agent API: http://localhost:8000"
        echo "- Prometheus: http://localhost:9090"
        echo "- Grafana: http://localhost:3001"
    else
        echo "Failed to start Docker containers."
    fi
}

function env_down() {
    echo "Stopping environment and removing volumes..."
    docker compose down -v
    echo "Environment fully torn down."
}

case "$1" in
    up)
        env_up
        ;;
    down)
        env_down
        ;;
    seed)
        run_seed
        ;;
    restart)
        env_down
        env_up
        ;;
    restart-agent)
        echo "Rebuilding and restarting ai-agent..."
        docker compose up -d --build ai-agent
        echo "ai-agent restarted."
        ;;
    restart-ui)
        echo "Rebuilding and restarting ui-app..."
        docker compose up -d --build ui-app
        echo "ui-app restarted. Wait a few moments for Next.js to compile on the first request."
        ;;
    logs)
        docker compose logs -f
        ;;
    *)
        show_help
        ;;
esac
