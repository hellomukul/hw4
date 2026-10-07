"""Catalogue tools the chat agent can call.

These are plain functions over data/campus_customs.db — the same database the
website reads — and they return the typed models in models.py, so the agent
gets a stable, validated shape and the harness has a single contract to point
at. They are deliberately self-contained (their own DB helpers, no import
from main) so the import graph stays a simple line: models -> tools -> agent
-> main, with nothing pointing back.

Every value comes from the database. Nothing here invents a price, a size or
a quantity: if a product or size is not found, that is reported as "not found"
or zero stock rather than filled in with a guess.

All of this reflects the Problem 2 database findings: colours and tags are
JSON-decoded, garment types are matched case-insensitively, sizes are ordered
XS -> XXL, and stock is reported per size.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from models import ProductCard, ProductDetail, SizeAvailability, SizeStock

HERE = Path(__file__).resolve().parent
DB_PATH = HERE.parent / "data" / "campus_customs.db"

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]
SIZE_RANK = {s: i for i, s in enumerate(SIZE_ORDER)}


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _json_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except (TypeError, ValueError):
        return []
    return value if isinstance(value, list) else []


def _sizes(conn: sqlite3.Connection, product_id: str) -> list[SizeStock]:
    """Per-size stock for one product, ordered XS -> XXL."""
    rows = conn.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
    ).fetchall()
    sizes = [SizeStock(size=r["size"], quantity=r["quantity"]) for r in rows]
    sizes.sort(key=lambda s: SIZE_RANK.get(s.size, len(SIZE_ORDER)))
    return sizes


# A chat reply shows a handful of cards, not a wall of them. Capping the
# matches keeps the payload small and the answer readable; a shopper who wants
# the whole range is pointed at the Products page, which has filters.
MAX_SEARCH_RESULTS = 6


def _in_stock_sizes(conn: sqlite3.Connection, product_ids: list[str]) -> dict[str, list[str]]:
    """In-stock sizes for several products in ONE query, ordered XS -> XXL.

    Replaces a per-product inventory lookup (an N+1 query) with a single
    grouped read, so searching for products does not hit the database once per
    hit.
    """
    if not product_ids:
        return {}
    placeholders = ",".join("?" for _ in product_ids)
    rows = conn.execute(
        f"SELECT product_id, size FROM inventory "
        f"WHERE product_id IN ({placeholders}) AND quantity > 0",
        product_ids,
    ).fetchall()
    by_product: dict[str, list[str]] = {}
    for r in rows:
        by_product.setdefault(r["product_id"], []).append(r["size"])
    for sizes in by_product.values():
        sizes.sort(key=lambda s: SIZE_RANK.get(s, len(SIZE_ORDER)))
    return by_product


def _cards_for(conn: sqlite3.Connection, rows: list[sqlite3.Row]) -> list[ProductCard]:
    """Build the lean product cards the frontend renders.

    Only the fields a card needs — id, name, type, price, image, colours and
    which sizes are in stock. No description, tags or per-size quantities;
    those belong to the product-detail lookup, not a list of search hits.
    """
    in_stock = _in_stock_sizes(conn, [r["product_id"] for r in rows])
    return [
        ProductCard(
            product_id=r["product_id"],
            name=r["name"],
            garment_type=r["garment_type"],
            price=r["price"],
            image_url=f"/media/{r['image_file_path']}",
            colors=_json_list(r["colors"]),
            sizes_in_stock=in_stock.get(r["product_id"], []),
        )
        for r in rows
    ]


def search_catalogue(keyword: str, limit: int = MAX_SEARCH_RESULTS) -> list[ProductCard]:
    """Find products matching a keyword in name, type, colour, tags or text.

    Returns at most `limit` (capped at MAX_SEARCH_RESULTS) compact cards, so a
    chat reply stays short and the payload small.
    """
    needle = keyword.strip().lower()
    if not needle:
        return []
    cap = max(1, min(limit, MAX_SEARCH_RESULTS))
    with _connect() as conn:
        rows = conn.execute(
            "SELECT product_id, name, garment_type, price, image_file_path, "
            "colors, search_tags, description FROM catalogue ORDER BY name"
        ).fetchall()
        matched: list[sqlite3.Row] = []
        for row in rows:
            haystack = " ".join(
                [
                    row["name"].lower(),
                    row["garment_type"].lower(),
                    (row["description"] or "").lower(),
                    " ".join(_json_list(row["colors"])).lower(),
                    " ".join(_json_list(row["search_tags"])).lower(),
                ]
            )
            if needle in haystack:
                matched.append(row)
            if len(matched) >= cap:
                break
        return _cards_for(conn, matched)


def products_by_type(
    garment_type: str, limit: int = MAX_SEARCH_RESULTS
) -> list[ProductCard]:
    """List products of one garment type, matched case-insensitively."""
    wanted = garment_type.strip().lower()
    cap = max(1, min(limit, MAX_SEARCH_RESULTS))
    with _connect() as conn:
        rows = conn.execute(
            "SELECT product_id, name, garment_type, price, image_file_path, colors "
            "FROM catalogue WHERE lower(garment_type) = ? ORDER BY name LIMIT ?",
            (wanted, cap),
        ).fetchall()
        return _cards_for(conn, rows)


def get_product_details(product_id: str) -> ProductDetail | None:
    """Description, price and full per-size stock for one product.

    Returns None when the product id is not in the catalogue, so the caller
    can say "I couldn't find that" instead of inventing an answer.
    """
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return None
        sizes = _sizes(conn, product_id)
        return ProductDetail(
            product_id=row["product_id"],
            name=row["name"],
            garment_type=row["garment_type"],
            description=row["description"] or "",
            price=row["price"],
            colors=_json_list(row["colors"]),
            image_url=f"/media/{row['image_file_path']}",
            inventory=sizes,
            total_stock=sum(s.quantity for s in sizes),
            sizes_in_stock=[s.size for s in sizes if s.quantity > 0],
        )


def check_size_availability(product_id: str, size: str) -> SizeAvailability:
    """Stock for one product in one size, read straight from inventory.

    No product is wholly out of stock in this catalogue, so availability is
    always a per-size answer. `found` is False when the product id or the size
    is not recognised — the caller should say so, not guess.
    """
    want = size.strip().upper()
    with _connect() as conn:
        row = conn.execute(
            "SELECT c.name, i.size, i.quantity FROM inventory i "
            "JOIN catalogue c ON c.product_id = i.product_id "
            "WHERE i.product_id = ? AND upper(i.size) = ?",
            (product_id, want),
        ).fetchone()
        if row is None:
            return SizeAvailability(product_id=product_id, size=want, found=False)
        return SizeAvailability(
            product_id=product_id,
            size=row["size"],
            found=True,
            name=row["name"],
            quantity=row["quantity"],
            in_stock=row["quantity"] > 0,
        )
