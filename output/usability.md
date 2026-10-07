# Campus Customs — Usability Improvements

Four improvements to make the shop easier to use and the assistant more
efficient. For each: what was added and why it helps a shopper or the business.

## 1. Loading, error, and empty states

**What was added**

- **Products page** (`pages/Products.tsx`)
  - *Loading* — a grid of shimmering skeleton cards while products load, so the
    grid area never flashes blank.
  - *Error* — a panel that names the problem and offers a **Try again** button
    (re-runs the fetch), instead of a dead page.
  - *Empty* — a real "No products matched" panel with a **Show all products**
    button, rather than a lonely line of text.
- **Product detail page** (`pages/ProductDetail.tsx`) — a skeleton laid out like
  the real page (image block + text lines) while one product loads, and a
  clear "Product not found" panel with a route back on error.
- **Chat** — the panel already shows typing dots while the agent works and the
  assistant's own "nothing matched" reply when a search finds nothing, so the
  chat has loading and empty states too.

**Why it helps**

A blank page reads as "broken" and sends shoppers away. Skeletons tell them
content is coming, an error with a retry lets them recover without a full
reload, and an empty state with a way out ("show all") keeps them shopping
instead of hitting a wall. For the business that is fewer bounces on a slow
request and fewer dead ends.

## 2. Responsive layout and navigation

**What was added**

- A **mobile menu**: below 820px the nav links and the log in / create account
  (or greeting + log out) collapse behind a hamburger button that opens a tidy
  dropdown; it closes automatically on navigation. On desktop everything stays
  inline as before.
- The **product detail** page stacks its image and info into one column on
  narrow screens (the image stops being sticky), so it reads top-to-bottom.
- The **Products filters** wrap instead of overflowing, and the grid reflows
  from four columns down to one.
- The **login / create-account** card fits small screens, and the first/last
  name fields stack into one column on the narrowest phones.
- The **chat** launcher and panel inset to the screen edges and cap their
  height on small screens, so the panel never runs off-screen.

**Why it helps**

A lot of shoppers browse on a phone. A nav that overflows, a product page that
needs sideways scrolling, or a chat panel wider than the screen all make the
shop feel broken on mobile. Making each view adapt means the same shop works in
a dorm room on a laptop or walking past the store on a phone — which is where a
campus-merch impulse buy actually happens.

## 3. The assistant asks before guessing

**What was added**

- A new section in `backend/prompts/prompt.md`: when a request is too vague or
  broad to search well — "I want something nice", "got any gifts?", "what
  should I buy?", "show me everything" — the assistant asks **one** short
  clarifying question (what kind of item, who it's for, a college/sport/colour)
  instead of guessing or dumping a random handful of products. A small hint is
  enough to proceed, and a specific request is still searched immediately.

**Why it helps**

Guessing wastes the shopper's attention: a random six products that don't match
what they meant is worse than a quick "what kind of thing are you after?". One
good question turns a vague browse into a real recommendation, which is exactly
what a helpful shop associate would do — and it keeps the assistant honest
rather than padding an answer to look useful.

## 4. Leaner, more efficient catalogue search

**What was added** (`backend/tools.py`)

- **A hard result cap** — `MAX_SEARCH_RESULTS = 6`. Search and browse never
  return more than six matches; a shopper who wants the full range is pointed
  at the Products page with its filters.
- **One query instead of N+1** — building the cards used to run a separate
  inventory query per matched product. Now a single grouped query fetches the
  in-stock sizes for all matches at once, so a search is a fixed two queries
  regardless of how many products match.
- **Only the fields a card needs** — search results carry just id, name, type,
  price, image, colours and which sizes are in stock. The heavy fields
  (description, tags, full per-size quantities) are left to the product-detail
  lookup, so a list of hits stays small.

**Why it helps**

A capped, lean result is a faster response and a shorter, more readable chat
answer — the shopper gets a handful of relevant cards, not a wall. Dropping the
per-product queries keeps the backend quick as the catalogue grows, and sending
only the card fields keeps the payload small on a phone connection. For the
business that is a snappier assistant that costs less to run.

---

All four work alongside the existing shop, chat, product search, auth and
customer-memory features — the states and responsive layout wrap the same
pages, and the search and clarification changes are the same tools and prompt
the chat already uses.
