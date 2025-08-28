import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch } from '@fortawesome/free-solid-svg-icons';
import ResultsPage from './ResultsPage';
import Footer from './Footer';
import axios from 'axios';

const ScholarSearch = () => {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (query.trim()) {
      setIsSearching(true);
      setError(null);
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/search/?query=${encodeURIComponent(query)}`
        );
        setResults(response.data);
      } catch (err) {
        setError('Failed to fetch results. Please try again.');
        setResults([]);
      }
    }
  };

  const handleBackToHome = () => {
    setIsSearching(false);
    setQuery('');
    setResults([]);
    setError(null);
  };

  // --- Scrape Functions ---
  const startScrape = async () => {
    try {
      const res = await axios.get(`${import.meta.env.VITE_API_URL}/scrape/`);
      setTaskId(res.data.task_id);
      setStatus('Started');
      checkStatus(res.data.task_id);
    } catch (err) {
      setStatus('Error starting scrape');
    }
  };

  const checkStatus = async (id) => {
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${import.meta.env.VITE_API_URL}/scrape/status/${id}/`);
        setStatus(res.data.status);
        if (res.data.status === 'SUCCESS' || res.data.status === 'FAILURE') {
          clearInterval(interval);
        }
      } catch (err) {
        setStatus('Error checking status');
        clearInterval(interval);
      }
    }, 3000);
  };

  if (isSearching) {
    return (
      <ResultsPage
        query={query}
        onSearch={handleSearch}
        results={results}
        error={error}
        onBackToHome={handleBackToHome}
      />
    );
  }

  return (
    <LandingPage
      query={query}
      setQuery={setQuery}
      onSearch={handleSearch}
      startScrape={startScrape}
      scrapeStatus={status}
    />
  );
};

// --- Landing Page Component ---
const LandingPage = ({ query, setQuery, onSearch, startScrape, scrapeStatus }) => (
  <div className="flex flex-col min-h-screen bg-white text-gray-800">
    <header className="flex justify-end items-center p-4 text-sm text-gray-600">
      <nav className="flex items-center space-x-4">
        <a href="#" className="hover:underline">Sign in</a>

        {/* Scrape Button */}
        <button
          onClick={startScrape}
          className="bg-sky-500 text-white px-3 py-1 rounded hover:bg-sky-600 text-xs"
        >
          Start Scrape
        </button>

        {scrapeStatus && <span className="text-xs text-gray-700 ml-2">{scrapeStatus}</span>}

        <div className="w-8 h-8 rounded-full bg-gray-200"></div>
      </nav>
    </header>

    <main className="flex-grow flex flex-col justify-center items-center p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-light text-sky-600">
          <img src="/culogo.png" alt="Coventry University Logo" className="inline-block h-10 mr-2" />
          <span className="font-bold">IR</span> Search Engine
        </h1>
      </div>

      <form onSubmit={onSearch} className="flex w-full max-w-2xl">
        <input
          type="text"
          className="flex-grow p-2 pl-4 border border-gray-300 rounded-l-full text-lg shadow-sm focus:outline-none focus:border-sky-500"
          placeholder="Search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          type="submit"
          className="flex items-center justify-center p-4 bg-sky-500 rounded-r-full text-white hover:bg-sky-600 transition-colors"
        >
          <FontAwesomeIcon icon={faSearch} />
        </button>
      </form>

      <div className="flex items-center mt-4 space-x-4 text-sm text-gray-500">
        <a href="https://pureportal.coventry.ac.uk/" className="hover:underline">All Articles</a>
      </div>
    </main>

    <Footer />
  </div>
);

export default ScholarSearch;
