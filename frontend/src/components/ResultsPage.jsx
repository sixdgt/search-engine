// Results Page Component
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch } from '@fortawesome/free-solid-svg-icons';
import Footer from './Footer';
const ResultsPage = ({ query, onSearch, results }) => (
  <div className="flex flex-col min-h-screen bg-white text-gray-800">
    {/* Header with Search Bar */}
    <header className="flex items-center p-4 border-b border-gray-200">
      <h1 className="text-2xl font-light text-sky-800 mr-8">
        <a href=""><img src="/culogo.png" alt="Coventry University Logo" className="inline-block h-10 mr-2" /></a>
        <span className="font-bold">IR</span> Search Engine
      </h1>
      <form onSubmit={onSearch} className="flex w-full max-w-xl">
        <input
          type="text"
          className="flex-grow p-2 pl-4 border border-gray-300 rounded-l-full text-lg shadow-sm focus:outline-none focus:border-sky-500"
          placeholder="Search"
          defaultValue={query}
        />
        <button type="submit" className="flex items-center justify-center p-4 bg-sky-500 rounded-r-full text-white hover:bg-sky-600 transition-colors">
          <FontAwesomeIcon icon={faSearch} />
        </button>
      </form>
    </header>

    {/* Main Content */}
    <main className="flex flex-grow p-8">
      {/* Left Sidebar for Filters */}
      <div className="w-1/4 pr-8 border-r border-gray-200">
        <h2 className="font-bold mb-4">Search results</h2>
        <ul className="space-y-2 text-sm text-gray-600">
          <li><a href="#" className="hover:underline text-sky-600">Anytime</a></li>
          <li><a href="#" className="hover:underline">Since 2024</a></li>
          <li><a href="#" className="hover:underline">Since 2023</a></li>
          <li><a href="#" className="hover:underline">Since 2020</a></li>
          <li className="pt-2"><a href="#" className="hover:underline">Custom range...</a></li>
        </ul>
      </div>

      {/* Article Results List */}
      <div className="w-3/4 pl-8">
        <p className="text-sm text-gray-500 mb-4">About {results.length} results ({Math.random().toFixed(2)} seconds)</p>
        
        {results.map((article, index) => (
          <div key={index} className="mb-6">
            <h3 className="text-xl text-blue-700 hover:underline cursor-pointer">{article.title}</h3>
            <p className="text-sm text-green-700">{article.authors} - {article.year} - {article.journal}</p>
            <p className="text-gray-700 mt-1">{article.snippet}</p>
            <p className="text-sm text-gray-500 mt-2">
              <a href="#" className="hover:underline text-blue-600">Cited by {article.citations}</a>
            </p>
          </div>
        ))}
      </div>
    </main>
    
    <Footer />
  </div>
);

export default ResultsPage;