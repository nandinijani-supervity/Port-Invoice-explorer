# 🚀 Starting the Invoice Command Center

## Prerequisites

1. **PostgreSQL Database** - Make sure PostgreSQL is running
2. **Python 3.11+** - For backend
3. **Node.js 18+** - For frontend
4. **Environment Variables** - Create `.env` file (see `env.example`)

## Step-by-Step Execution

### 1. Set Up Environment

```bash
# Copy example env file
cp env.example .env

# Edit .env and add your credentials:
# - GEMINI_API_KEY (from https://aistudio.google.com/)
# - DATABASE_URL (your PostgreSQL connection string)
# - AUTH_SECRET_KEY
```

### 2. Install Backend Dependencies

```bash
# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r packages/requirements.txt
```

### 3. Set Up Database

```bash
# Make sure PostgreSQL is running and DATABASE_URL is set in .env

# Run database migrations
alembic upgrade head

# Seed initial AP data (PO, SES, Checklist)
python scripts/seed_ap_data.py
```

### 4. Start Backend Server

```bash
# From project root directory
# Option 1: Using uvicorn (development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Option 2: Using gunicorn (production-like)
gunicorn -c gunicorn/dev.py app.main:app
```

Backend will be available at: **http://localhost:8001**
API Docs: **http://localhost:8001/docs**

### 5. Start Frontend Server

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:3000**

## Quick Start (All Commands)

```bash
# Terminal 1: Backend
source venv/bin/activate
alembic upgrade head
python scripts/seed_ap_data.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2: Frontend
cd frontend
npm install  # First time only
npm run dev
```

## Verify Everything Works

1. **Backend Health Check**: http://localhost:8001/api/health
2. **API Documentation**: http://localhost:8001/docs
3. **Frontend**: http://localhost:3000
4. **Test Invoice Upload**: 
   - Go to http://localhost:3000/explorer
   - Upload a PDF invoice
   - Check validation results

## Troubleshooting

### Database Connection Issues
- Check PostgreSQL is running: `pg_isready`
- Verify DATABASE_URL in `.env` is correct
- Check database exists: `psql -l`

### Gemini API Issues
- Verify GEMINI_API_KEY is set in `.env`
- Check API key is valid at https://aistudio.google.com/
- Check logs for API errors

### Migration Issues
- If migration fails, check alembic version: `alembic current`
- To reset: `alembic downgrade base` then `alembic upgrade head`

### Port Already in Use
- Backend: Change port in uvicorn command: `--port 8002`
- Frontend: Change port in package.json or use: `npm run dev -- -p 3001`

## Environment Variables Required

```bash
# Required
GEMINI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Optional
BASE_PATH=
APP_ENV=development
LOG_LEVEL=INFO
AUTH_SECRET_KEY=your_secret_here
```

