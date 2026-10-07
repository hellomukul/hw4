"""The Campus Customs shop assistant — a PydanticAI agent.

Loads its instructions from prompts/prompt.md and its model from Portkey's
OpenAI-compatible gateway, exposes the catalogue tools in tools.py, and
returns a structured ChatResponse (reply text + product cards + tools used).

The agent never touches the product cards directly: each tool appends the
products it found to a per-request collector, and run_chat hands those back.
That keeps the model's job to writing the reply, and guarantees the cards the
website shows are real rows, not something the model described.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.exceptions import ModelHTTPError, UsageLimitExceeded
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits

import audit
import tools
from models import (
    ChatResponse,
    ChatTurn,
    PageContext,
    ProductCard,
    ProductDetail,
    SizeAvailability,
)

HERE = Path(__file__).resolve().parent
PROMPT_PATH = HERE / "prompts" / "prompt.md"

# The Portkey key lives in the project-root .env, several levels above this
# file. Load the nearest .env walking upward so the key is found wherever the
# server is launched from.
for _candidate in (HERE, *HERE.parents):
    env_file = _candidate / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        break

# Per AGENTS.md: OpenAI model gpt-5.6-luna, reached through Portkey.
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5.6-luna")
PORTKEY_BASE_URL = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1")

# Loop limit: the most model requests one chat turn may make (the initial call
# plus tool-call round-trips). Bounds the agent loop so a single turn can't run
# away; a normal answer needs only a few.
RUN_REQUEST_LIMIT = 8

INSTRUCTIONS = PROMPT_PATH.read_text(encoding="utf-8").strip()


@dataclass
class ChatDeps:
    """Per-request state: who is asking, and what the tools found."""

    first_name: str | None = None
    email: str | None = None
    # Keyed by product_id so the same item shown by two tools appears once.
    collected: dict[str, ProductCard] = field(default_factory=dict)
    tools_used: list[str] = field(default_factory=list)
    # One record per tool call, for the audit trail: name, args, short result.
    tool_log: list[dict] = field(default_factory=list)

    def remember(self, name: str) -> None:
        if name not in self.tools_used:
            self.tools_used.append(name)

    def log_tool(self, tool: str, args: dict, result) -> None:
        """Record a tool call for the audit trail (a short result summary)."""
        if isinstance(result, list):
            summary = f"{len(result)} result(s)"
        elif hasattr(result, "model_dump"):
            summary = result.model_dump()
        else:
            summary = result
        self.tool_log.append({"tool": tool, "args": args, "result": summary})

    def add(self, item: ProductCard | ProductDetail) -> None:
        """Remember a product to show as a card. Accepts a search-result card
        or a full detail result; stores the compact card either way."""
        card = ProductCard(
            product_id=item.product_id,
            name=item.name,
            garment_type=item.garment_type,
            price=item.price,
            image_url=item.image_url,
            colors=item.colors,
            sizes_in_stock=item.sizes_in_stock,
            total_stock=item.total_stock,
        )
        self.collected[card.product_id] = card


def require_api_key() -> str:
    key = os.getenv("PORTKEY_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "PORTKEY_API_KEY is not set. Add it to the project-root .env, then "
            "restart the server."
        )
    return key


def build_model() -> OpenAIResponsesModel:
    """Model on Portkey's gateway. The Responses endpoint is used because the
    agent calls function tools, which Portkey serves there without the
    reasoning-effort restriction of /chat/completions."""
    client = AsyncOpenAI(api_key=require_api_key(), base_url=PORTKEY_BASE_URL)
    return OpenAIResponsesModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))


def build_agent() -> Agent[ChatDeps, str]:
    agent = Agent(
        build_model(),
        deps_type=ChatDeps,
        instructions=INSTRUCTIONS,
        name="campus-customs-assistant",
    )

    @agent.tool
    def search_products(ctx: RunContext[ChatDeps], keyword: str) -> list[dict]:
        """Find products by keyword — a word from the product name, garment
        type, colour, a tag, or the description (e.g. "hoodie", "Saybrook",
        "navy", "hockey"). Use this first when the shopper is looking for
        something but has not named a specific product."""
        ctx.deps.remember("search_products")
        found = tools.search_catalogue(keyword)
        for card in found:
            ctx.deps.add(card)
        ctx.deps.log_tool("search_products", {"keyword": keyword}, found)
        return [_brief(card) for card in found]

    @agent.tool
    def list_by_type(ctx: RunContext[ChatDeps], garment_type: str) -> list[dict]:
        """List products of a given garment type, e.g. "pullover hoodie",
        "crewneck", "quarter-zip pullover", "short-sleeve t-shirt". Use this
        when the shopper asks for a whole category."""
        ctx.deps.remember("list_by_type")
        found = tools.products_by_type(garment_type)
        for card in found:
            ctx.deps.add(card)
        ctx.deps.log_tool("list_by_type", {"garment_type": garment_type}, found)
        return [_brief(card) for card in found]

    @agent.tool
    def product_details(ctx: RunContext[ChatDeps], product_id: str) -> ProductDetail | dict:
        """Look up one product's description, price and full per-size stock by
        its product_id. Use this for any question about what a specific product
        is, what it costs, or whether it is in stock. Returns {"found": false}
        if the id is not in the catalogue — say so, do not guess."""
        ctx.deps.remember("product_details")
        detail = tools.get_product_details(product_id)
        if detail is None:
            not_found = {"found": False, "product_id": product_id}
            ctx.deps.log_tool("product_details", {"product_id": product_id}, not_found)
            return not_found
        ctx.deps.add(detail)
        ctx.deps.log_tool(
            "product_details",
            {"product_id": product_id},
            {"name": detail.name, "price": detail.price, "total_stock": detail.total_stock},
        )
        return detail

    @agent.tool
    def size_availability(
        ctx: RunContext[ChatDeps], product_id: str, size: str
    ) -> SizeAvailability:
        """Check stock for one product in one specific size (XS, S, M, L, XL,
        XXL). Use this when a shopper asks about a particular size. The
        `quantity` and `in_stock` come straight from the database; if `found`
        is false the product id or size was not recognised."""
        ctx.deps.remember("size_availability")
        result = tools.check_size_availability(product_id, size)
        ctx.deps.log_tool(
            "size_availability", {"product_id": product_id, "size": size}, result
        )
        return result

    return agent


def _brief(card: ProductCard) -> dict:
    """The fields the model needs to talk about a search hit — no image path."""
    return {
        "product_id": card.product_id,
        "name": card.name,
        "garment_type": card.garment_type,
        "price": card.price,
        "colors": card.colors,
        "sizes_in_stock": card.sizes_in_stock,
    }


# Built once and reused; building it per request would reopen the model client
# every time.
_agent: Agent[ChatDeps, str] | None = None


def get_agent() -> Agent[ChatDeps, str]:
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


def _context_note(
    first_name: str | None,
    email: str | None,
    page: PageContext | None,
    history: list[ChatTurn] | None,
) -> str:
    """A bracketed note the model reads as background, not as a command.

    Carries who is chatting, what page they're on (so "this"/"it" resolve),
    and the recent conversation so follow-ups have context.
    """
    lines: list[str] = []

    if first_name or email:
        who = first_name or "a signed-in customer"
        tail = f" (email {email})" if email else ""
        lines.append(f"- The customer is signed in as {who}{tail}.")
    else:
        lines.append("- The customer is a guest (not signed in).")

    if page and page.product_id:
        where = page.product_name or page.product_id
        lines.append(
            f"- The customer is currently on the product page for \"{where}\" "
            f"(product id: {page.product_id}). If they say \"this\", \"it\" or "
            f"\"this one\" without naming a product, they mean this one — look "
            f"it up by that id."
        )
    elif page and page.path:
        lines.append(f"- The customer is on the page: {page.path}.")

    if history:
        recent = history[-8:]
        transcript = "\n".join(
            f"    {'Customer' if t.role == 'user' else 'You'}: {t.content}"
            for t in recent
        )
        lines.append("- Recent conversation so far:\n" + transcript)

    body = "\n".join(lines)
    return f"[Context for you, not a message from the customer:\n{body}\n]"


async def run_chat(
    message: str,
    first_name: str | None = None,
    email: str | None = None,
    page: PageContext | None = None,
    history: list[ChatTurn] | None = None,
) -> ChatResponse:
    """Run one chat turn and return the reply plus any product cards.

    Every run appends one entry to output/audit_trail.json: the time, the
    tools called with short args/results, a reply preview, and why it stopped.
    """
    deps = ChatDeps(first_name=first_name, email=email)
    signed_in = bool(email)

    prompt = f"{_context_note(first_name, email, page, history)}\n\n{message}"

    def record(reply: str, stop_reason: str) -> None:
        audit.append_entry(
            audit.build_entry(
                message=message,
                tool_calls=deps.tool_log,
                reply=reply,
                stop_reason=stop_reason,
                products_shown=len(deps.collected),
                signed_in=signed_in,
            )
        )

    try:
        # RUN_REQUEST_LIMIT bounds the model/tool loop so a run can't spin
        # forever; reaching it stops the run rather than looping on.
        result = await get_agent().run(
            prompt, deps=deps, usage_limits=UsageLimits(request_limit=RUN_REQUEST_LIMIT)
        )
    except UsageLimitExceeded:
        reply = (
            "Sorry — that took more steps than I can take in one go. Could you "
            "narrow it down a little?"
        )
        record(reply, "request_limit_reached")
        return ChatResponse(reply=reply, products=[], tools_used=deps.tools_used)
    except ModelHTTPError as exc:
        # The provider's own content filter rejects some messages (e.g. prompt
        # injection or unsafe content) before the model replies. Turn that into
        # a civil decline rather than letting the turn error out.
        if "content_filter" in str(exc) or exc.status_code == 400:
            reply = (
                "I can only help with Campus Customs — our Yale apparel, "
                "sizes, colours and stock. Ask me what we carry and I'll "
                "point you to the right piece."
            )
            record(reply, "content_filtered")
            return ChatResponse(reply=reply, products=[], tools_used=deps.tools_used)
        record("", "model_error")
        raise

    reply = (result.output or "").strip()
    record(reply, "completed")
    return ChatResponse(
        reply=reply,
        products=list(deps.collected.values()),
        tools_used=deps.tools_used,
    )
