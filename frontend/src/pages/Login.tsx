import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../api'
import { useAuth } from '../auth'
import './Auth.css'

export default function Login() {
  const { signIn } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      const user = await login(email.trim(), password)
      signIn(user)
      navigate('/products')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not log in.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="container page auth-page">
      <div className="auth-card">
        <h1>Log in</h1>
        <p className="auth-sub">Welcome back. Sign in to your Campus Customs account.</p>

        <form onSubmit={onSubmit}>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@yale.edu"
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button type="submit" className="btn primary wide" disabled={busy}>
            {busy ? 'Signing in…' : 'Log in'}
          </button>
        </form>

        {error && <p className="notice error">{error}</p>}

        <p className="auth-alt">
          New here? <Link to="/signup">Create an account</Link>
        </p>
      </div>
    </div>
  )
}
