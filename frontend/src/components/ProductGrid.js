const API_URL = "http://localhost:8000";

function SkeletonCard() {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden animate-pulse">
      <div className="w-full h-48 bg-gray-200 dark:bg-gray-800" />
      <div className="p-4">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2" />
        <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-2/3" />
      </div>
    </div>
  );
}

function ProductCard({ product, index }) {
  const imageName = product.image_path.replace(/\\/g, "/").split("/").pop();
  const imageUrl = `${API_URL}/images/${imageName}`;

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden hover:shadow-lg transition-shadow group">
      <div className="relative overflow-hidden">
        <img
          src={imageUrl}
          alt={product.name}
          className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
          onError={(e) => {
            e.target.src = "https://placehold.co/400x400?text=No+Image";
          }}
        />
        <div className="absolute top-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded-full">
          #{index + 1}
        </div>
      </div>
      <div className="p-4">
        <h3 className="text-sm font-medium text-gray-900 dark:text-white line-clamp-2 mb-1">
          {product.name}
        </h3>
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs px-2 py-1 bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400 rounded-full">
            {product.article_type}
          </span>
          <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded-full">
            {product.colour}
          </span>
          <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded-full">
            {product.gender}
          </span>
        </div>
        
        <a
          href={`https://www.myntra.com/${product.name.toLowerCase().replace(/ /g, '-')}`}
          target="_blank"
          rel="noreferrer"
          className="mt-3 block text-center text-xs py-2 bg-pink-50 dark:bg-pink-950 text-pink-600 dark:text-pink-400 rounded-lg hover:bg-pink-100 transition-colors font-medium"
        >
          View on Myntra →
        </a>
      </div>
    </div>
  );
}

function ProductGrid({ results, loading }) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {Array(8).fill(0).map((_, i) => <SkeletonCard key={i} />)}
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-20">
        <div className="text-6xl mb-4">🔍</div>
        <p className="text-gray-500 dark:text-gray-400 text-lg">
          Search for fashion products above
        </p>
        <p className="text-gray-400 dark:text-gray-600 text-sm mt-2">
          Try "blue casual shirt" or upload a product image
        </p>
      </div>
    );
  }

  return (
    <div>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        {results.length} results found
      </p>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {results.map((product, index) => (
          <ProductCard key={product.id} product={product} index={index} />
        ))}
      </div>
    </div>
  );
}

export default ProductGrid;