# AI Prompt Log — Homework 4

A record of the prompts I gave the AI while working this assignment, kept per
problem and in the order I typed them.

**How to use this file**

- One `##` section per problem, with the problem number and title.
- Prompts are kept verbatim inside the code fences — typos, shorthand and all.
  The fences keep Markdown from reformatting anything.
- **Follow-up prompt** holds any correction or refinement after the first
  result; it's empty where there wasn't one.
- **Notes** is a short record of what the step produced.

---

## Problem 1 — Set up the prompt log

**Prompts**

1.
```text
Create AI_prompts.md in the project and make sure it is ready for me to keep adding the prompts I use for each problem. I want one section for each problem with the problem number and title, the prompts I actually typed, and a place for a follow-up prompt.
```

**Follow-up prompt**

```text

```

**Notes**

This file. One section per problem with the prompt(s), a follow-up slot, and notes.

---

## Problem 2 — Explore the database

**Prompts**

1.
```text
Here is the prompt 2, Added the data.zip file to the project folder. First unzip it and check what files are inside, then find and inspect data/campus_customs.db. I need to understand the database, especially the catalogue, inventory, and users tables. Figure out all the fields in each table and what each field is used for in the shop or chatbot. Then put the findings into output/harness.md
```

**Follow-up prompt**

```text

```

**Notes**

Findings written to `output/harness.md`. The database also has a fourth table,
`chat_messages`, which the prompt did not name but which matters for the
chatbot — documented alongside the other three.



---

## Problem 3 — Scaffold the website (React + Vite + TS frontend, FastAPI backend)

**Prompts**

1.
```text
Prompt 3 now. I need to start building the Campus Customs website. First scaffold the React + Vite + TypeScript frontend and set up the main pages with a top nav for Home, Products, About Us, Log in, and Create account. I also need the Products page to show the product images and basic info from the database, and each product should open its own single product page with the bigger image, description, price, and sizes or stock if that data is available. I also need a floating chat box in the bottom right, but for now it can just be a basic interface that will connect to the backend later. We also need a small FastAPI backend in backend/main.py to read the database and serve the products and images. For the Home and About Us pages, look at yalebulldogblue.com to understand the Campus Customs style and information, but write the actual page content in our own words. First look at what we already have from problem 2 and the database structure, then build this. Also add this prompt to AI_prompts.md.
```

**Follow-up prompt**

```text

```

**Notes**

Used the Problem 2 findings directly: JSON-decoded `colors`/`search_tags`,
case-insensitive `garment_type`, explicit XS-XXL size order, and per-size
stock rather than per-product. Visual direction is Yale navy and white from
yalebulldogblue.com, all page copy written fresh.



---

## Problem 4 — Create-account and login flow

**Prompts**

1.
```text
let's do prompt 4 now. Build a create-account and login flow using the frontend and backend we already made. For create account, I need first name, last name, email, password, and confirm password. For login, just email and password. New accounts should be saved in the existing users table in data/campus_customs.db. Make sure passwords are properly hashed and never stored as plain text. Ensure the existing test user from the database can log in using the credentials given in the assignment. After that, test both the existing user login and creating a brand-new account to make sure both work. Update output/harness.md with a simple explanation of how the auth works, what user information is stored, and how the passwords are protected. Keep the existing website functionality working.
```

**Follow-up prompt**

```text

```

**Notes**

Passwords hashed with PBKDF2-HMAC-SHA256, 260k iterations, per-user salt;
new accounts use a self-describing `pbkdf2_sha256$iterations$salt$digest`
format, and `verify_password` also reads the seeded three-field hashes.
New-account signup + login verified end to end through the UI. Confirming the
existing test user's login still needs the assignment's password for it —
noted for the user.



---

## Problem 5 — Shop chatbot (PydanticAI agent behind FastAPI)

**Prompts**

