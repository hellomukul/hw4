import { useEffect, useState } from 'react'
import { NavLink, Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import { ChatResults } from './ChatResults'
import { ChatWidget } from './ChatWidget'
import './Layout.css'

const NAV = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Products' },
  { to: '/about', label: 'About Us' },
]

export function Layout() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)
  const location = useLocation()

  // Close the mobile menu whenever the route changes.
  useEffect(() => {
    setMenuOpen(false)
  }, [location.pathname])

  return (
    <div className="site">
      <div className="announce" role="note">
        <span className="announce-dot" aria-hidden />
        Officially licensed Yale apparel · Free in-store pickup at 57 Broadway, New Haven
      </div>
      <header className="masthead">
        <div className="container masthead-inner">
          <Link to="/" className="brand" aria-label="Campus Customs home">
            <span className="brand-mark" aria-hidden>
              CC
            </span>
            <span className="brand-text">
              <strong>Campus Customs</strong>
              <small>Yale apparel &amp; spirit wear</small>
            </span>
          </Link>

          <button
            type="button"
            className="menu-toggle"
            aria-expanded={menuOpen}
            aria-controls="main-menu"
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            onClick={() => setMenuOpen((o) => !o)}
          >
            <span aria-hidden>{menuOpen ? '✕' : '☰'}</span>
          </button>

          <div id="main-menu" className={`menu${menuOpen ? ' open' : ''}`}>
            <nav className="nav" aria-label="Main">
              {NAV.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>

            <div className="account-actions">
              {user ? (
                <>
                  <span className="account-hi" title={user.email}>
                    Hi, {user.first_name || user.name}
                  </span>
                  <button
                    type="button"
                    className="btn ghost"
                    onClick={() => {
                      signOut()
                      navigate('/')
                    }}
                  >
                    Log out
                  </button>
                </>
              ) : (
                <>
                  <NavLink to="/login" className="btn ghost">
                    Log in
                  </NavLink>
                  <NavLink to="/signup" className="btn solid">
                    Create account
                  </NavLink>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="site-main">
        <ChatResults />
        <Outlet />
      </main>

      <footer className="site-footer">
        <div className="container footer-inner">
          <div>
            <strong>Campus Customs</strong>
            <p>57 Broadway, New Haven, CT 06511</p>
            <p className="muted">Officially licensed Yale University merchandise.</p>
          </div>
          <nav aria-label="Footer">
            <Link to="/products">Shop all</Link>
            <Link to="/about">About us</Link>
            <Link to="/login">Log in</Link>
            <Link to="/signup">Create account</Link>
          </nav>
        </div>
        <div className="container footer-legal">
          Student project for MGT 409 — not a real storefront.
        </div>
      </footer>

      <ChatWidget />
    </div>
  )
}
