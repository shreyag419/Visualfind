import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";

const API_URL = "http://localhost:8000";

const ARTICLE_TYPES = [
  "Baby Dolls", "Bath Robe", "Belts", "Blazers", "Booties", "Boxers",
  "Bra", "Briefs", "Camisoles", "Capris", "Casual Shoes", "Churidar",
  "Clothing Set", "Dresses", "Dupatta", "Flats", "Flip Flops",
  "Formal Shoes", "Heels", "Innerwear Vests", "Jackets", "Jeans",
  "Jeggings", "Jumpsuit", "Kurta Sets", "Kurtas", "Kurtis", "Leggings",
  "Lehenga Choli", "Lounge Pants", "Lounge Shorts", "Lounge Tshirts",
  "Nehru Jackets", "Night suits", "Nightdress", "Patiala", "Rain Jacket",
  "Rain Trousers", "Robe", "Rompers", "Salwar", "Salwar and Dupatta",
  "Sandals", "Sarees", "Shapewear", "Shirts", "Shorts", "Shrug",
  "Skirts", "Sports Sandals", "Sports Shoes", "Stockings", "Suspenders",
  "Sweaters", "Sweatshirts", "Swimwear", "Tights", "Tops", "Track Pants",
  "Tracksuits", "Trousers", "Trunk", "Tshirts", "Tunics", "Waistcoat"
];

function SearchBar({ setResults, setLoading, searchMode, setSearchMode }) {
  const [query, setQuery] = useState("");
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [imageWeight, setImageWeight] = useState(0.7);
  const [gender, setGender] = useState("");
  const [articleType, setArticleType] = useState("");
  const [error, setError] = useState("");

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [] },
    multiple: false
  });

  const handleSearch = async () => {
    setError("");
    setLoading(true);
    setResults([]);

    try {
      let response;

      if (searchMode === "text") {
        if (!query.trim()) {
          setError("Please enter a search query");
          setLoading(false);
          return;
        }
        response = await axios.post(`${API_URL}/search/text`, {
          query,
          top_k: 12,
          gender: gender || null,
          article_type: articleType || null
        });
        setResults(response.data.results);

      } else if (searchMode === "image") {
        if (!image) {
          setError("Please upload an image");
          setLoading(false);
          return;
        }
        const formData = new FormData();
        formData.append("file", image);
        formData.append("top_k", 12);
        response = await axios.post(`${API_URL}/search/image`, formData);
        setResults(response.data.results);

      } else if (searchMode === "composed") {
        if (!image || !query.trim()) {
          setError("Please provide both an image and text description");
          setLoading(false);
          return;
        }
        const formData = new FormData();
        formData.append("file", image);
        formData.append("query", query);
        formData.append("image_weight", imageWeight);
        formData.append("top_k", 12);
        response = await axios.post(`${API_URL}/search/composed`, formData);
        setResults(response.data.results);
      }

    } catch (err) {
      setError("Search failed. Make sure the API server is running.");
    } finally {
      setLoading(false);
    }
  };

  const clearImage = () => {
    setImage(null);
    setImagePreview(null);
  };

  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-800 p-6 mb-8">

      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
        Search Fashion Products
      </h1>
      <p className="text-gray-500 dark:text-gray-400 mb-6">
        Search by text, image, or combine both for precise results
      </p>

      {/* Mode Toggle */}
      <div className="flex gap-2 mb-6">
        {["text", "image", "composed"].map((mode) => (
          <button
            key={mode}
            onClick={() => setSearchMode(mode)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors capitalize ${
              searchMode === mode
                ? "bg-blue-600 text-white"
                : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700"
            }`}
          >
            {mode === "text" ? "📝 Text" : mode === "image" ? "🖼️ Image" : "✨ Composed"}
          </button>
        ))}
      </div>

      {/* Image Upload */}
      {(searchMode === "image" || searchMode === "composed") && (
        <div className="mb-4">
          {imagePreview ? (
            <div className="relative inline-block">
              <img
                src={imagePreview}
                alt="Preview"
                className="w-40 h-40 object-cover rounded-xl border border-gray-200 dark:border-gray-700"
              />
              <button
                onClick={clearImage}
                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600"
              >
                ✕
              </button>
            </div>
          ) : (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-950"
                  : "border-gray-300 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-500"
              }`}
            >
              <input {...getInputProps()} />
              <div className="text-4xl mb-2">📸</div>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                {isDragActive
                  ? "Drop it here..."
                  : "Drag & drop an image, or click to browse"}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Text Input */}
      {(searchMode === "text" || searchMode === "composed") && (
        <div className="mb-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder={
              searchMode === "composed"
                ? "Describe modifications... e.g. 'but in black'"
                : "Search for products... e.g. 'blue casual shirt for men'"
            }
            className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
          />
        </div>
      )}

      {/* Fusion Slider */}
      {searchMode === "composed" && (
        <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              🖼️ Image influence
            </span>
            <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
              {Math.round(imageWeight * 100)}%
            </span>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              📝 Text influence
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={imageWeight}
            onChange={(e) => setImageWeight(parseFloat(e.target.value))}
            className="w-full accent-blue-600"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>Image only</span>
            <span>Equal</span>
            <span>Text only</span>
          </div>
        </div>
      )}

      {/* Filters Row */}
      <div className="flex gap-3 mb-4 flex-wrap">
        <select
          value={gender}
          onChange={(e) => setGender(e.target.value)}
          className="px-4 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All genders</option>
          <option value="Men">Men</option>
          <option value="Women">Women</option>
          <option value="Boys">Boys</option>
          <option value="Girls">Girls</option>
          <option value="Unisex">Unisex</option>
        </select>

        <select
          value={articleType}
          onChange={(e) => setArticleType(e.target.value)}
          className="px-4 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 flex-1"
        >
          <option value="">All article types</option>
          {ARTICLE_TYPES.map((type) => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>

      {/* Error */}
      {error && (
        <p className="text-red-500 text-sm mb-4">{error}</p>
      )}

      {/* Search Button */}
      <button
        onClick={handleSearch}
        className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-colors text-lg"
      >
        Search
      </button>
    </div>
  );
}

export default SearchBar;