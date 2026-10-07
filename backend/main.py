"""Campus Customs API — reads data/campus_customs.db and serves it to the shop.

Everything here follows the database findings written up in output/harness.md:

- `colors` and `search_tags` are JSON-encoded strings, so they are decoded
  before they leave this layer; the frontend never sees a stringified array.
- `garment_type` is matched case-insensitively, because the catalogue holds
  both "short-sleeve T-shirt" and "short-sleeve t-shirt".
- Sizes are returned in XS -> XXL order, never alphabetical.
- Stock is per size. No product is wholly out of stock, so availability is
  always reported at the size level.

Run from this folder:
  uvicorn main:app --reload --host 127.0.0.1 --port 8001
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import store
from auth import hash_password, verify_password
from models import (
    ChatHistory,
    ChatRequest,
    ChatResponse,
    HistoryMessage,
    ProductCard,
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
DATA_DIR = PROJECT / "data"
DB_PATH = DATA_DIR / "campus_customs.db"
PRODUCT_IMAGES = DATA_DIR / "products"

# The catalogue stores sizes as plain text, which sorts to L, M, S, XL, XS,
# XXL. This is the order a shopper expects instead.
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]
SIZE_RANK = {s: i for i, s in enumerate(SIZE_ORDER)}

app = FastAPI(title="Campus Customs", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Product photos live beside the database; serve them at the same /media path
# the stored chat snapshots already use.
if PRODUCT_IMAGES.exists():
    app.mount("/media/products", StaticFiles(directory=PRODUCT_IMAGES), name="product-images")


def connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise HTTPException(status_code=500, detail=f"Database not found at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def decode_json_field(raw: str | None) -> list[str]:
    """`colors` and `search_tags` are JSON arrays stored as TEXT."""
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except (TypeError, ValueError):
        return []
    return value if isinstance(value, list) else []


def to_product(row: sqlite3.Row, sizes: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """One catalogue row as the shop wants it.

    Shape matches the product snapshots already stored in chat_messages:
    the catalogue columns, plus a web `image_url` and inventory rolled in.
    """
    product: dict[str, Any] = {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "colors": decode_json_field(row["colors"]),
        "search_tags": decode_json_field(row["search_tags"]),
        "image_file_path": row["image_file_path"],
        "image_url": f"/media/{row['image_file_path']}",
        "price": row["price"],
    }
    if sizes is not None:
        product["inventory"] = sizes
        product["total_stock"] = sum(s["quantity"] for s in sizes)
        product["sizes_in_stock"] = [s["size"] for s in sizes if s["quantity"] > 0]
    return product


def sizes_for(conn: sqlite3.Connection, product_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
    ).fetchall()
    sizes = [{"size": r["size"], "quantity": r["quantity"]} for r in rows]
    sizes.sort(key=lambda s: SIZE_RANK.get(s["size"], len(SIZE_ORDER)))
    return sizes


@app.get("/api/health")
def health() -> dict[str, Any]:
    try:
        with connect() as conn:
            products = conn.execute("SELECT COUNT(*) FROM catalogue").fetchone()[0]
            stock_rows = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
    except HTTPException as exc:
        return {"ok": False, "error": exc.detail}
    return {
        "ok": True,
        "database": DB_PATH.name,
        "products": products,
        "inventory_rows": stock_rows,
        "images": len(list(PRODUCT_IMAGES.glob("*.jpg"))) if PRODUCT_IMAGES.exists() else 0,
    }


@app.get("/api/products")
def list_products(
    q: str | None = None,
    garment_type: str | None = None,
    color: str | None = None,
) -> dict[str, Any]:
    """The Products page. Totals come from one grouped query, not 102 of them."""
    with connect() as conn:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()

        # Roll stock up per product in a single pass.
        totals: dict[str, int] = {}
        in_stock: dict[str, list[str]] = {}
        for r in conn.execute("SELECT product_id, size, quantity FROM inventory"):
            totals[r["product_id"]] = totals.get(r["product_id"], 0) + r["quantity"]
            if r["quantity"] > 0:
                in_stock.setdefault(r["product_id"], []).append(r["size"])

    products = []
    for row in rows:
        item = to_product(row)
        pid = item["product_id"]
        item["total_stock"] = totals.get(pid, 0)
        item["sizes_in_stock"] = sorted(
            in_stock.get(pid, []), key=lambda s: SIZE_RANK.get(s, len(SIZE_ORDER))
        )
        products.append(item)

    # Filtering happens in Python so the JSON columns can be searched properly
    # -- a SQL LIKE on `colors` would also match the brackets and quotes.
    if garment_type:
        wanted = garment_type.strip().lower()
        products = [p for p in products if p["garment_type"].lower() == wanted]

    if color:
        wanted = color.strip().lower()
        products = [p for p in products if any(wanted in c.lower() for c in p["colors"])]

    if q:
        needle = q.strip().lower()
        products = [
            p
            for p in products
            if needle in p["name"].lower()
            or needle in p["description"].lower()
            or needle in p["garment_type"].lower()
            or any(needle in t.lower() for t in p["search_tags"])
            or any(needle in c.lower() for c in p["colors"])
        ]

    return {"count": len(products), "products": products}


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict[str, Any]:
    """One product, with its full size grid for the detail page."""
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"No product '{product_id}'")
        return to_product(row, sizes_for(conn, product_id))


@app.get("/api/filters")
def filters() -> dict[str, Any]:
    """Filter options for the Products page.

    Garment types are de-duplicated case-insensitively, keeping the most
    common spelling as the label.
    """
    with connect() as conn:
        rows = conn.execute("SELECT garment_type, colors, price FROM catalogue").fetchall()

    by_key: dict[str, dict[str, Any]] = {}
    colors: dict[str, int] = {}
    prices: list[float] = []

    for r in rows:
        key = r["garment_type"].lower()
        entry = by_key.setdefault(key, {"labels": {}, "count": 0})
        entry["labels"][r["garment_type"]] = entry["labels"].get(r["garment_type"], 0) + 1
        entry["count"] += 1
        for c in decode_json_field(r["colors"]):
            colors[c.lower()] = colors.get(c.lower(), 0) + 1
        prices.append(r["price"])

    garment_types = [
        {
            "value": key,
            "label": max(entry["labels"].items(), key=lambda kv: kv[1])[0],
            "count": entry["count"],
        }
        for key, entry in sorted(by_key.items())
    ]

    return {
        "garment_types": garment_types,
        "colors": [
            {"value": k, "count": v}
            for k, v in sorted(colors.items(), key=lambda kv: -kv[1])
        ],
        "price": {"min": min(prices), "max": max(prices)},
        "sizes": SIZE_ORDER,
    }


# --------------------------------------------------------------------------
# accounts


class SignupRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=200)


class LoginRequest(BaseModel):
    email: str
    password: str


def public_user(row: sqlite3.Row) -> dict[str, Any]:
    """A user safe to return — everything except the password hash."""
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
    }


@app.post("/api/auth/signup")
def signup(body: SignupRequest) -> dict[str, Any]:
    """Create an account. Stores a salted hash, never the password itself."""
    email = body.email.strip().lower()
    first = body.first_name.strip()
    last = body.last_name.strip()
    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=422, detail="That does not look like an email address.")

    full_name = f"{first} {last}".strip()
    password_hash = hash_password(body.password)

    with connect() as conn:
        exists = conn.execute(
            "SELECT 1 FROM users WHERE lower(email) = ?", (email,)
        ).fetchone()
        if exists:
            raise HTTPException(status_code=409, detail="An account with that email already exists.")
        cur = conn.execute(
            """
            INSERT INTO users (name, email, password_hash, first_name, last_name)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, email, password_hash, first, last),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()

    return {"ok": True, "user": public_user(row)}


