import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { signup } from '../api'
import { useAuth } from '../auth'
import './Auth.css'

export default function SignUp() {
  const { signIn } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirm: '',
  })
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  function set(key: keyof typeof form, value: string) {
    setForm((f) => ({ ...f, [key]: value }))
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    if (form.password !== form.confirm) {
      setError('The two passwords do not match.')
      return
    }
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }

    setBusy(true)
    try {
      const user = await signup({
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        email: form.email.trim(),
        password: form.password,
      })
      signIn(user)
      navigate('/products')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create account.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="container page auth-page">
      <div className="auth-card">
        <h1>Create account</h1>
        <p className="auth-sub">Save your sizes and keep track of what you have ordered.</p>

        <form onSubmit={onSubmit}>
          <div className="row">
            <div>
              <label htmlFor="first">First name</label>
              <input
                id="first"
                required
                value={form.first_name}
                onChange={(e) => set('first_name', e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="last">Last name</label>
              <input
                id="last"
                required
                value={form.last_name}
                onChange={(e) => set('last_name', e.target.value)}
              />
            </div>
          </div>

          <label htmlFor="email2">Email</label>
          <input
            id="email2"
            type="email"
            autoComplete="email"
            required
            value={form.email}
            onChange={(e) => set('email', e.target.value)}
            placeholder="you@yale.edu"
          />

          <label htmlFor="password2">Password</label>
          <input
            id="password2"
            type="password"
            autoComplete="new-password"
            required
            minLength={8}
            value={form.password}
            onChange={(e) => set('password', e.target.value)}
          />

          <label htmlFor="confirm">Confirm password</label>
          <input
            id="confirm"
            type="password"
            autoComplete="new-password"
            required
            value={form.confirm}
            onChange={(e) => set('confirm', e.target.value)}
          />
          <p className="hint">At least 8 characters.</p>

          <button type="submit" className="btn primary wide" disabled={busy}>
            {busy ? 'Creating…' : 'Create account'}
          </button>
        </form>

        {error && <p className="notice error">{error}</p>}

        <p className="auth-alt">
          Already have one? <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  )
}
