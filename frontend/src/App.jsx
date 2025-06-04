import ChatWidget from './ChatWidget'
import './App.css'

function App() {
  return (
    <div className="App">
      <div className="app-container">
        <header className="app-header">
          <h1>🏠 Lead-to-Lease Chat Concierge</h1>
          <p>Find your perfect apartment and schedule a tour instantly!</p>
        </header>

        <main className="app-main">
          <ChatWidget />
        </main>

        <footer className="app-footer">
          <p>Powered by FastAPI & React • Built for Homewiz</p>
        </footer>
      </div>
    </div>
  )
}

export default App
