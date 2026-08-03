# AI Job Finder

An AI-powered job search system that scrapes job postings on a schedule, embeds them into a vector database, and lets users search for relevant jobs conversationally through a **Telegram bot** — with paginated, card-style results (title, company, description, and a Next/Prev flow), plus an optional LLM-powered conversational search path via **MCP + Ollama**.

## How it works

```
Airflow DAGs  →  scrape & ingest job postings  →  Postgres (staging table)
                                                          │
                                              embed job text (embedder)
                                                          │
                                                          ▼
                                              pgvector similarity search
                                                          │
                    ┌─────────────────────────────────────┴─────────────────────────────┐
                    │                                                                     │
         Telegram bot (direct search)                                     Telegram bot (conversational / future)
         search_jobs_db() called directly                                 ask_agent() → Ollama (local LLM)
         → paginated job cards, ◀ Prev / Next ▶                                │
                                                                                ▼
                                                                    MCP server (MCP/server.py)
                                                                    exposes search_jobs_db as
                                                                    an MCP tool over HTTP
                                                                                │
                                                                                ▼
                                                                    Ollama decides when to call
                                                                    the tool, then summarizes
                                                                    results conversationally
```

1. **Airflow** DAGs run on a schedule to scrape job postings from configured sources and load them into a Postgres staging table.
2. Job text is embedded (via the `common/embedder` module) and stored in a vector-enabled Postgres table (pgvector) for similarity search.
3. A user messages the **Telegram bot** with a search query (e.g. `"python dev remote"`).
4. The **FastAPI backend** receives the message via a Telegram webhook, embeds the query, runs a vector similarity search (`embedding <-> query_vector`) against the job table, and fetches the matching job records from the staging table. Results are sent back **one job per message ("card")**, with inline **Prev / Next** buttons to page through results.
5. Separately, an **MCP server** exposes the same job search logic as a tool that a locally running **Ollama** model can call. This powers a conversational search path — the LLM decides when to search and summarizes results in natural language — running entirely on your own infrastructure with no external API keys required.

## Project structure

```
ai_job_finder/
├── Airflow/            # DAGs that scrape/ingest job postings on a schedule
├── MCP/                 # MCP server + client for the LLM-powered conversational search
│   ├── server.py          # Exposes search_jobs_db as an MCP tool (streamable-http transport)
│   └── agent_client.py     # Connects to the MCP server + Ollama; drives the tool-calling loop
├── artifacts/           # Docs and diagrams
├── backend/             # FastAPI app: routes, controllers, Telegram webhook logic
│   ├── routes/             # API route definitions (e.g. /api/jobs, /api/jobs/webhook)
│   └── controller/          # Request handlers — see apis.py below
│       └── apis.py            # search_jobs_db (direct DB search) · get_jobs (REST entry point)
│                                 · ask_agent (LLM/MCP conversational entry point) · Telegram webhook logic
├── common/              # Shared modules used across the backend and MCP server
│   ├── db/                 # DB connectors (vector DB + Postgres staging DB)
│   ├── config/               # Schema/table name settings
│   └── embedder/              # Text embedding logic
├── compose.yaml         # Docker Compose setup: backend, mcp, ollama, postgres, airflow
└── example.env          # Environment variable template
```

### A note on `search_jobs_db` vs `get_jobs` vs `ask_agent`

These three functions look similar but serve different callers — keeping them separate avoids a request loop between the backend and the MCP server:

| Function | What it does | Called by |
|---|---|---|
| `search_jobs_db` | The only function that talks to Postgres/pgvector directly | REST route, Telegram card flow, the MCP tool |
| `get_jobs` | Thin async wrapper around `search_jobs_db` for the REST route | `GET /api/jobs` |
| `ask_agent` | Runs the Ollama + MCP conversational loop | Optional/future chat-style endpoint |

`MCP/server.py`'s tool must call `search_jobs_db`, never `get_jobs` or `ask_agent` — otherwise the agent's tool call re-enters itself and hangs indefinitely.

## Prerequisites

- Docker & Docker Compose
- A Telegram bot token (create one via [@BotFather](https://t.me/BotFather))
- A Postgres database with the [pgvector](https://github.com/pgvector/pgvector) extension enabled
- [Ollama](https://ollama.com) running locally or in its own container, with a tool-calling-capable model pulled (e.g. `qwen3`)
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
   Fill in `.env` with at minimum:
   ```
   TELEGRAM_TOKEN=your-telegram-bot-token
   OLLAMA_MODEL=qwen3
   MCP_SERVER_URL=http://mcp:8000/mcp   # use the Docker service name, not localhost, when containers talk to each other
   ```
   (see `example.env` for the full list — database connection strings, schema/table names, etc.)

3. **Pull the Ollama model** (once, before first run):
   ```bash
   docker exec -it ollama ollama pull qwen3
   ```

4. **Start the stack**
   ```bash
   docker compose up --build
   ```
   This brings up the FastAPI backend, the MCP server, Ollama, and Postgres.

5. **Run the Airflow scraping DAGs** to populate the job database before searching.

6. **Expose your backend publicly and register the Telegram webhook:**
   ```bash
   curl "https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=https://your-public-url.com/api/jobs"
   ```
   Verify it's set correctly:
   ```bash
   curl "https://api.telegram.org/bot<TELEGRAM_TOKEN>/getWebhookInfo"
   ```

7. **Chat with your bot on Telegram** — send a search query like `python developer remote` and it will reply with matching job cards you can page through with ◀ Prev / Next ▶.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/api/healthz` | GET | Health check |
| `/api/jobs` | GET | Search jobs directly via query params (`search`, `page`, `limit`, `distance`) |
| `/api/jobs` | POST | Telegram webhook — receives messages and callback queries from Telegram |


## Roadmap / notes

- `ask_agent` (the Ollama + MCP conversational search) isn't wired to a Telegram-facing route yet — currently callable directly, intended for a future chat-style endpoint alongside the existing card/pagination flow.
- `artifacts/` holds project docs and diagrams.

## Contributing

Issues and pull requests are welcome. If you add a new job source to the Airflow DAGs or extend the search API, please keep the staging schema (`common/config/schema_table_setting`) in sync with the vector table.

## License