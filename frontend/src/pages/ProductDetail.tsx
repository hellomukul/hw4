import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, formatPrice, imageUrl } from '../api'
import type { Product } from '../types'
import './ProductDetail.css'

export default function ProductDetail() {
  const { productId = '' } = useParams()
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [size, setSize] = useState<string | null>(null)

  useEffect(() => {
    const ac = new AbortController()
    setLoading(true)
    setError(null)
    setSize(null)
    fetchProduct(productId, ac.signal)
      .then(setProduct)
      .catch((err) => {
        if (err instanceof DOMException && err.name === 'AbortError') return
        setError(err instanceof Error ? err.message : String(err))
      })
      .finally(() => setLoading(false))
    return () => ac.abort()
  }, [productId])

  // Loading: a skeleton laid out like the real page, so it doesn't jump.
  if (loading) {
    return (
      <div className="container page">
        <div className="detail" aria-hidden>
          <div className="detail-media skeleton-box" style={{ aspectRatio: '1 / 1' }} />
          <div className="detail-info">
            <div className="skeleton-line short" />
            <div className="skeleton-line wide" style={{ height: '1.8rem' }} />
            <div className="skeleton-line" style={{ height: '1.4rem', width: '30%' }} />
            <div className="skeleton-line" />
            <div className="skeleton-line" />
            <div className="skeleton-line short" />
          </div>
        </div>
      </div>
    )
  }
  if (error || !product) {
    return (
      <div className="container page">
        <div className="state-panel error" role="alert">
          <h2>Product not found</h2>
          <p>{error ?? 'We couldn’t find that product.'}</p>
          <Link to="/products" className="btn primary">
            Back to all products
          </Link>
        </div>
      </div>
    )
  }

  const inventory = product.inventory ?? []
  const selected = inventory.find((s) => s.size === size)

  return (
    <div className="container page">
      <nav className="crumbs" aria-label="Breadcrumb">
        <Link to="/">Home</Link>
        <span aria-hidden>›</span>
        <Link to="/products">Products</Link>
        <span aria-hidden>›</span>
        <span className="current">{product.name}</span>
      </nav>

      <div className="detail">
        <div className="detail-media">
          <img src={imageUrl(product)} alt={product.name} />
        </div>

        <div className="detail-info">
          <p className="eyebrow">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <p className="detail-price">{formatPrice(product.price)}</p>

          <p className="detail-desc">{product.description}</p>

          {product.colors.length > 0 && (
            <div className="detail-block">
              <h2>Colours</h2>
              <ul className="chips">
                {product.colors.map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
            </div>
          )}

          {inventory.length > 0 && (
            <div className="detail-block">
              <h2>Size &amp; availability</h2>
              <div className="sizes">
                {inventory.map((s) => {
                  const out = s.quantity === 0
                  return (
                    <button
                      key={s.size}
                      type="button"
                      className={`size${size === s.size ? ' selected' : ''}${out ? ' out' : ''}`}
                      disabled={out}
                      onClick={() => setSize(s.size)}
                      title={out ? 'Out of stock' : `${s.quantity} in stock`}
                    >
                      {s.size}
                    </button>
                  )
                })}
              </div>

              <p className="stock-line">
                {selected ? (
                  selected.quantity > 5 ? (
                    <span className="ok">{selected.size} — in stock ({selected.quantity})</span>
                  ) : (
                    <span className="low">
                      {selected.size} — only {selected.quantity} left
                    </span>
                  )
                ) : (
                  <span className="muted">
                    Select a size. {product.total_stock} in stock across{' '}
                    {inventory.filter((s) => s.quantity > 0).length} of {inventory.length} sizes.
                  </span>
                )}
              </p>

              <button type="button" className="btn primary wide" disabled={!selected}>
                {selected ? `Add ${selected.size} to bag` : 'Select a size'}
              </button>
            </div>
          )}

          {product.search_tags.length > 0 && (
            <div className="detail-block">
              <h2>Tags</h2>
              <ul className="chips subtle">
                {product.search_tags.map((t) => (
                  <li key={t}>{t}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
