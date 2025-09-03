<<<<<<< HEAD
# GeoPulse

A geospatial data processing web application with React frontend and FastAPI backend.

## Project Structure

```
GeoPulse/
├── src/
│   ├── API/                 # FastAPI backend
│   │   ├── app/            # Main application code
│   │   ├── database/       # Database setup and migrations
│   │   ├── alembic/        # Database migrations
│   │   ├── tests/          # Unit tests
│   │   ├── main.py         # Application entry point
│   │   └── requirements.txt
│   └── UI/                 # React frontend
│       ├── src/            # React source code
│       ├── public/         # Static assets
│       ├── package.json
│       └── setup.sh
└── requirements/           # Project requirements
```

## Quick Start

### Option 1: Automated Setup (Recommended)

1. Set up the database:
   ```bash
   ./setup_database.sh
   ```

2. Start the application:
   ```bash
   ./start.sh
   ```

This will automatically:
- Start PostgreSQL database
- Run database migrations
- Install all dependencies
- Start both backend and frontend servers

### Option 2: Manual Setup

#### Backend (FastAPI)

1. Navigate to the API directory:
   ```bash
   cd src/API
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   # Start PostgreSQL (using Docker)
   docker-compose -f database/docker-compose.yml up -d
   
   # Run migrations
   alembic upgrade head
   ```

5. Start the API server:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

#### Frontend (React)

1. Navigate to the UI directory:
   ```bash
   cd src/UI
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The UI will be available at `http://localhost:3000`

## Features

- User registration and authentication
- File upload and processing
- Geospatial data analysis
- Dashboard with data visualization
- API usage tracking

## Configuration

- Backend configuration: `src/API/app/config.py`
- Database configuration: `src/API/database/docker-compose.yml`
- Frontend configuration: `src/UI/src/utils/api.js`

## Testing

Run backend tests:
```bash
cd src/API
python -m pytest tests/
```

Run frontend tests:
```bash
cd src/UI
npm test
```
=======
# practising_git
>>>>>>> d9d13dd4c29f98e7a8ea02b6565f7288c2084f16
