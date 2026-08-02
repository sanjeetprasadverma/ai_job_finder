# AI Job Finder

An AI-powered job search system that scrapes job postings on a schedule, embeds them into a vector database, and lets users search for relevant jobs conversationally through a **Telegram bot** — with paginated, card-style results (title, company, description, and a Next/Prev flow).

## How it works

```
Airflow DAGs  →  scrape & ingest job postings  →  Postgres (staging table)
                                                          │
                                              embed job text (embedder)
                                                          │
                                                          ▼
                                              pgvector similarity search
                                                          │
                                                          ▼
                            FastAPI backend  ←──  Telegram webhook (user query)
                                    │
                                    ▼
                     Telegram bot replies
```

1. **Airflow** DAGs run on a schedule to scrape job postings from configured sources and load them into a Postgres staging table.
2. Job text is embedded (via the `common/embedder` module) and stored in a vector-enabled Postgres table (pgvector) for similarity search.
3. A user messages the **Telegram bot** with a search query (e.g. `"python dev remote"`).
4. The **FastAPI backend** receives the message via a Telegram webhook, embeds the query, runs a vector similarity search (`embedding <-> query_vector`) against the job table, and fetches the matching job records from the staging table.
5. Results are sent back to the user **one job per message ("card")**, with inline **Prev / Next** buttons to page through results without spamming the chat.

## Project structure

```
ai_job_finder/
├── Airflow/          # DAGs that scrape/ingest job postings on a schedule
├── MCP/               # Placeholder — not in use yet
├── artifacts/         # Docs and diagrams
├── backend/           # FastAPI app: routes, controllers, Telegram webhook logic
│   ├── routes/         # API route definitions (e.g. /api/jobs, /api/jobs/webhook)
│   └── controller/      # Request handlers (get_jobs, telegram_webhook, etc.)
├── common/            # Shared modules used across the backend
│   ├── db/              # DB connectors (vector DB + Postgres staging DB)
│   ├── config/           # Schema/table name settings
│   └── embedder/         # Text embedding logic
├── compose.yaml       # Docker Compose setup for local development
└── example.env        # Environment variable template
```

## Prerequisites

- Docker & Docker Compose
- A Telegram bot token (create one via [@BotFather](https://t.me/BotFather))
- A Postgres database with the [pgvector](https://github.com/pgvector/pgvector) extension enabled for similarity search
- A publicly reachable HTTPS URL for the Telegram webhook (e.g. via [ngrok](https://ngrok.com/) for local dev, or a deployed domain in production)

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/sanjeetprasadverma/ai_job_finder.git
   cd ai_job_finder
   ```

2. **Configure environment variables**
   ```bash
   cp example.env .env
   ```
   Fill in `.env` with your values, including at minimum:
   ```
   TELEGRAM_TOKEN=your-telegram-bot-token
   ```
   (see `example.env` for the full list of required variables — database connection strings, schema/table names, etc.)

3. **Start the stack**
   ```bash
   docker compose up --build
   ```
   This brings up the FastAPI backend (and any other services defined in `compose.yaml`, e.g. Postgres/Airflow if included).

4. **Run the Airflow scraping DAGs** (if not already scheduled) to populate the job database before searching.

5. **Expose your backend publicly and register the Telegram webhook:**
   ```bash
   curl "https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=https://your-public-url.com/api/jobs"
   ```
   Verify it's set correctly:
   ```bash
   curl "https://api.telegram.org/bot<TELEGRAM_TOKEN>/getWebhookInfo"
   ```

6. **Chat with your bot on Telegram** — send a search query like `python developer remote` and it will reply with matching job cards you can page through.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/api/healthz` | GET | Health check |
| `/api/jobs` | GET | Search jobs directly via query params (`search`, `page`, `limit`, `distance`) |
| `/api/jobs` | POST | Telegram webhook endpoint — receives messages and callback queries from Telegram |

## Roadmap / notes

- `MCP/` is reserved for a future Model Context Protocol server to expose job search as a tool for LLM clients — not implemented yet.
- `artifacts/` holds project docs and diagrams.

## Contributing

Issues and pull requests are welcome. If you add a new job source to the Airflow DAGs or extend the search API, please keep the staging schema (`common/config/schema_table_setting`) in sync with the vector table.

## License
