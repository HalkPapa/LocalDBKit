# LocalDBKit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7-47A248.svg)](https://www.mongodb.com/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D.svg)](https://redis.io/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Latest-24386C.svg)](https://qdrant.tech/)

🗄️ Complete local database development kit with Docker Compose

An all-in-one local development database environment featuring PostgreSQL, MongoDB, Redis, Qdrant, plus integrated Ollama LLM and RAG system.

[日本語版README](README.md)

## ⚡ Quick Start

```bash
# 1. Clone repository
git clone https://github.com/HalkPapa/LocalDBKit.git
cd LocalDBKit

# 2. Setup environment variables
cp .env.example .env

# 3. Start all services
make up

# 4. Health check
make health

# 5. Access Open WebUI
open http://localhost:3000
```

## 📋 Key Commands

| Command | Description |
|---------|-------------|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make health` | Run health check |
| `make backup` | Backup databases |
| `make logs` | View logs |
| `make help` | Show all commands |

Run `make help` for complete command list.

## 🎯 Features

### 🗄️ Multiple Databases

- **PostgreSQL 16** with pgvector extension
- **MongoDB 7** with replica set support
- **Redis 7** for caching and KVS
- **Qdrant** vector database for semantic search

### 🤖 Local LLM System

- **Ollama** - Local LLM server (Gemma2:9b, Qwen2.5:7b)
- **Open WebUI** - Beautiful chat interface
- **RAG System** - Retrieval-Augmented Generation
- **Semantic Search** - Natural language document search

### 🛠️ Management Tools

- **Adminer** (port 8080) - PostgreSQL management
- **Mongo Express** (port 8081) - MongoDB management
- **Qdrant Dashboard** (port 6333) - Vector DB dashboard
- **Grafana** (port 3001) - Monitoring dashboard (NEW! v0.2.0)
- **Prometheus** (port 9090) - Metrics collection (NEW! v0.2.0)
- **Learning Dashboard** (port 8502) - Study progress tracking
- **LLM Dashboard** (port 8501) - Model performance comparison

### 📦 DevOps Features

- **Makefile** - 18+ convenient commands
- **GitHub Actions CI/CD** - Automated testing
- **Backup/Restore** - One-command database backup (NEW! v0.2.0)
- **Auto Backup** - Cron-based automated backup (NEW! v0.2.0)
- **Monitoring** - Prometheus + Grafana metrics (NEW! v0.2.0)
- **Health Checks** - Service monitoring
- **Docker Compose** - Complete containerization

## 📁 Project Structure

```
LocalDBKit/
├── 📄 docker-compose.yml       # Docker configuration
├── 📄 Makefile                # Convenient commands
├── 📄 requirements.txt         # Python dependencies
│
├── 🚀 apps/                    # Applications
│   ├── rag/                   # RAG system
│   ├── learning/              # Learning management
│   └── dashboard/             # Dashboards
│
├── 🔧 scripts/                 # Scripts
│   ├── deployment/            # Deployment scripts
│   ├── knowledge/             # Knowledge management
│   └── multi_app/             # Multi-app support
│
├── 💾 data/                    # Data
│   ├── knowledge/             # RAG knowledge base
│   └── init-scripts/          # DB initialization
│
├── 📚 docs/                    # Documentation
│   ├── guides/                # User guides
│   ├── reference/             # Technical references
│   └── diagrams/              # Architecture diagrams
│
└── 📝 examples/                # Sample code
```

## 🚀 Use Cases

### 1. Local Development Environment

Perfect for:
- Full-stack application development
- Microservices testing
- Database migration testing
- Multi-database applications

### 2. AI/ML Projects

Ideal for:
- RAG (Retrieval-Augmented Generation) prototypes
- Vector search experiments
- Local LLM testing
- Knowledge base management

### 3. Learning & Education

Great for:
- Database learning (4 types)
- Docker Compose practice
- LLM experimentation
- Study progress tracking

### 4. Prototyping

Excellent for:
- Quick proof-of-concepts
- Architecture validation
- Performance testing
- Multi-database comparison

## 📖 Documentation

**All documentation is organized in the [docs/](docs/) folder.**

### 🚀 Quick Start
- **[QUICKSTART.md](docs/guides/QUICKSTART.md)** - 5-minute quick start

### 📖 Guides
- **[SETUP_GUIDE.md](docs/guides/SETUP_GUIDE.md)** - Complete setup guide
- **[DOCKER_GUIDE.md](docs/guides/DOCKER_GUIDE.md)** - Docker complete guide
- **[FLOW_GUIDE.md](docs/guides/FLOW_GUIDE.md)** - System usage flow guide
- **[LLM_GUIDE.md](docs/guides/LLM_GUIDE.md)** - Local LLM system guide
- **[MULTI_APP_GUIDE.md](docs/guides/MULTI_APP_GUIDE.md)** - Multi-app management
- **[BACKUP_GUIDE.md](docs/guides/BACKUP_GUIDE.md)** - Backup & restore guide (NEW! v0.2.0)

### 📋 References
- **[ARCHITECTURE.md](docs/reference/ARCHITECTURE.md)** - System architecture
- **[DATABASES.md](docs/reference/DATABASES.md)** - Database comparison guide
- **[APP_DATABASE_MAP.md](docs/reference/APP_DATABASE_MAP.md)** - App-DB mapping

### 🎨 Diagrams
- **[architecture.drawio](docs/diagrams/architecture.drawio)** - Architecture diagram (editable)
- **[flow.drawio](docs/diagrams/flow.drawio)** - Flow diagram (editable)

### 📝 Project Information
- **[PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** - Project summary
- **[WORK_LOG.md](docs/WORK_LOG.md)** - Construction log
- **[ROADMAP.md](ROADMAP.md)** - Development roadmap
- **[SCREENSHOTS.md](docs/SCREENSHOTS.md)** - UI screenshots (NEW! v0.2.0)

## 📊 Monitoring & Management (NEW! v0.2.0)

### Prometheus + Grafana Monitoring System

Real-time database performance monitoring!

#### Grafana Dashboard
- **URL**: http://localhost:3001
- **Login**: admin / admin
- **Features**:
  - PostgreSQL, MongoDB, Redis metrics
  - Real-time performance monitoring
  - Resource usage graphs
  - Query execution time analysis

#### Prometheus Metrics
- **URL**: http://localhost:9090
- **Features**:
  - Metrics collection engine
  - Time-series data storage
  - Query language (PromQL)

See **[SCREENSHOTS.md](docs/SCREENSHOTS.md)** for details

### Automated Backup System

Ensure data safety with automated backup features.

#### Manual Backup
```bash
# Execute backup
make backup

