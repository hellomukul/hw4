import { Link } from 'react-router-dom'
import { formatPrice, imageUrl } from '../api'
import type { Product } from '../types'

/** Grid tile on the Products page: photo, name, type, price, stock hint. */
export function ProductCard({ product }: { product: Product }) {
  const inStock = product.sizes_in_stock ?? []
  // Every product has stock in some size, so the honest signal is which
  // sizes are missing, not whether the item is available at all.
  const soldOutSizes = 6 - inStock.length

  return (
    <Link to={`/products/${product.product_id}`} className="card">
      <div className="card-media">
        <img src={imageUrl(product)} alt={product.name} loading="lazy" />
      </div>
      <div className="card-body">
        <h3>{product.name}</h3>
        <p className="card-type">{product.garment_type}</p>
        <div className="card-foot">
          <span className="price">{formatPrice(product.price)}</span>
          {inStock.length > 0 ? (
            <span className={soldOutSizes > 0 ? 'stock partial' : 'stock ok'}>
              {soldOutSizes > 0 ? `${inStock.length} of 6 sizes` : 'All sizes'}
            </span>
          ) : (
            <span className="stock out">Out of stock</span>
          )}
        </div>
        {product.colors.length > 0 && (
          <p className="card-colors">{product.colors.slice(0, 3).join(' · ')}</p>
        )}
      </div>
    </Link>
  )
}
