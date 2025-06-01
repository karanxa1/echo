#!/bin/bash

echo "🔥 Setting up ECHO - Your Life, Remembered Forever"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version | cut -d' ' -f2)
        print_success "Python $python_version found"
    else
        print_error "Python 3.8+ is required but not found"
        exit 1
    fi
}

# Check if Node.js is installed
check_node() {
    if command -v node &> /dev/null; then
        node_version=$(node --version)
        print_success "Node.js $node_version found"
    else
        print_error "Node.js 16+ is required but not found"
        exit 1
    fi
}

# Check if PostgreSQL is installed
check_postgresql() {
    if command -v psql &> /dev/null; then
        print_success "PostgreSQL found"
    else
        print_warning "PostgreSQL not found. Please install PostgreSQL and create a database named 'echo_db'"
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    cd backend
    
    # Create virtual environment
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate || . venv/Scripts/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Copy environment file
    if [ ! -f .env ]; then
        print_status "Creating environment file..."
        cp env.example .env
        print_warning "Please edit backend/.env with your configuration"
    fi
    
    cd ..
    print_success "Backend setup complete"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Create Next.js environment file
    if [ ! -f .env.local ]; then
        print_status "Creating frontend environment file..."
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
    fi
    
    cd ..
    print_success "Frontend setup complete"
}

# Create database
setup_database() {
    print_status "Setting up database..."
    
    # Check if createdb command exists
    if command -v createdb &> /dev/null; then
        # Try to create database
        createdb echo_db 2>/dev/null && print_success "Database 'echo_db' created" || print_warning "Database 'echo_db' might already exist"
    else
        print_warning "createdb command not found. Please manually create a PostgreSQL database named 'echo_db'"
    fi
}

# Main setup function
main() {
    echo
    print_status "Checking system requirements..."
    
    check_python
    check_node
    check_postgresql
    
    echo
    print_status "Installing dependencies..."
    
    setup_backend
    setup_frontend
    setup_database
    
    echo
    print_success "🎉 ECHO setup complete!"
    echo
    echo "Next steps:"
    echo "1. Edit backend/.env with your OpenAI API key and database credentials"
    echo "2. Start the backend: cd backend && source venv/bin/activate && python app.py"
    echo "3. Start the frontend: cd frontend && npm run dev"
    echo "4. Visit http://localhost:3000"
    echo
    echo "For more information, see README.md"
}

# Run main function
main 