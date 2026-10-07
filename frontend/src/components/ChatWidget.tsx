import { useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { cardImage, fetchHistory, sendChat } from '../api'
import type { ChatProductCard, ChatTurn, PageContext } from '../api'
import { useAuth } from '../auth'
import { useChatResults } from '../chatResults'
import './ChatWidget.css'

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  products?: ChatProductCard[]
}

const GREETING: Message = {
  id: 0,
  role: 'assistant',
  content:
    "Hi! I'm the Campus Customs shop assistant. Ask me about sizes, colours, or what Yale gear we carry.",
}

/** The current page, including the product being viewed on a product page. */
function pageContextFrom(pathname: string): PageContext {
  const match = /^\/products\/(.+)$/.exec(pathname)
  return match ? { path: pathname, product_id: match[1] } : { path: pathname }
}

/** Floating shop assistant, bottom right. Talks to POST /api/chat. */
export function ChatWidget() {
  const { user } = useAuth()
  const { setResults } = useChatResults()
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const [draft, setDraft] = useState('')
  const [messages, setMessages] = useState<Message[]>([GREETING])
  const [pending, setPending] = useState(false)
  const bodyRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (open) inputRef.current?.focus()
  }, [open])

  useEffect(() => {
    bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, pending])

  // Load saved history for a logged-in customer; reset to a fresh greeting for
  // a guest or on logout. Memory only exists for a real account.
  useEffect(() => {
    let cancelled = false
    if (!user?.email) {
      setMessages([GREETING])
      return
    }
    fetchHistory(user.email)
      .then((history) => {
        if (cancelled) return
        if (history.length === 0) {
          setMessages([GREETING])
          return
        }
        setMessages([
          GREETING,
          ...history.map((m, i) => ({
            id: i + 1,
            role: m.role,
            content: m.content,
            products: m.products,
          })),
        ])
      })
      .catch(() => {
        if (!cancelled) setMessages([GREETING])
      })
    return () => {
      cancelled = true
    }
  }, [user?.email])

  async function sendMessage(text: string) {
    const trimmed = text.trim()
    if (!trimmed || pending) return

    // Recent turns (excluding the opening greeting) for follow-up context.
    const history: ChatTurn[] = messages
      .filter((m) => m.id !== 0)
      .slice(-8)
      .map((m) => ({ role: m.role, content: m.content }))

    setMessages((prev) => [...prev, { id: Date.now(), role: 'user', content: trimmed }])
    setDraft('')
    setPending(true)

    try {
      const res = await sendChat({
        message: trimmed,
        first_name: user?.first_name ?? null,
        email: user?.email ?? null,
        page: pageContextFrom(location.pathname),
        history,
      })
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: 'assistant', content: res.reply, products: res.products },
      ])
      // Surface the matches on the page itself, not just inside the panel.
      if (res.products.length > 0) {
        setResults(res.products, trimmed)
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content:
            err instanceof Error
              ? `Sorry — ${err.message}`
              : 'Sorry, something went wrong. Please try again.',
        },
      ])
    } finally {
      setPending(false)
    }
  }

  return (
    <>
      <button
        type="button"
        className={`chat-launcher${open ? ' hidden' : ''}`}
        onClick={() => setOpen(true)}
        aria-label="Open shop assistant"
      >
        <span className="chat-launcher-mark" aria-hidden>
          CC
        </span>
        <span>Ask us</span>
      </button>

      <section className={`chat-panel${open ? ' open' : ''}`} aria-label="Shop assistant">
        <header className="chat-head">
          <span className="chat-head-mark" aria-hidden>
            CC
          </span>
          <div className="chat-head-text">
            <strong>Campus Customs assistant</strong>
            <span className="chat-sub">Sizes, colours &amp; availability</span>
          </div>
          <button
            type="button"
            className="chat-close"
            onClick={() => setOpen(false)}
            aria-label="Close chat"
          >
            ✕
          </button>
        </header>

        <div className="chat-body" ref={bodyRef}>
          {messages.map((m) => (
            <div key={m.id} className={`chat-turn ${m.role}`}>
              <div className={`bubble ${m.role}`}>{m.content}</div>
              {m.products && m.products.length > 0 && (
                <div className="chat-cards">
                  {m.products.map((p) => (
                    <Link
                      key={p.product_id}
                      to={`/products/${p.product_id}`}
                      className="chat-card"
                      onClick={() => setOpen(false)}
                    >
                      <img src={cardImage(p)} alt={p.name} loading="lazy" />
                      <div className="chat-card-info">
                        <span className="chat-card-name">{p.name}</span>
                        <span className="chat-card-type">{p.garment_type}</span>
                        <span className="chat-card-price">${p.price.toFixed(2).replace(/\.00$/, '')}</span>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          ))}
          {pending && (
            <div className="bubble assistant typing" aria-live="polite">
              <span />
              <span />
              <span />
            </div>
          )}
        </div>

        <form
          className="chat-form"
          onSubmit={(e) => {
            e.preventDefault()
            void sendMessage(draft)
          }}
        >
          <textarea
            ref={inputRef}
            rows={1}
            value={draft}
            placeholder="Do you have this in navy?"
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                void sendMessage(draft)
              }
            }}
          />
          <button type="submit" className="btn primary" disabled={!draft.trim() || pending}>
            Send
          </button>
        </form>
      </section>
    </>
  )
}
