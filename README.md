# Port Invoice Explorer

AI-powered invoice validation system that automates 3-way matching and compliance checking.

## Features

- **AI Invoice Extraction** - Uses Google Gemini AI to extract data from PDF invoices
- **10-Point Validation** - Comprehensive compliance rules including 3-way match, tax calculations, and more
- **Database Integration** - Validates against Purchase Orders (PO) and Service Entry Sheets (SES)
- **Excel Reports** - Auto-generates detailed validation reports
- **Web Interface** - Modern Next.js frontend for invoice exploration

## Tech Stack

- **Backend:** FastAPI (Python 3.11)
- **Frontend:** Next.js 15 + React 19
- **AI:** Google Gemini API
- **Database:** PostgreSQL 15
- **Auth:** NextAuth.js (Demo Mode)

## Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/nandinijani-supervity/Port-Invoice-explorer.git
cd Port-Invoice-explorer
cp .env.example .env
```

### 2. Configure Environment
Edit `.env` and add:
```bash
GEMINI_API_KEY=your_key_here  # Get from https://aistudio.google.com/
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

Generate `NEXTAUTH_SECRET`:
```bash
openssl rand -base64 32
```

### 3. Start Services
```bash
make up
```

### 4. Setup Database
```bash
make migrate-up
docker-compose exec backend python scripts/seed_ap_data.py
```

### 5. Access Application
- **Frontend:** http://localhost:3001/app1/explorer
- **API Docs:** http://localhost:8001/docs

**Note:** Currently running in demo mode - authentication is simplified for development.

## Validation Rules

1. PO/SES existence check
2. Document type validation (Tax Invoice vs Credit Note)
3. Digital signature verification
4. Invoice number format (≤16 digits)
5. Invoice date age (≤90 days)
6. 3-way match (Invoice vs PO vs SES)
7. IRN & QR code presence
8. Tax calculation accuracy
9. Deductions validation
10. Hold status check

## Development

```bash
make up          # Start all services
make down        # Stop all services
make logs-be     # View backend logs
make logs-fe     # View frontend logs
make format      # Format code
make lint        # Lint code
make migrate-up  # Run migrations
```

## API Endpoints

- `POST /api/invoices/validate` - Upload and validate invoice PDF
- `GET /api/invoices/report/{report_id}` - Download Excel report
- `GET /api/health` - Health check

See http://localhost:8001/docs for full API documentation.

## Project Structure

```
app/
├── api/invoices.py          # Invoice validation endpoints
├── services/
│   ├── ai_extraction.py     # Gemini AI integration
│   └── rule_engine.py        # 10 validation rules
├── models/ap_docs.py        # PO, SES, Checklist models
└── utils/report_generator.py # Excel report generation

frontend/src/app/explorer/   # Invoice explorer UI
```

## Troubleshooting

**Database issues:** Check PostgreSQL is running and `DATABASE_URL` is correct  
**Gemini API issues:** Verify `GEMINI_API_KEY` is set and valid

For detailed setup, see [START_APP.md](./START_APP.md)
