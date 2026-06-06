<div align="center">
  <a href="https://github.com/TegroTON/TON-DEX-TegroFinance-Web-Backend">
    <img src="https://tegro.money/assets/tpay/images/logotypes/logo-lebe.png" alt="Tegro DEX Logo" width="120" height="120">
  </a>

  <h2 align="center">Backend for Tegro Finance — Decentralized Exchange (DEX) on TON</h2>

  <p align="center">
    The server-side API, indexer and swap engine that power the <a href="https://tegro.finance">Tegro Finance</a> decentralized exchange on The Open Network (TON).
    <br/><br/>
    <a href="https://tegro.finance">View Live DEX</a>
    ·
    <a href="https://github.com/TegroTON/TON-DEX-TegroFinance-Web-Backend/issues">Report a Bug</a>
    ·
    <a href="https://github.com/TegroTON/TON-DEX-TegroFinance-Web-Backend/issues">Request a Feature</a>
  </p>
</div>

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![TON](https://img.shields.io/badge/Built%20on-TON-0098EA?logo=ton&logoColor=white)
![Stargazers](https://img.shields.io/github/stars/TegroTON/TON-DEX-TegroFinance-Web-Backend?style=social)

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Architecture & Related Repositories](#architecture--related-repositories)
- [Tegro Ecosystem](#tegro-ecosystem)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

This repository contains the **backend services** for [Tegro Finance](https://tegro.finance), an open-source decentralized exchange (DEX / AMM) built on the **TON blockchain**. It exposes the REST API consumed by the [web frontend](https://github.com/TegroTON/TON-DEX-TegroFinance-Web-Frontend), tracks on-chain liquidity pools and swaps, and prepares the transactions users sign to trade and provide liquidity.

## Key Features

- **Swap engine** — quote and build swap transactions for token pairs on TON.
- **Liquidity pools** — track reserves, prices and pool state on-chain.
- **On-chain indexer** — monitors TON for relevant DEX transactions via TON API.
- **REST API** — clean, documented FastAPI endpoints for frontends and integrators.
- **Auth** — JWT-based authentication with secure cookie support.
- **Configurable fees & cashback** — swap fee and cashback parameters are environment-driven.

## Tech Stack

- **Language:** Python 3.10
- **Web framework:** [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn
- **TON integration:** `tonsdk`, `pytonapi`
- **Database:** SQLAlchemy 2 + Alembic migrations (SQLite by default, any SQLAlchemy backend supported)
- **Auth:** PyJWT
- **Dependency management:** Poetry (`pyproject.toml`) / `requirements.txt`

## Project Structure

```
src/
├── api/v1/          # REST API routes (versioned)
├── auth/            # Authentication & JWT
├── database/        # SQLAlchemy models & data-access layer (DAL)
│   ├── models/
│   └── dal/
├── dex/             # DEX logic, pool models, STON.fi-compatible contracts
│   └── models/
├── middlewares/     # FastAPI middlewares
├── task_scheduler/  # Background jobs (indexing, sync)
├── ton/             # TON blockchain client & helpers
└── utils/           # Shared utilities
```

## Getting Started

### Prerequisites
- Python 3.10
- [Poetry](https://python-poetry.org/) (recommended) or `pip`

### Installation

```bash
# Clone the repository
git clone https://github.com/TegroTON/TON-DEX-TegroFinance-Web-Backend.git
cd TON-DEX-TegroFinance-Web-Backend

# Install dependencies (Poetry)
poetry install
# …or with pip
pip install -r requirements.txt

# Configure environment
cp .env.dist .env
# edit .env with your TON API key, contract addresses and secrets

# Run database migrations
alembic upgrade head

# Start the API
uvicorn src.api:app --reload
```

Interactive API docs are available at `http://localhost:8000/docs` (Swagger UI) once the server is running.

## Configuration

All configuration is supplied via environment variables — see [`.env.dist`](.env.dist) for the full template. Key groups:

| Variable group | Purpose |
|---|---|
| `TON_CONSOLE__API_KEY` | TON API access key |
| `TON__*_CONTRACT_ADDRESS` | On-chain contract addresses |
| `STON_FI__*` | STON.fi-compatible router/pool configuration |
| `SWAP__FEE_PERCENT`, `SWAP__*_CASHBACK_PERCENT` | Swap fee & cashback parameters |
| `DATABASE__*` | Database connection settings |
| `SECRET`, `ALGORITHM`, `JWT__*` | Auth & JWT settings |
| `SERVER__DOMAIN`, `SERVER__CORS_ALLOW_ORIGINS` | HTTP server & CORS |

> 🔐 Never commit a real `.env`. Keep API keys and secrets out of version control.

## Architecture & Related Repositories

Tegro Finance is built as a set of cooperating open-source services on TON:

| Layer | Repository | Stack |
|---|---|---|
| Web app (full) | [TON-DEX-TegroFinance-Web-Frontend](https://github.com/TegroTON/TON-DEX-TegroFinance-Web-Frontend) | TypeScript · React |
| Web app (lite, TON/TOR) | [TON-DEX-TegroFinance-Web-Frontend-Lite](https://github.com/TegroTON/TON-DEX-TegroFinance-Web-Frontend-Lite) | TypeScript · React |
| **Backend / indexer** | **TON-DEX-TegroFinance-Web-Backend** *(this repo)* | Python · FastAPI |
| Public DEX API | [API-DEX-TON-Blockchain](https://github.com/TegroTON/API-DEX-TON-Blockchain) | Kotlin |

## Tegro Ecosystem

- 🔁 **DEX** — https://tegro.finance
- 💳 **Payments (Tegro Money)** — https://tegro.money
- 👛 **Wallet** — https://t.me/TegroMoneyBot
- 💬 **Community** — https://t.me/TegroMoney
- 🏠 **All open-source repos** — https://github.com/TegroTON

## Contributing

Contributions are welcome! Please open an [issue](https://github.com/TegroTON/TON-DEX-TegroFinance-Web-Backend/issues) to discuss substantial changes, and submit focused pull requests:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push and open a pull request

## License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
