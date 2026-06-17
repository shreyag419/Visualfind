import { useState } from "react";
import SearchBar from "./components/SearchBar";
import ProductGrid from "./components/ProductGrid";
import Navbar from "./components/Navbar";

function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [searchMode, setSearchMode] = useState("text");

  return (
    <div className={darkMode ? "dark" : ""}>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors duration-300">
        <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />
        <main className="max-w-7xl mx-auto px-4 py-8">
          <SearchBar
            setResults={setResults}
            setLoading={setLoading}
            searchMode={searchMode}
            setSearchMode={setSearchMode}
          />
          <ProductGrid results={results} loading={loading} />
        </main>
      </div>
    </div>
  );
}

export default App;