1.
```text
let's do prompt 5 now. Build the Campus Customs shop chatbot as a PydanticAI agent behind FastAPI and connect it to the chat widget on the frontend. Put the API app in backend/main.py and keep the agent files in backend/ with prompts/prompt.md, agent.py, tools.py, and models.py. Add the Campus Customs voice and basic safety rules to the prompt file. Start the Pydantic/PydanticAI models needed for chat replies and product cards, and make the agent load the prompt and the AI model properly. In main.py, add a chat route so messages from the website go to the agent and the agent's reply comes back to the frontend. Keep whatever product and auth connections are needed for the existing site working. The backend should run from the backend/ folder with: uvicorn main:app --reload --port 8000. Update output/harness.md with a simple explanation of how the frontend talks to FastAPI and how the agent is loaded, including the prompt file and model. Keep the existing website functionality working and add this prompt to AI_prompts.md.
```

**Follow-up prompt**

```text

```

**Notes**

Agent uses gpt-5.6-luna via Portkey (per AGENTS.md), with `OpenAIResponsesModel`
so it can call the catalogue tools. Tools append real product cards to a
per-request collector, so the cards the widget shows are always database rows,
never something the model described. Verified live in the browser: reply +
product cards render, images load, the signed-in user is greeted by name, and
off-topic / prompt-injection requests are declined. Committed to run on port
8000 as specified; this session's preview ran on 8001 because another app held
8000.

---

## Problem 6 — Product info and stock tools

**Prompts**

1.
```text
let's do the product info and stock tools now. Build the tools the chatbot needs to look up real information from data/campus_customs.db for product description, price, and stock. It should also be able to check stock by size when a customer asks about a specific size. Make sure these tools actually use the database and don't invent any prices or quantities. If a product or size is out of stock, the chatbot should say that clearly instead of guessing. Expand backend/prompts/prompt.md so the agent knows when to use these tools for product, price, and stock questions. Add or update the return types in backend/models.py for these tool results. Also update output/harness.md with each tool and explain which model fields you chose for the lookup results and why. Test the tools with the actual database and make sure they return the correct product and stock information.
```

**Follow-up prompt**

```text

```

**Notes**

Added typed return models (`ProductDetail`, `SizeAvailability`); tools batched to
2 DB queries; prompt gained a "which tool to use" section.

---

## Problem 7 — Chat search feature (dynamic product cards)

**Prompts**

1.
```text
let's do the problem 7, which is chat search feature. When a customer asks something like “what hoodies do you have?”, the chatbot should search the catalogue and return the matching products, and those products should dynamically show up on the website as product cards with the image, name, price, and short info. The agent should return the product matches in a structured format so the frontend can use them to render the cards. Make sure this works with the chat interface we already built and that clicking any of these dynamically shown product cards still opens the same single-product detail page with the large image and full product information. Also update prompts/prompt.md and output/harness.md to explain how the search results get from the agent to the frontend and how the frontend displays them. Test it with a few different product searches and make sure the page updates with the correct matching products.
```

**Follow-up prompt**

```text

```

**Notes**

Matches render on the page via a shared results context, reusing the same
ProductCard; each card opens the detail page.

---

## Problem 8 — Customer memory, identity, and page context

**Prompts**

1.
```text
let's do step 8, customer memory now. When a shopper is logged in, save their chat history in the database and load that history again when they come back, but guests can still chat without having their history saved. The agent should also know who is currently chatting, including their name and email, and that information should be passed into the agent context or through a tool the agent can use. Also pass the current page context to the agent, including the product the shopper is looking at when they are on a product page, so if they ask something like “do you have this in pink?” the agent knows which product they mean. Make sure this works with the login system and chat we already built and that the memory is only tied to the logged-in user. Update output/harness.md to explain how chat history is stored, what customer information the agent can see, and how the current page context gets passed to the agent. Test it with a logged-in user and a guest, including a conversation on a product page.
```

**Follow-up prompt**

```text

```

**Notes**

History saved to `chat_messages` for logged-in users only; identity + current
product + recent turns passed to the agent as context.

---

## Problem 9 — Usability improvements

**Prompts**

