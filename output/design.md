# Campus Customs — Design Notes

A cohesive visual pass to make the site feel like a real Yale campus-merch
storefront. Short version: one navy-and-gold identity applied consistently, a
proper type pairing, and small motion that makes browsing feel alive. Each
change below is there to keep a shopper on the page and moving toward a buy.

## Identity & colour

- **Yale navy with a sparing gold accent.** Navy is the dominant brand colour;
  a warm gold (`--accent`) is used only for emphasis — the top bar, active
  edges, the price, the "all sizes" badge. One restrained accent reads as
  "premium store", not "random colours", and draws the eye to the things that
  sell (price, availability).
- **A slim announcement bar** — "Officially licensed · free pickup at 57
  Broadway" — sets trust and locality the moment the page loads, which is what
  turns a browser into a buyer for licensed goods.

## Typography

- **Fraunces** (a warm, collegiate serif) for headings and prices, **Inter**
  for everything else. The serif gives the Yale/academic feel; the sans keeps
  body text and controls crisp. A clear type pairing creates hierarchy, so the
  eye lands on the product name and price first.

## Visual hierarchy & layout

- **Gradient-topped masthead with a gold underline** and a clear active nav
  state, so navigation always reads as navigation.
- **Hero** with a pill "officially licensed" eyebrow, a large serif headline,
  and a faint diagonal spirit-wear texture — a confident front door rather
  than a plain banner.
- Prices enlarged and set in the display serif; stock badges kept small and
  colour-coded so availability is scannable at a glance.

## Motion (subtle, not noisy)

- Cards **lift and the product image zooms** on hover, with a "View product"
  strip sliding up — a card now clearly invites a click.
- Hero and content **fade up** on load; the announcement dot gently pulses.
- All motion is disabled under `prefers-reduced-motion`, so it never gets in
  the way.

## Product presentation

- Product cards and the product page share the same gradient image frame, serif
  price and refined chips, so a product looks consistent from grid to detail.
- The detail page's size selector and a gradient "Select a size" button make
  the buy action the obvious next step.

## The chat as part of the store

- The assistant now has a **branded header with the CC mark and gold accent**,
  a matching launcher, and the same product-card styling in its replies and in
  the on-page "Shop assistant matches" section — so it feels like the store
  helping you, not a bolted-on bot.

## Why it helps

Consistency builds trust, hierarchy speeds up finding the right product, and
light motion makes browsing feel responsive and alive — together they keep
shoppers exploring instead of bouncing, and push the eye toward the price,
availability, and the buy button.

*(All styling is original — colours, type, the generic "CC" wordmark and the
diagonal texture. No Yale logo or other trademarked artwork is reproduced.)*
