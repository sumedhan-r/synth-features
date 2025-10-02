#!/bin/bash
# Interactive script to run docker-compose with database selection

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root (parent of scripts directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
# Path to docker-compose file
COMPOSE_FILE="$PROJECT_ROOT/docker/docker-compose.yml"

# Change to project root to ensure relative paths work
cd "$PROJECT_ROOT"

echo "========================================="
echo "  Synth Features - Docker Setup"
echo "========================================="
echo ""
echo "Select database provider:"
echo "  1) PostgreSQL"
echo "  2) MySQL"
echo "  3) SQLite (file-based, no separate container)"
echo "  4) No database (backend only)"
echo ""
read -p "Enter choice [1-4]: " choice

# Set default values
PROFILE=""
DATABASE_URL=""

case $choice in
    1)
        echo ""
        echo "=== PostgreSQL Selected ==="
        PROFILE="--profile postgres"

        # Prompt for custom credentials or use defaults
        read -p "Use default credentials? (y/n) [y]: " use_defaults
        use_defaults=${use_defaults:-y}

        if [[ "$use_defaults" == "y" ]]; then
            DATABASE_URL="postgresql://synth_user:synth_password@postgres:5432/synth_db"
            echo "Using default PostgreSQL connection"
        else
            read -p "Database host [postgres]: " db_host
            db_host=${db_host:-postgres}
            read -p "Database port [5432]: " db_port
            db_port=${db_port:-5432}
            read -p "Database name [synth_db]: " db_name
            db_name=${db_name:-synth_db}
            read -p "Database user [synth_user]: " db_user
            db_user=${db_user:-synth_user}
            read -sp "Database password [synth_password]: " db_password
            db_password=${db_password:-synth_password}
            echo ""
            DATABASE_URL="postgresql://${db_user}:${db_password}@${db_host}:${db_port}/${db_name}"
        fi
        ;;
    2)
        echo ""
        echo "=== MySQL Selected ==="
        PROFILE="--profile mysql"

        read -p "Use default credentials? (y/n) [y]: " use_defaults
        use_defaults=${use_defaults:-y}

        if [[ "$use_defaults" == "y" ]]; then
            DATABASE_URL="mysql+pymysql://synth_user:synth_password@mysql:3306/synth_db"
            echo "Using default MySQL connection"
        else
            read -p "Database host [mysql]: " db_host
            db_host=${db_host:-mysql}
            read -p "Database port [3306]: " db_port
            db_port=${db_port:-3306}
            read -p "Database name [synth_db]: " db_name
            db_name=${db_name:-synth_db}
            read -p "Database user [synth_user]: " db_user
            db_user=${db_user:-synth_user}
            read -sp "Database password [synth_password]: " db_password
            db_password=${db_password:-synth_password}
            echo ""
            DATABASE_URL="mysql+pymysql://${db_user}:${db_password}@${db_host}:${db_port}/${db_name}"
        fi
        ;;
    3)
        echo ""
        echo "=== SQLite Selected ==="
        PROFILE="--profile sqlite"
        read -p "SQLite database file path [/app/data/synth.db]: " db_file
        db_file=${db_file:-/app/data/synth.db}
        DATABASE_URL="sqlite:///${db_file}"
        echo "Using SQLite at ${db_file}"
        ;;
    4)
        echo ""
        echo "=== No Database ==="
        echo "WARNING: Backend will fail if it requires a database connection"
        read -p "Continue without database? (y/n) [n]: " confirm
        confirm=${confirm:-n}
        if [[ "$confirm" != "y" ]]; then
            echo "Aborted."
            exit 1
        fi
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "Configuration:"
echo "  Profile: ${PROFILE:-none}"
echo "  Database URL: ${DATABASE_URL:-not set}"
echo "========================================="
echo ""

# Ask for additional environment variables
read -p "Set custom ENV value? (LOCAL/DEV/STAGING/PROD) [LOCAL]: " env_value
env_value=${env_value:-LOCAL}

# Export environment variables
export DATABASE_URL
export ENV="$env_value"

# Ask for docker-compose action
echo ""
read -p "Action: (up/down/restart/logs) [up]: " action
action=${action:-up}

# Build docker-compose base command with explicit file path
BASE_CMD="docker-compose -f $COMPOSE_FILE"
if [[ -n "$PROFILE" ]]; then
    BASE_CMD="$BASE_CMD $PROFILE"
fi

case $action in
    up)
        echo ""
        read -p "Clean stop and remove existing containers? (y/n) [y]: " clean_start
        clean_start=${clean_start:-y}

        read -p "Rebuild images? (y/n) [y]: " rebuild
        rebuild=${rebuild:-y}

        read -p "Run in detached mode? (y/n) [y]: " detached
        detached=${detached:-y}

        # Execute commands in sequence
        if [[ "$clean_start" == "y" ]]; then
            echo ""
            echo "Stopping containers..."
            eval "$BASE_CMD stop" || true
            echo "Removing containers..."
            eval "$BASE_CMD rm -f" || true
        fi

        if [[ "$rebuild" == "y" ]]; then
            echo ""
            echo "Building images..."
            eval "$BASE_CMD build"
        fi

        echo ""
        echo "Starting services..."
        if [[ "$detached" == "y" ]]; then
            eval "$BASE_CMD up -d"
        else
            eval "$BASE_CMD up"
        fi
        ;;
    down)
        COMPOSE_CMD="$BASE_CMD down"
        read -p "Remove volumes? (y/n) [n]: " remove_volumes
        remove_volumes=${remove_volumes:-n}
        if [[ "$remove_volumes" == "y" ]]; then
            COMPOSE_CMD="$COMPOSE_CMD -v"
        fi
        echo ""
        echo "Running: $COMPOSE_CMD"
        echo ""
        eval $COMPOSE_CMD
        ;;
    restart)
        COMPOSE_CMD="$BASE_CMD restart"
        echo ""
        echo "Running: $COMPOSE_CMD"
        echo ""
        eval $COMPOSE_CMD
        ;;
    logs)
        COMPOSE_CMD="$BASE_CMD logs -f"
        echo ""
        echo "Running: $COMPOSE_CMD"
        echo ""
        eval $COMPOSE_CMD
        ;;
    *)
        echo "Invalid action. Exiting."
        exit 1
        ;;
esac
