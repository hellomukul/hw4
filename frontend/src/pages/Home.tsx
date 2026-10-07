import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchProducts } from '../api'
import { ProductCard } from '../components/ProductCard'
import type { Product } from '../types'
import './Home.css'

const CATEGORIES = [
  { label: 'Hoodies & sweatshirts', query: 'hoodie', blurb: 'Fleece-lined staples for a New Haven winter.' },
  { label: 'Residential colleges', query: 'college', blurb: 'Branford to Trumbull — wear your college.' },
  { label: 'Varsity sports', query: 'sports', blurb: 'Hockey, crew, squash and the rest of the Bulldogs.' },
  { label: 'Family & alumni', query: 'mom', blurb: 'Yale Mom, Dad, Grandma, and the whole family tree.' },
]

export default function Home() {
  const [featured, setFeatured] = useState<Product[]>([])

  useEffect(() => {
    const ac = new AbortController()
    fetchProducts({}, ac.signal)
      .then((r) => setFeatured(r.products.slice(0, 4)))
      .catch(() => {})
    return () => ac.abort()
  }, [])

  return (
    <>
      <section className="hero">
        <div className="container hero-inner">
          <p className="hero-eyebrow">Officially licensed Yale University apparel</p>
          <h1>Wear it like you mean it.</h1>
          <p className="hero-lead">
            Campus Customs has outfitted Yale students, families and alumni from our shop on
            Broadway. Every piece is licensed, built to last past graduation, and printed for the
            people who actually live here.
          </p>
          <div className="hero-actions">
            <Link to="/products" className="btn solid big">
              Shop the collection
            </Link>
            <Link to="/about" className="btn ghost big">
              Our story
            </Link>
          </div>
        </div>
      </section>

      <section className="container section">
        <div className="section-head">
          <h2>Shop by category</h2>
          <Link to="/products">See everything →</Link>
        </div>
        <div className="categories">
          {CATEGORIES.map((c) => (
            <Link key={c.label} to={`/products?q=${encodeURIComponent(c.query)}`} className="category">
              <h3>{c.label}</h3>
              <p>{c.blurb}</p>
              <span className="category-go">Browse →</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="container section">
        <div className="section-head">
          <h2>New in store</h2>
          <Link to="/products">All products →</Link>
        </div>
        <div className="grid">
          {featured.map((p) => (
            <ProductCard key={p.product_id} product={p} />
          ))}
        </div>
      </section>

      <section className="promise">
        <div className="container promise-inner">
          <div>
            <h3>Licensed, not knock-off</h3>
            <p>Every design is approved under Yale&apos;s trademark licensing programme.</p>
          </div>
          <div>
            <h3>Stocked in six sizes</h3>
            <p>XS through XXL on the shelf, with live stock counts on each product page.</p>
          </div>
          <div>
            <h3>Right off Broadway</h3>
            <p>Pick up in store at 57 Broadway, two minutes from Old Campus.</p>
          </div>
        </div>
      </section>
    </>
  )
}
