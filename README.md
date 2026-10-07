# Campus Customs — Homework 4

A small Yale campus-merch storefront: a React + Vite + TypeScript frontend, a
FastAPI backend, and a PydanticAI shop-assistant chatbot that answers from a
SQLite product catalogue. Shoppers can browse and search products, open a
product page, create an account and log in, and chat with an assistant that
looks up real descriptions, prices and per-size stock — and shows matching
products as cards on the page.

## Repository layout

```
hw4/
├── AI_prompts.md          # every prompt used to build this homework
├── requirements.txt       # Python backend dependencies
├── .env.example           # copy to .env and add your key
├── README.md
├── frontend/              # Vite React TypeScript app
├── backend/
│   ├── main.py            # FastAPI app (products, auth, chat, images)
│   ├── agent.py           # PydanticAI shop assistant
│   ├── models.py          # Pydantic models
│   ├── tools.py           # catalogue/stock tools
│   ├── auth.py            # password hashing
│   ├── store.py           # chat-history persistence
│   ├── audit.py           # append-only audit trail
│   └── prompts/
│       └── prompt.md      # the assistant's system prompt
└── output/                # harness, design, usability, app check, audit trail
```

## 1. Add the local data pack

The product database and images are **not** stored in git. Place the data pack
so the final layout is:

```
data/
├── campus_customs.db      # SQLite catalogue, inventory, users, chat_messages
└── products/              # one .jpg per product, referenced by the catalogue
```

Unzip the provided `data.zip` into the project root (it already contains a
`data/` folder), or create `data/` and drop the files in. The backend expects
`data/campus_customs.db` and `data/products/` relative to the project root.

## 2. Configure your key

```bash
cp .env.example .env
# then edit .env and set PORTKEY_API_KEY to your own key
```

The backend reads the nearest `.env` (this folder or a parent). `MODEL_NAME`
defaults to `gpt-5.6-luna` via the Portkey gateway.

## 3. Run the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt    # or: pip install -r ../requirements.txt
uvicorn main:app --reload --port 8000
```

This one process serves the catalogue, product images, the account endpoints
and the chat assistant. Check it with <http://127.0.0.1:8000/api/health>.

## 4. Run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite serves the site on <http://localhost:5174> and proxies `/api` and
`/media` to the backend on port 8000, so the browser talks to one origin. To
point at a different backend, set `VITE_API_BASE`.

## Test account

The seeded database includes a test user:

- **Email:** `test@campuscustoms.yale.edu`
- **Password:** `password`

New accounts you create are stored (with salted password hashes) in the same
`users` table.

## Documentation

See `output/` for the build notes: `harness.md` (database, models, tools,
safety rules, specs), `usability.md`, `design.md`, `app_check.html` (a
screenshot walkthrough of the live app), and `audit_trail.json` (an
append-only log of agent runs).