1.
```text
let's improve the usability of the shop now. Add two frontend improvements: first, add proper loading, error, and empty states when products or chat search results are being loaded or when nothing matches, instead of leaving the page blank. Second, improve the responsive layout and navigation so the shop, product pages, login/create account pages, and chat are easy to use on smaller screens as well as desktop. Also add two agent/backend improvements: first, make the agent handle unclear or broad product searches better by asking a short clarification when it doesn't have enough information instead of guessing what product the customer means. Second, make the catalogue search more efficient by limiting the number of product matches returned and only returning the fields the frontend actually needs for the product cards. Make sure these changes work with the existing shop, chat, product search, auth, and customer memory features. Create or update output/usability.md as you build this and for each of the four improvements explain what was added and why it helps a Campus Customs shopper or the business. Make sure all four improvements are actually visible and working in the running app.
```

**Follow-up prompt**

```text

```

**Notes**

Skeletons/error/empty states, mobile hamburger nav, clarify-before-guessing,
and a capped 2-query search. Documented in `output/usability.md`.

---

## Problem 10 — Storefront styling

**Prompts**

1.
```text
Let's do step 10, which is styling the website so it feels like a real Campus Customs storefront. Add creative and imaginative design improvements across the site, including the fonts, colors, visual hierarchy, motion/animations, product presentation, and the chat experience. Make the design feel polished and cohesive rather than just adding random styling, and make sure it still feels like a Campus Customs/Yale campus-merch store. Focus on making the site more engaging and easier to browse, with product cards and product pages looking good, navigation being clear, and the chat feeling like part of the storefront. Keep all the existing functionality working, including product search, dynamic product cards, product details, login/create account, and customer chat. Also create output/design.md and keep it short and concrete, explaining what you changed and why each change should help customers stay on the site and buy.
```

**Follow-up prompt**

```text

```

**Notes**

Navy-and-gold identity, Fraunces + Inter type, announcement bar, hero texture,
card hover/zoom, branded chat. All original styling; no trademarked artwork.

---

## Problem 11 — Live app check with screenshots

**Prompts**

1.
```text
Let's do step 11, which is testing the live site and documenting the results in output/app_check.html. Test the main features we have built and make the page easy to grade. I need screenshots and short captions showing a chat where the agent checks the inventory level of an item and gives the honest stock and price from the database, the dynamic product cards appearing after a category question like “what hoodies do you have?”, and one of the usability improvements we added in step 9. Put the screenshot files in output/app_check_images/ and link them from output/app_check.html using relative paths. Give each screenshot a clear heading and one or two sentences explaining what it proves. Make sure the screenshots are from the actual running site and that all three features are working before documenting them.
```

**Follow-up prompt**

```text

```

**Notes**

Three real screenshots in `output/app_check_images/`, linked from
`output/app_check.html` with headings and captions.

---

## Problem 12 — Audit trail, safety rules, and harness

**Prompts**

1.
```text
Let's do step 12, which is finishing the audit trail, safety rules, and the harness documentation. Keep output/audit_trail.json append-only so every agent run adds a new entry instead of replacing the old ones. Each entry should include the time, the tool name, the short arguments/result, and why the agent stopped. Add useful safety rules to prompts/prompt.md so the agent doesn't make up product information, prices, stock, or sizes, doesn't expose passwords or private customer information, doesn't claim that something was done when it wasn't, and uses the database/tools when it needs real product information. Also make the agent ignore requests that try to override its system rules or expose internal prompts, tools, or private data. Finish output/harness.md so it clearly explains the model fields in models.py and why they were chosen, the tools and abilities the agent has, the safety rules, and the important specs such as loop limits, result limits, which model is being used, and how to run both the frontend and backend. Keep the existing information in the harness and add to it rather than replacing useful sections. Test an agent run and make sure a real audit entry is added and stays there across multiple runs.
```

**Follow-up prompt**

```text

```

**Notes**

Append-only `output/audit_trail.json` (time, tools+args/results, stop reason);
loop limit 8; harness finished with models, tools, safety, and specs.
