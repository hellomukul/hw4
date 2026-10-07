import { Link } from 'react-router-dom'
import './About.css'

export default function About() {
  return (
    <div className="container page prose">
      <header className="page-head">
        <h1>About Campus Customs</h1>
        <p className="lead">
          We make the sweatshirt someone still wears to the Harvard game twenty years after
          they graduate.
        </p>
      </header>

      <section>
        <h2>Who we are</h2>
        <p>
          Campus Customs is a New Haven apparel shop specialising in officially licensed Yale
          University merchandise. We sit at 57 Broadway, in the middle of the shopping block
          that most undergraduates walk through several times a week, and we have built the
          business around the people who pass the window: students kitting themselves out in
          their first week, parents buying something on move-in day, alumni back for a reunion,
          and fans heading to the Bowl.
        </p>
      </section>

      <section>
        <h2>What we sell</h2>
        <p>
          Our range is apparel first — hoodies, crewnecks, quarter-zips, fleece jackets and
          t-shirts — in weights that make sense for a New Haven winter and a September tailgate
          alike. Beyond the plain Yale wordmark, the catalogue is organised around the things
          people here actually identify with:
        </p>
        <ul>
          <li>
            <strong>Residential colleges</strong> — Benjamin Franklin through Trumbull, so you
            can wear the one you were sorted into.
          </li>
          <li>
            <strong>Varsity sport</strong> — from football and hockey to squash, fencing,
            sailing and diving.
          </li>
          <li>
            <strong>Graduate and professional schools</strong> — Management, Law, Medicine,
            Nursing, Architecture, Art, Music, Divinity, Engineering, Public Health and the
            Forest School.
          </li>
          <li>
            <strong>Family</strong> — Yale Mom, Dad, Grandma, Grandpa, Aunt, Uncle, Brother and
            Cousin, because everyone wants one.
          </li>
        </ul>
      </section>

      <section>
        <h2>Licensing</h2>
        <p>
          Everything we print carries official Yale University licensing. That matters more
          than it sounds: licensed goods are made to approved standards, the marks are
          reproduced correctly, and a share of every sale goes back to the University rather
          than to whoever is selling shirts out of a van on game day.
        </p>
      </section>

      <section>
        <h2>Sizes and stock</h2>
        <p>
          We carry XS to XXL across the range. Stock moves quickly in the popular middle sizes,
          so each product page shows what is actually on the shelf per size rather than a vague
          in-stock badge — if the medium is gone, we would rather tell you before you get to
          the counter.
        </p>
      </section>

      <section>
        <h2>Visit us</h2>
        <p>
          57 Broadway, New Haven, CT 06511. Order online for pickup, or come in and try things
          on — we would rather you got the fit right.
        </p>
        <p>
          <Link to="/products" className="btn primary">
            Browse the collection
          </Link>
        </p>
      </section>

      <p className="disclaimer">
        This site is coursework for MGT 409 at the Yale School of Management. It is a student
        project built against a sample dataset, not a real storefront, and no orders are
        processed.
      </p>
    </div>
  )
}
