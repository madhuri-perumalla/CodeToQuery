# CodeToQuery

> **Code-Aware SQL Execution Analysis Platform**
> Analyze SQL queries directly from application source code, generate PostgreSQL execution plans, detect performance bottlenecks, and provide actionable optimization insights before deployment.


## Overview

Modern applications often contain hundreds of SQL queries spread across repositories, services, ORMs, and raw SQL files. Identifying inefficient queries before deployment is difficult and usually requires manual database analysis.

**CodeToQuery** automates this process by scanning application source code, extracting SQL queries, generating PostgreSQL execution plans, performing rule-based diagnostics, detecting duplicate query patterns, and presenting the results through an interactive dashboard.


## Key Features

* 🔍 Automatic SQL extraction from application source code
* 🗄️ PostgreSQL **EXPLAIN** and **EXPLAIN ANALYZE** integration
* 📊 Interactive dashboard with project metrics
* 📂 Multi-project and codebase management
* ⚙️ Background codebase scanning using Celery
* 📈 Query execution plan visualization
* 🚨 Rule-based SQL performance diagnostics
* 🧩 Query normalization and duplicate detection
* 📑 Query grouping and pattern analysis
* 🔐 JWT-based authentication and authorization


## 🛠️ Supported SQL Sources

CodeToQuery automatically extracts SQL queries from:

* SQLAlchemy
* Django ORM
* Sequelize
* Prisma
* TypeORM
* Raw SQL files


## 🚀 Application Workflow

```text
Create Project
      │
      ▼
Add Codebase
      │
      ▼
Scan Source Code
      │
      ▼
Extract SQL Queries
      │
      ▼
Normalize Queries
      │
      ▼
Generate PostgreSQL Execution Plans
      │
      ▼
Run Diagnostic Rules
      │
      ▼
Pattern Analysis
      │
      ▼
Dashboard & Reports
```

## 💻 Tech Stack

| Category         | Technologies                                                                                       |
| ---------------- | -------------------------------------------------------------------------------------------------- |
| Frontend         | React 18, TypeScript, Material UI, React Router, React Query, Zustand, Axios, Chart.js, React Flow |
| Backend          | FastAPI, Python, SQLAlchemy, Alembic, Pydantic v2                                                  |
| Database         | PostgreSQL                                                                                         |
| SQL Processing   | SQLGlot                                                                                            |
| Background Tasks | Celery, Redis                                                                                      |
| DevOps           | Docker, Docker Compose, Nginx                                                                      |

## 📂 Project Structure

```text
CodeToQuery/
├── backend/
│   ├── app/
│   ├── alembic/
│   └── tests/
├── frontend/
├── docker/
├── docs/
└── scripts/
```


## 🚀 Getting Started

### Clone the Repository

```bash
git clone <repository-url>
cd CodeToQuery
```

### Start with Docker

```bash
cd docker
docker compose up --build
```

### Apply Database Migrations

```bash
docker compose exec backend alembic upgrade head
```
### Access the Application

| Service     | URL                                |
| ----------- | ---------------------------------- |
| Frontend    | http://localhost:3000              |
| Backend API | http://localhost:8000              |
| Swagger UI  | http://localhost:8000/api/v1/docs  |
| ReDoc       | http://localhost:8000/api/v1/redoc |


## 📌 Core Modules

* **Authentication** – Secure JWT authentication and user management
* **Project Management** – Organize multiple projects and codebases
* **Codebase Scanner** – Background scanning and SQL extraction
* **Query Inventory** – Centralized SQL query repository
* **Execution Plan Analysis** – PostgreSQL execution plan generation
* **Diagnostics Engine** – Performance issue detection and recommendations
* **Pattern Analysis** – Query grouping and duplicate detection
* **Dashboard** – Project insights and analytics


