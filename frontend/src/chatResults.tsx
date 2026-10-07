import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import type { ChatProductCard } from './api'

/**
 * Shared place for the product matches the chat assistant returns.
 *
 * The chat widget pushes the structured `products` from a reply here, and a
 * results section in the page layout reads them and renders product cards —
 * so a search typed into the chat updates the website itself, not just the
 * little chat panel.
 */

interface ChatResultsState {
  results: ChatProductCard[]
  query: string
  setResults: (products: ChatProductCard[], query: string) => void
  clear: () => void
}

const ChatResultsContext = createContext<ChatResultsState | null>(null)

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [results, setResultsState] = useState<ChatProductCard[]>([])
  const [query, setQuery] = useState('')

  const setResults = useCallback((products: ChatProductCard[], q: string) => {
    setResultsState(products)
    setQuery(q)
  }, [])

  const clear = useCallback(() => {
    setResultsState([])
    setQuery('')
  }, [])

  const value = useMemo(
    () => ({ results, query, setResults, clear }),
    [results, query, setResults, clear],
  )
  return <ChatResultsContext.Provider value={value}>{children}</ChatResultsContext.Provider>
}

export function useChatResults(): ChatResultsState {
  const ctx = useContext(ChatResultsContext)
  if (!ctx) throw new Error('useChatResults must be used within ChatResultsProvider')
  return ctx
}
