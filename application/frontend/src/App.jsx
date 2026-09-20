import { useEffect, useState } from 'react'

function App() {
  const [alerts, setAlerts] = useState([])
  const [selectedTitle, setSelectedTitle] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false

    fetch('/all_alerts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`)
        }
        return response.json()
      })
      .then((data) => {
        if (cancelled) return
        setAlerts(data.alerts)
        setSelectedTitle((current) => current ?? data.alerts[0]?.title ?? null)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  const selected = alerts.find((alert) => alert.title === selectedTitle) ?? null

  return (
    <div className="app">
      <header className="banner">Proactive Care</header>
      <div className="layout">
        <nav className="menu">
          <h2 className="menu-title">Alerts</h2>
          <ul className="menu-list">
            {alerts.map((alert) => (
              <li key={alert.title}>
                <button
                  className={
                    alert.title === selectedTitle ? 'menu-item selected' : 'menu-item'
                  }
                  onClick={() => setSelectedTitle(alert.title)}
                >
                  {alert.title}
                </button>
              </li>
            ))}
          </ul>
        </nav>
        <main className="content">
          {loading && <p>Loading alerts...</p>}
          {error && <p className="error">{error}</p>}
          {!loading && !error && selected && (
            <pre className="alert-text">{selected.content}</pre>
          )}
          {!loading && !error && !selected && (
            <p>Select an alert to view its contents.</p>
          )}
        </main>
      </div>
    </div>
  )
}

export default App