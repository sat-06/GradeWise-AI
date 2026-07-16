# GradeWise AI

<div align="center">

![GradeWise AI](https://img.shields.io/badge/GradeWise-AI-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat&logo=next.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5.4-blue?style=flat&logo=typescript)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

**AI-Powered Decision Support System for Predictive Basis Weight Control During Paper Grade Transitions**

</div>

---

## 📋 Overview

GradeWise AI is a production-ready, enterprise-grade AI platform designed for paper manufacturing plants. It functions as an **AI Co-Pilot** that predicts Basis Weight (GSM) deviations before they occur, explains the causes, recommends corrective machine settings, and helps operators make informed decisions during paper grade transitions.

### 🎯 Problem Statement

During paper grade transitions, maintaining the desired Basis Weight (GSM) is difficult due to changes in process variables. These transitions often lead to:

- Basis Weight deviations
- Increased production waste
- Longer stabilization times
- Heavy dependence on experienced operators
- Manual trial-and-error adjustments

### 💡 Solution

GradeWise AI combines **Predictive Analytics**, **Explainable AI**, **Prescriptive Analytics**, and **Digital Twin Simulation** into a single platform that serves as an intelligent co-pilot for operators and engineers.

---

## ✨ Features

### Core AI Capabilities

| Module | Description |
|--------|-------------|
| 🔮 **Predictive AI Engine** | Predicts future Basis Weight, risk levels, and stabilization time using ensemble ML models |
| 🔍 **Explainable AI** | SHAP/LIME-based feature importance, root cause analysis, and human-readable decision explanations |
| 🎯 **Recommendation Engine** | Optimal machine setting recommendations with expected improvement calculations |
| 🏭 **Digital Twin Simulator** | What-If simulation allowing operators to test parameter changes before applying |
| 📚 **AI Knowledge Base** | Organizational knowledge repository with best practices and lessons learned |
| 📊 **Historical Intelligence** | Search and analyze similar historical grade transitions |

### Platform Features

- **Real-Time Machine Monitoring** — Live sensor data visualization with animated gauges
- **Business Intelligence Dashboard** — KPIs: waste reduction, cost savings, efficiency gains
- **Intelligent Alerts** — Priority-based alerts (Green/Yellow/Red) with reasons and recommended actions
- **Operator Feedback System** — Accept/Reject/Modify recommendations with stored feedback
- **Model Monitoring** — Track model accuracy, drift, and retraining status
- **Continuous Learning** — Modular ML pipeline designed for periodic retraining on new data

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Next.js Frontend (Port 3000)            │
│  Dashboard │ Monitoring │ Predictions │ Recommendations   │
│  What-If │ History │ Knowledge │ Analytics │ Alerts       │
├─────────────────────────────────────────────────────────┤
│                  FastAPI Backend (Port 8000)              │
│  REST API │ Auth (JWT) │ ML Pipeline │ Explainability    │
│  Recommendation Engine │ What-If Simulator               │
├─────────────────────────────────────────────────────────┤
│                  PostgreSQL + Redis                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **PostgreSQL 16** (optional — the app can run with mock data for demo)
- **Redis** (optional)

### Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Generate synthetic data
python -m app.ml.data.synthetic_generator

# Train ML models
python -m app.ml.models.train

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at **http://localhost:8000**
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at **http://localhost:3000**

### Environment Configuration

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `NEXT_PUBLIC_API_URL` | Backend API URL (frontend) | `http://localhost:8000/api/v1` |
| `JWT_SECRET_KEY` | JWT signing key | Change in production |

---

## 📁 Project Structure

```
GradeWise-AI/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── api/routes/              # API route handlers
│   │   │   ├── auth.py              # Authentication
│   │   │   ├── monitoring.py        # Live monitoring
│   │   │   ├── predictions.py       # AI predictions
│   │   │   ├── recommendations.py   # Recommendations
│   │   │   ├── whatif.py            # What-if simulator
│   │   │   ├── analytics.py         # Business analytics
│   │   │   ├── knowledge.py         # Knowledge base
│   │   │   └── alerts.py            # Intelligent alerts
│   │   ├── core/                    # Core configuration
│   │   │   ├── config.py            # App settings
│   │   │   ├── security.py          # JWT & auth
│   │   │   └── logging.py           # Structured logging
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   ├── repositories/            # Data access layer
│   │   ├── schemas/                 # Pydantic schemas
│   │   └── ml/                      # ML Pipeline
│   │       ├── data/                # Synthetic data generator
│   │       ├── models/              # Model registry & training
│   │       ├── explainability/      # SHAP/LIME explainers
│   │       └── pipeline/            # Feature engineering
│   ├── alembic/                     # Database migrations
│   └── requirements.txt
├── frontend/                        # Next.js Frontend
│   ├── src/
│   │   ├── app/                    # App router pages (12+ pages)
│   │   ├── components/             # React components
│   │   │   ├── layout/             # App layout & navigation
│   │   │   ├── dashboard/          # Charts & widgets
│   │   │   └── shared/             # Shared components
│   │   ├── lib/                    # Utilities
│   │   └── store/                  # Zustand state
│   ├── package.json
│   └── tailwind.config.ts
├── data/synthetic/                  # Synthetic manufacturing data
├── Makefile
├── pyproject.toml
├── .env.example
├── LICENSE
└── README.md
```

---

## 🛠️ Development

### Available Commands

```bash
make help           # Show all available commands
make dev-backend    # Start backend with hot reload
make dev-frontend   # Start frontend dev server
make install        # Install all dependencies
make seed           # Generate synthetic manufacturing data
make train          # Train ML models
make test           # Run all tests
make lint           # Lint code
make format         # Format code
make migrate        # Run database migrations
```

### Code Quality

```bash
# Format backend
cd backend && black app/ && ruff check --fix app/

# Lint frontend
cd frontend && npm run lint
```

### Database Migrations

```bash
# Create new migration
make migrate-create msg="description"

# Apply migrations
make migrate
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">

**GradeWise AI** — *Intelligence for Industrial Excellence*

</div>
