"""Pydantic models shared by the chat agent and the FastAPI chat route.

Kept separate from the catalogue's raw dict shape so the chat layer has a
stable contract: a text reply plus any product cards the agent decided to
show, and the list of tools it used for that turn.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SizeStock(BaseModel):
    size: str
    quantity: int


class ProductCard(BaseModel):
    """A product as the chat widget renders it — enough for a compact card.

    Also the return type of the search/browse tools: it carries just enough
    for the assistant to talk about an item (name, type, price, colours, which
    sizes are in stock) without the full size-by-size breakdown.
    """

    product_id: str
    name: str
    garment_type: str
    price: float
    image_url: str
    colors: list[str] = Field(default_factory=list)
    sizes_in_stock: list[str] = Field(default_factory=list)
    total_stock: int = 0


class ProductDetail(BaseModel):
    """Full lookup result for one product: description, price and stock.

    Returned by the product-details tool. This is the model the assistant
    reads from when a shopper asks what a product is, what it costs, or what
    is in stock — every field here is a real column or a direct roll-up from
    the database, so the assistant never has to guess.
    """

    product_id: str
    name: str
    garment_type: str
    # The catalogue's own description text — the "what is this" answer.
    description: str
    # Real price from the catalogue; never estimated.
    price: float
    colors: list[str] = Field(default_factory=list)
    image_url: str
    # Per-size stock, XS -> XXL, straight from the inventory table.
    inventory: list[SizeStock] = Field(default_factory=list)
    # Roll-ups over `inventory`, so the assistant can answer "is it in stock"
    # and "which sizes" without re-deriving them.
    total_stock: int = 0
    sizes_in_stock: list[str] = Field(default_factory=list)


class SizeAvailability(BaseModel):
    """Stock for one product in one specific size — the by-size check.

    `found` says whether that product + size pairing exists at all; `quantity`
    is the real unit count from inventory; `in_stock` is the plain yes/no the
    assistant should report. When `found` is False the product id or the size
    was not recognised, and the assistant should say so rather than guess.
    """

    product_id: str
    size: str
    found: bool
    name: str | None = None
    quantity: int = 0
    in_stock: bool = False


class PageContext(BaseModel):
    """Where the shopper is on the site right now.

    When they are on a product page, `product_id` is set, so a question like
    "do you have this in pink?" can be tied to the product they're looking at.
    """

    path: str | None = None
    product_id: str | None = None
    product_name: str | None = None


class ChatTurn(BaseModel):
    """One earlier message, sent back so the assistant has conversation
    context for follow-ups like "and in blue?"."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """What the website POSTs to /api/chat."""

    message: str = Field(min_length=1, max_length=2000)
    # Optional signed-in user, so the assistant can greet by name and so the
    # backend can tie saved history to the account. The frontend only sends
    # non-secret profile fields; never a password.
    first_name: str | None = None
    email: str | None = None
    # What the shopper is currently looking at (for "this"/"it" questions).
    page: PageContext | None = None
    # Recent turns from this conversation, for follow-up continuity.
    history: list[ChatTurn] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """What the chat route returns to the website."""

    reply: str
    products: list[ProductCard] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)


class HistoryMessage(BaseModel):
    """One stored turn, as returned to the widget when a user comes back."""

    role: str
    content: str
    products: list[ProductCard] = Field(default_factory=list)
    created_at: str


class ChatHistory(BaseModel):
    """A logged-in user's saved conversation. Empty for guests."""

    messages: list[HistoryMessage] = Field(default_factory=list)
