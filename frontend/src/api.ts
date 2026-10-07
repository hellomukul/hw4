import type { Filters, Product, ProductList } from './types'

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, '') || ''

async function get<T>(path: string, signal?: AbortSignal): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { signal })
  if (!res.ok) throw new Error(`Server returned ${res.status}`)
  return (await res.json()) as T
}

/** Absolute URL for a product photo served from /media/products. */
export function imageUrl(product: Product): string {
  return `${API_BASE}${product.image_url}`
}

export function fetchProducts(
  params: { q?: string; garment_type?: string; color?: string } = {},
  signal?: AbortSignal,
): Promise<ProductList> {
  const qs = new URLSearchParams()
  if (params.q?.trim()) qs.set('q', params.q.trim())
  if (params.garment_type) qs.set('garment_type', params.garment_type)
  if (params.color) qs.set('color', params.color)
  const query = qs.toString()
  return get<ProductList>(`/api/products${query ? `?${query}` : ''}`, signal)
}

export function fetchProduct(productId: string, signal?: AbortSignal): Promise<Product> {
  return get<Product>(`/api/products/${encodeURIComponent(productId)}`, signal)
}

export function fetchFilters(signal?: AbortSignal): Promise<Filters> {
  return get<Filters>('/api/filters', signal)
}

export function formatPrice(value: number): string {
  return `$${value.toFixed(2).replace(/\.00$/, '')}`
}

// ------------------------------------------------------------------ accounts

export interface AuthUser {
  id: number
  name: string
  email: string
  first_name: string | null
  last_name: string | null
}

interface AuthResponse {
  ok: boolean
  user: AuthUser
}

/** Turn a failed auth response into its server-provided message. */
async function postAuth(path: string, body: unknown): Promise<AuthUser> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = (await res.json().catch(() => ({}))) as Partial<AuthResponse> & { detail?: string }
  if (!res.ok) {
    throw new Error(data.detail || `Request failed (${res.status})`)
  }
  return (data as AuthResponse).user
}

export function signup(input: {
  first_name: string
  last_name: string
  email: string
  password: string
}): Promise<AuthUser> {
  return postAuth('/api/auth/signup', input)
}

export function login(email: string, password: string): Promise<AuthUser> {
  return postAuth('/api/auth/login', { email, password })
}

// --------------------------------------------------------------------- chat

export interface ChatProductCard {
  product_id: string
  name: string
  garment_type: string
  price: number
  image_url: string
  colors: string[]
  sizes_in_stock: string[]
  total_stock: number
}

export interface ChatReply {
  reply: string
  products: ChatProductCard[]
  tools_used: string[]
}

export interface PageContext {
  path?: string
  product_id?: string
  product_name?: string
}

export interface ChatTurn {
  role: 'user' | 'assistant'
  content: string
}

export function sendChat(input: {
  message: string
  first_name?: string | null
  email?: string | null
  page?: PageContext
  history?: ChatTurn[]
}): Promise<ChatReply> {
  return postJson('/api/chat', input)
}

export interface HistoryMessage {
  role: 'user' | 'assistant'
  content: string
  products: ChatProductCard[]
  created_at: string
}

/** A logged-in user's saved conversation. Empty for guests / unknown email. */
export async function fetchHistory(email: string): Promise<HistoryMessage[]> {
  const data = await get<{ messages: HistoryMessage[] }>(
    `/api/chat/history?email=${encodeURIComponent(email)}`,
  )
  return data.messages
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = (await res.json().catch(() => ({}))) as T & { detail?: string }
  if (!res.ok) throw new Error((data as { detail?: string }).detail || `Request failed (${res.status})`)
  return data as T
}

/** Absolute URL for a chat product card image. */
export function cardImage(card: ChatProductCard): string {
  return `${API_BASE}${card.image_url}`
}