# Restore from backup
make restore BACKUP=./backups/20260315_120000
```

#### Automated Backup (cron setup)
```bash
# Edit crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/LocalDBKit/scripts/deployment/auto-backup.sh
```

**Backup Contents**:
- PostgreSQL full data (SQL)
- MongoDB full data (compressed)
- Redis snapshot
- Qdrant full data

See **[BACKUP_GUIDE.md](docs/guides/BACKUP_GUIDE.md)** for details

## 🛠️ Requirements

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Python** 3.11+ (for applications)
- **Make** (optional, for convenient commands)

## 📊 Service Ports

| Service | Port | URL |
|---------|------|-----|
| PostgreSQL | 5432 | - |
| MongoDB | 27017 | - |
| Redis | 6379 | - |
| Qdrant | 6333 | http://localhost:6333/dashboard |
| Ollama | 11434 | - |
| Open WebUI | 3000 | http://localhost:3000 |
| **Grafana** | **3001** | **http://localhost:3001** (NEW!) |
| Adminer | 8080 | http://localhost:8080 |
| Mongo Express | 8081 | http://localhost:8081 |
| RAG API | 8003 | http://localhost:8003 |
| LLM Dashboard | 8501 | http://localhost:8501 |
| Learning Dashboard | 8502 | http://localhost:8502 |
| **Prometheus** | **9090** | **http://localhost:9090** (NEW!) |

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Ways to Contribute

- **Code**: Feature implementation, bug fixes
- **Documentation**: Translations, tutorials
- **Testing**: Test case additions
- **Design**: UI/UX improvements
- **Feedback**: Feature requests, bug reports

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [PostgreSQL](https://www.postgresql.org/) with [pgvector](https://github.com/pgvector/pgvector)
- [MongoDB](https://www.mongodb.com/)
- [Redis](https://redis.io/)
- [Qdrant](https://qdrant.tech/)
- [Ollama](https://ollama.ai/)
- [Open WebUI](https://github.com/open-webui/open-webui)
- [Docker](https://www.docker.com/)

## 🌟 Star History

If you find this project helpful, please consider giving it a ⭐!

---

**Maintainer**: [@HalkPapa](https://github.com/HalkPapa)
**Created with**: Claude Sonnet 4.5 (Anthropic)
