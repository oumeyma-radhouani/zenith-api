# 🧠✧ Zenith OS: API & Database Vault

> 🔗 **Frontend Desktop:** This API powers the interactive retro 3D desktop UI found in the [Zenith OS Frontend](https://github.com/oumeyma-radhouani/zenith-life-manager).

## ( •̀ ω •́ )✧ Project Overview
This is the brain of the Zenith Gamified Life Manager. Built with a modern, decoupled architecture, this API handles all the heavy lifting: database connections, XP calculations, and secure task management.

## (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Key Features
* **Modular Architecture:** Clean separation of routers, schemas, and database logic.
* **Secure Vault:** Uses `.env` shielding to protect Supabase credentials.
* **CORS Bridge:** Explicitly configured to securely communicate with the Next.js frontend.
* **Instant Documentation:** Automatically generates Swagger UI docs via FastAPI.

## (✿◠‿◠) Tech Stack
* **Framework:** FastAPI (Python)
* **Database:** Supabase (PostgreSQL) using the official `supabase-py` client
* **Containerization:** Docker & Docker Compose

## (ง •_•)ง Local Setup
To run this vault locally:
1. Clone the repository.
2. Create a `.env` file in the root directory with your `SUPABASE_URL` and `SUPABASE_KEY`.
3. Run `docker compose up --build` to ignite the engine.
4. The API will be available at `http://localhost:8000`.
