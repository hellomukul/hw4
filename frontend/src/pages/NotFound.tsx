import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="container page">
      <h1>Page not found</h1>
      <p>That page does not exist.</p>
      <Link to="/" className="btn primary">
        Back to home
      </Link>
    </div>
  )
}
