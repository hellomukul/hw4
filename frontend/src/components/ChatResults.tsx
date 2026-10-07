import { useChatResults } from '../chatResults'
import type { ChatProductCard } from '../api'
import type { Product } from '../types'
import { ProductCard } from './ProductCard'
import './ChatResults.css'

/**
 * A chat product card carries everything ProductCard reads; fill the few
 * Product fields ProductCard doesn't use so we can reuse the same tile the
 * Products grid uses, and the cards look identical across the site.
 */
function toProduct(card: ChatProductCard): Product {
  return {
    ...card,
    description: '',
    search_tags: [],
    image_file_path: card.image_url.replace(/^\/media\//, ''),
  }
}

/**
 * The matches the chat assistant last returned, shown as product cards on the
 * page. Appears when the assistant finds products and the shopper can dismiss
 * it. Each card is the same ProductCard used on the Products page, so clicking
 * one opens the single-product detail page.
 */
export function ChatResults() {
  const { results, query, clear } = useChatResults()
  if (results.length === 0) return null

  return (
    <section className="chat-results" aria-label="Shop assistant results">
      <div className="container chat-results-inner">
        <div className="chat-results-head">
          <div>
            <h2>Shop assistant matches</h2>
            <p>
              {results.length} product{results.length === 1 ? '' : 's'}
              {query ? (
                <>
                  {' '}for <em>“{query}”</em>
                </>
              ) : null}{' '}
              — click any card for full details.
            </p>
          </div>
          <button type="button" className="chat-results-clear" onClick={clear}>
            Clear
          </button>
        </div>
        <div className="grid">
          {results.map((card) => (
            <ProductCard key={card.product_id} product={toProduct(card)} />
          ))}
        </div>
      </div>
    </section>
  )
}