@app.post("/api/auth/login")
def login(body: LoginRequest) -> dict[str, Any]:
    """Verify an email + password against the stored hash."""
    email = body.email.strip().lower()
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE lower(email) = ?", (email,)
        ).fetchone()

    # Same response whether the email is unknown or the password is wrong, so
    # the form cannot be used to discover which emails have accounts.
    if row is None or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    return {"ok": True, "user": public_user(row)}


# --------------------------------------------------------------------------
# chat assistant


@app.get("/api/chat/history", response_model=ChatHistory)
def chat_history(email: str | None = None) -> ChatHistory:
    """A logged-in customer's saved conversation, so it reloads when they
    return. Guests (or an unknown email) get an empty list — memory is tied to
    the account found for that email."""
    user = store.get_user_by_email(email)
    if user is None:
        return ChatHistory(messages=[])
    rows = store.load_history(user["id"])
    return ChatHistory(
        messages=[
            HistoryMessage(
                role=r["role"],
                content=r["content"],
                products=[ProductCard(**p) for p in r["products"]],
                created_at=r["created_at"],
            )
            for r in rows
        ]
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    """Send a website message to the Campus Customs agent and return its reply.

    For a signed-in customer (an email that matches a user) the turn is saved
    to `chat_messages` so it comes back next time; guests are not persisted.
    The agent also receives who is chatting and what page/product they are
    looking at, so "do you have this in pink?" resolves to the right item.

    The agent is imported lazily so the rest of the API — products, images,
    auth — still starts and serves even if the AI model or key is missing.
    """
    try:
        from agent import run_chat
    except Exception as exc:  # import-time config error
        raise HTTPException(status_code=503, detail=f"Chat is unavailable: {exc}")

    # Memory only for a real account; a guest resolves to None and is not saved.
    user = store.get_user_by_email(body.email)

    try:
        response = await run_chat(
            body.message,
            first_name=body.first_name,
            email=body.email,
            page=body.page,
            history=body.history,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"The assistant could not reply: {exc}")

    if user is not None:
        store.save_message(user["id"], "user", body.message)
        store.save_message(
            user["id"],
            "assistant",
            response.reply,
            products=[p.model_dump() for p in response.products],
        )

    return response


if __name__ == "__main__":
    import uvicorn

    # The assignment runs this with: uvicorn main:app --reload --port 8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
