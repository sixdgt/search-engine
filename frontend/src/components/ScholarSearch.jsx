import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch } from '@fortawesome/free-solid-svg-icons';
import ResultsPage from './ResultsPage';
import Footer from './Footer';

// Dummy data for search results
const searchResults = [
  {
    title: 'The impact of AI on academic publishing',
    authors: 'J. Smith, M. Johnson',
    year: '2023',
    journal: 'Journal of Computer Science',
    snippet: 'This study investigates how artificial intelligence is transforming the peer-review process...',
    citations: 15,
  },
  {
    title: 'A comprehensive review of machine learning algorithms',
    authors: 'A. Lee, B. Chen, P. Wang',
    year: '2022',
    journal: 'arXiv',
    snippet: 'We provide an in-depth analysis of the most commonly used machine learning techniques...',
    citations: 450,
  },
  // Add more dummy articles here
];

const ScholarSearch = () => {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      setIsSearching(true);
    }
  };

  const handleBackToHome = () => {
    setIsSearching(false);
    setQuery('');
  };

  if (isSearching) {
    return (
      <ResultsPage
        query={query}
        onSearch={handleSearch}
        results={searchResults}
      />
    );
  }

  return (
    <LandingPage
      query={query}
      setQuery={setQuery}
      onSearch={handleSearch}
    />
  );
};

// Landing Page Component (Presentational)
const LandingPage = ({ query, setQuery, onSearch }) => (
  <div className="flex flex-col min-h-screen bg-white text-gray-800">
    {/* Header */}
    <header className="flex justify-end items-center p-4 text-sm text-gray-600">
      <nav className="flex items-center space-x-4">
        <a href="#" className="hover:underline">Sign in</a>
        <div className="w-8 h-8 rounded-full bg-gray-200"></div>
      </nav>
    </header>

    {/* Main Content (Central Area) */}
    <main className="flex-grow flex flex-col justify-center items-center p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-light text-sky-600">
          <img src="/culogo.png" alt="Coventry University Logo" className="inline-block h-10 mr-2" />
          <span className="font-bold">IR</span> Search Engine
        </h1>
      </div>
      
      {/* Search Bar */}
      <form onSubmit={onSearch} className="flex w-full max-w-2xl">
        <input
          type="text"
          className="flex-grow p-2 pl-4 border border-gray-300 rounded-l-full text-lg shadow-sm focus:outline-none focus:border-sky-500"
          placeholder="Search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="flex items-center justify-center p-4 bg-sky-500 rounded-r-full text-white hover:bg-sky-600 transition-colors">
          <FontAwesomeIcon icon={faSearch} />
        </button>
      </form>
      
      {/* Search Options Links */}
      <div className="flex items-center mt-4 space-x-4 text-sm text-gray-500">
        <a href="https://pureportal.coventry.ac.uk/" className="hover:underline">All Articles</a>
      </div>
    </main>

    <Footer />
  </div>
);

export default ScholarSearch;
