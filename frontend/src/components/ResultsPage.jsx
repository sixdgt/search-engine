// Results Page Component
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch } from '@fortawesome/free-solid-svg-icons';
import Footer from './Footer';
const ResultsPage = ({ query, onSearch, results, error, onBackToHome }) => (
  <div className="flex flex-col min-h-screen bg-white text-gray-800">
    <header className="flex justify-between items-center p-4 text-sm text-gray-600">
      <div className="flex items-center space-x-4">
        <button onClick={onBackToHome} className="text-sky-600 hover:underline">
          Back to Home
        </button>

        <button
          onClick={startScrape}
          className="bg-sky-500 text-white px-3 py-1 rounded hover:bg-sky-600 text-xs"
        >
          Start Scrape
        </button>
      </div>

      <nav className="flex items-center space-x-4">
        <a href="#" className="hover:underline">Sign in</a>
        <div className="w-8 h-8 rounded-full bg-gray-200"></div>
      </nav>
    </header>


    <main className="flex-grow p-8">
      <form onSubmit={onSearch} className="flex w-full max-w-2xl mb-8">
        <input
          type="text"
          className="flex-grow p-2 pl-4 border border-gray-300 rounded-l-full text-lg shadow-sm focus:outline-none focus:border-sky-500"
          placeholder="Search"
          value={query}
          onChange={(e) => query(e.target.value)}
        />
        <button type="submit" className="flex items-center justify-center p-4 bg-sky-500 rounded-r-full text-white hover:bg-sky-600 transition-colors">
          <FontAwesomeIcon icon={faSearch} />
        </button>
      </form>

      {error && <p className="text-red-500 mb-4">{error}</p>}

      <h2 className="text-2xl font-semibold mb-4">Search Results for "{query}"</h2>
      {results.length === 0 && !error ? (
        <p>No results found.</p>
      ) : (
        <ul className="space-y-4">
          {results.map((result, idx) => (
            <li key={idx} className="border-b pb-4">
              <a
                href={result.pub_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sky-600 hover:underline text-lg"
              >
                {result.title} ({result.year})
              </a>
              <p className="text-sm text-gray-600">Authors: {result.authors.join(', ')}</p>
              {result.journal && <p className="text-sm text-gray-600">Journal: {result.journal}</p>}
              {result.snippet && <p className="text-sm text-gray-500">{result.snippet}</p>}
              {result.citations && <p className="text-sm text-gray-500">Citations: {result.citations}</p>}
            </li>
          ))}
        </ul>
      )}
    </main>
    <Footer />
  </div>
);

export default ResultsPage;