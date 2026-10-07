import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { fetchFilters, fetchProducts } from '../api'
import { ProductCard } from '../components/ProductCard'
import type { Filters, Product } from '../types'
import './Products.css'

export default function Products() {
  const [params, setParams] = useSearchParams()
  const [products, setProducts] = useState<Product[]>([])
  const [filters, setFilters] = useState<Filters | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  // Bumped by the Retry button to re-run the fetch after a failure.
  const [reloadKey, setReloadKey] = useState(0)

  const q = params.get('q') ?? ''
  const garmentType = params.get('garment_type') ?? ''
  const color = params.get('color') ?? ''
  const [search, setSearch] = useState(q)

  useEffect(() => {
    const ac = new AbortController()
    fetchFilters(ac.signal).then(setFilters).catch(() => {})
    return () => ac.abort()
  }, [])

  useEffect(() => {
    const ac = new AbortController()
    setLoading(true)
    setError(null)
    fetchProducts({ q, garment_type: garmentType, color }, ac.signal)
      .then((r) => setProducts(r.products))
      .catch((err) => {
        if (err instanceof DOMException && err.name === 'AbortError') return
        setError(err instanceof Error ? err.message : String(err))
      })
      .finally(() => setLoading(false))
    return () => ac.abort()
  }, [q, garmentType, color, reloadKey])

  function update(key: string, value: string) {
    const next = new URLSearchParams(params)
    if (value) next.set(key, value)
    else next.delete(key)
    setParams(next, { replace: true })
  }

  const activeCount = useMemo(
    () => [q, garmentType, color].filter(Boolean).length,
    [q, garmentType, color],
  )

  return (
    <div className="container page">
      <header className="page-head">
        <h1>Shop all products</h1>
        <p className="lead">
          Yale apparel for students, families, alumni and fans — residential colleges,
          varsity teams, graduate schools and everything in between.
        </p>
      </header>

      <form
        className="filters"
        onSubmit={(e) => {
          e.preventDefault()
          update('q', search)
        }}
      >
        <div className="filter-field grow">
          <label htmlFor="search">Search</label>
          <input
            id="search"
            type="search"
            value={search}
            placeholder="hoodie, Saybrook, navy, hockey…"
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="filter-field">
          <label htmlFor="type">Garment type</label>
          <select
            id="type"
            value={garmentType}
            onChange={(e) => update('garment_type', e.target.value)}
          >
            <option value="">All types</option>
            {filters?.garment_types.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label} ({t.count})
              </option>
            ))}
          </select>
        </div>

        <div className="filter-field">
          <label htmlFor="color">Colour</label>
          <select id="color" value={color} onChange={(e) => update('color', e.target.value)}>
            <option value="">Any colour</option>
            {filters?.colors.slice(0, 20).map((c) => (
              <option key={c.value} value={c.value}>
                {c.value} ({c.count})
              </option>
            ))}
          </select>
        </div>

        <button type="submit" className="btn primary">
          Search
        </button>
        {activeCount > 0 && (
          <button
            type="button"
            className="btn ghost dark"
            onClick={() => {
              setSearch('')
              setParams({}, { replace: true })
            }}
          >
            Clear
          </button>
        )}
      </form>

      <p className="result-count" aria-live="polite">
        {loading
          ? 'Searching the catalogue…'
          : error
            ? 'Could not load products'
            : `${products.length} product${products.length === 1 ? '' : 's'}`}
      </p>

      {/* Loading: skeleton tiles, so the grid area never flashes blank. */}
      {loading && (
        <div className="grid" aria-hidden>
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="card card-skeleton">
              <div className="card-media skeleton-box" />
              <div className="card-body">
                <div className="skeleton-line wide" />
                <div className="skeleton-line" />
                <div className="skeleton-line short" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Error: say what happened and offer a retry, rather than a blank page. */}
      {!loading && error && (
        <div className="state-panel error" role="alert">
          <h2>We couldn’t load the products</h2>
          <p>{error}</p>
          <button type="button" className="btn primary" onClick={() => setReloadKey((k) => k + 1)}>
            Try again
          </button>
        </div>
      )}

      {/* Empty: a real empty state with a way out. */}
      {!loading && !error && products.length === 0 && (
        <div className="state-panel">
          <h2>No products matched</h2>
          <p>
            Nothing in the catalogue matches
            {q || garmentType || color ? ' those filters' : ' your search'}. Try a broader
            term or clear the filters.
          </p>
          <button
            type="button"
            className="btn primary"
            onClick={() => {
              setSearch('')
              setParams({}, { replace: true })
            }}
          >
            Show all products
          </button>
        </div>
      )}

      {!loading && !error && products.length > 0 && (
        <div className="grid">
          {products.map((p) => (
            <ProductCard key={p.product_id} product={p} />
          ))}
        </div>
      )}
    </div>
  )
}
