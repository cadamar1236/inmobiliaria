import { useState, useEffect, useCallback, useRef, useMemo } from 'react'
import { Search, SlidersHorizontal, Star, ChevronLeft, ChevronRight, X, MapPin, Home, DollarSign, Maximize, Heart, Share2, Clock, Shield, TrendingUp, Users, Building, Filter, Grid3X3, List, ArrowUpDown } from 'lucide-react'

const BASE = window.__BACKEND_URL__ || '';

async function apiFetch(path, opts = {}) {
  for (let i = 0; i < 5; i++) {
    try {
      const r = await fetch(BASE + path, opts);
      if (r.ok) return r.json();
    } catch (_) {}
    await new Promise(r => setTimeout(r, 1500));
  }
  return null;
}

const mockListings = [
  { id: 1, title: "Piso luminoso en el centro", price: 250000, location: "Madrid Centro", size: 85, bedrooms: 3, bathrooms: 2, rating: 4.8, category: "Pisos", image: "", featured: true, tags: ["Reformado", "Luminoso"], description: "Amplio piso completamente reformado con vistas espectaculares" },
  { id: 2, title: "Ático con terraza", price: 320000, location: "Barcelona", size: 110, bedrooms: 3, bathrooms: 2, rating: 4.9, category: "Áticos", image: "", featured: true, tags: ["Terraza", "Vistas"], description: "Ático exclusivo con terraza privada de 30m²" },
  { id: 3, title: "Casa adosada con jardín", price: 450000, location: "Valencia", size: 150, bedrooms: 4, bathrooms: 3, rating: 4.7, category: "Casas", image: "", featured: true, tags: ["Jardín", "Garaje"], description: "Casa adosada en zona residencial con amplio jardín" },
  { id: 4, title: "Estudio céntrico", price: 120000, location: "Sevilla", size: 45, bedrooms: 1, bathrooms: 1, rating: 4.5, category: "Estudios", image: "", tags: ["Céntrico", "Amueblado"], description: "Estudio ideal para inversión en pleno centro histórico" },
  { id: 5, title: "Dúplex con piscina", price: 380000, location: "Málaga", size: 130, bedrooms: 3, bathrooms: 2, rating: 4.6, category: "Dúplex", image: "", tags: ["Piscina", "Parking"], description: "Dúplex en urbanización con piscina comunitaria" },
  { id: 6, title: "Local comercial", price: 180000, location: "Bilbao", size: 90, bedrooms: 0, bathrooms: 1, rating: 4.3, category: "Locales", image: "", tags: ["Esquina", "Acondicionado"], description: "Local comercial en esquina con gran visibilidad" },
  { id: 7, title: "Chalet independiente", price: 650000, location: "Marbella", size: 200, bedrooms: 5, bathrooms: 3, rating: 4.9, category: "Chalets", image: "", tags: ["Lujo", "Piscina privada"], description: "Exclusivo chalet con piscina privada y vistas al mar" },
  { id: 8, title: "Piso de obra nueva", price: 290000, location: "Madrid Norte", size: 95, bedrooms: 3, bathrooms: 2, rating: 4.7, category: "Pisos", image: "", tags: ["Obra nueva", "Garaje"], description: "Piso de obra nueva con acabados de alta calidad" },
  { id: 9, title: "Casa rural con terreno", price: 220000, location: "Toledo", size: 180, bedrooms: 4, bathrooms: 2, rating: 4.4, category: "Casas", image: "", tags: ["Rural", "Tranquilo"], description: "Casa rural ideal para desconectar con parcela de 500m²" },
  { id: 10, title: "Ático dúplex", price: 410000, location: "Valencia", size: 140, bedrooms: 4, bathrooms: 3, rating: 4.8, category: "Áticos", image: "", tags: ["Dúplex", "Terraza"], description: "Ático dúplex con terraza de 50m² y vistas al mar" },
  { id: 11, title: "Piso económico", price: 85000, location: "Almería", size: 60, bedrooms: 2, bathrooms: 1, rating: 4.2, category: "Pisos", image: "", tags: ["Económico", "Céntrico"], description: "Piso económico ideal para primera vivienda" },
  { id: 12, title: "Loft industrial", price: 195000, location: "Barcelona", size: 80, bedrooms: 2, bathrooms: 1, rating: 4.6, category: "Lofts", image: "", tags: ["Industrial", "Moderno"], description: "Loft estilo industrial con techos altos y luz natural" }
];

const categories = ["Todas", "Pisos", "Áticos", "Casas", "Chalets", "Estudios", "Dúplex", "Locales", "Lofts"];

function QuickViewModal({ listing, onClose }) {
  useEffect(() => {
    const handleEsc = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  if (!listing) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-[#0a0e1a] border border-white/10 rounded-2xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto fade-in" onClick={e => e.stopPropagation()}>
        <div className="relative h-64 bg-gradient-to-br from-[#2E86AB]/20 to-[#F18F01]/20 flex items-center justify-center">
          <div className="text-6xl opacity-30"><Building size={80} /></div>
          <button onClick={onClose} className="absolute top-4 right-4 p-2 bg-white/10 hover:bg-white/20 rounded-full transition-all">
            <X size={20} />
          </button>
        </div>
        <div className="p-6 space-y-4">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold">{listing.title}</h2>
              <p className="text-white/60 flex items-center gap-1 mt-1"><MapPin size={14} /> {listing.location}</p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold gradient-text">{listing.price.toLocaleString()}€</p>
              <div className="flex items-center gap-1 text-yellow-400 mt-1">
                <Star size={16} fill="currentColor" /> {listing.rating}
              </div>
            </div>
          </div>
          <p className="text-white/70">{listing.description}</p>
          <div className="flex gap-4 text-sm">
            <span className="flex items-center gap-1"><Maximize size={14} /> {listing.size}m²</span>
            <span className="flex items-center gap-1"><Home size={14} /> {listing.bedrooms} hab</span>
            <span className="flex items-center gap-1"><DollarSign size={14} /> {listing.bathrooms} baños</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {(listing.tags || []).map(tag => (
              <span key={tag} className="px-3 py-1 bg-[#F18F01]/10 text-[#F18F01] rounded-full text-sm">{tag}</span>
            ))}
          </div>
          <div className="flex gap-3">
            <button className="flex-1 bg-[#2E86AB] hover:bg-[#2E86AB]/80 text-white py-3 rounded-xl font-semibold transition-all">Contactar</button>
            <button className="p-3 border border-white/10 hover:border-white/20 rounded-xl transition-all"><Heart size={20} /></button>
            <button className="p-3 border border-white/10 hover:border-white/20 rounded-xl transition-all"><Share2 size={20} /></button>
          </div>
        </div>
      </div>
    </div>
  );
}

function Sidebar({ selectedCategory, setSelectedCategory, priceRange, setPriceRange, minRating, setMinRating, sidebarOpen }) {
  return (
    <aside className={`w-72 flex-shrink-0 flex flex-col h-full border-r border-white/5 bg-white/[0.02] p-5 ${sidebarOpen ? '' : 'hidden lg:flex'}`}>
      <div className="flex items-center gap-2 mb-6">
        <Filter size={20} />
        <h3 className="font-semibold">Filtros</h3>
      </div>
      
      <div className="mb-6">
        <h4 className="text-sm text-white/60 mb-3">Categorías</h4>
        <div className="space-y-1">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${
                selectedCategory === cat ? 'bg-[#2E86AB]/20 text-[#2E86AB]' : 'hover:bg-white/5 text-white/70'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="mb-6">
        <h4 className="text-sm text-white/60 mb-3">Precio máximo: {priceRange.toLocaleString()}€</h4>
        <input
          type="range"
          min="50000"
          max="1000000"
          step="10000"
          value={priceRange}
          onChange={(e) => setPriceRange(Number(e.target.value))}
          className="w-full accent-[#F18F01]"
        />
        <div className="flex justify-between text-xs text-white/40 mt-1">
          <span>50.000€</span>
          <span>1.000.000€</span>
        </div>
      </div>

      <div>
        <h4 className="text-sm text-white/60 mb-3">Valoración mínima: {minRating}</h4>
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map(star => (
            <button key={star} onClick={() => setMinRating(star)} className={`transition-all ${star <= minRating ? 'text-yellow-400' : 'text-white/20'}`}>
              <Star size={20} fill={star <= minRating ? 'currentColor' : 'none'} />
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}

function ListingCard({ listing, onQuickView }) {
  return (
    <div className="glass p-0 overflow-hidden fade-in group cursor-pointer" onClick={() => onQuickView(listing)}>
      <div className="h-48 bg-gradient-to-br from-[#2E86AB]/20 to-[#F18F01]/20 flex items-center justify-center relative overflow-hidden">
        <div className="text-4xl opacity-20 group-hover:scale-110 transition-transform duration-500"><Building size={64} /></div>
        {listing.featured && (
          <div className="absolute top-3 left-3 px-3 py-1 bg-[#F18F01] text-white text-xs font-semibold rounded-full">
            Destacado
          </div>
        )}
        <button className="absolute top-3 right-3 p-2 bg-black/40 hover:bg-black/60 rounded-full transition-all opacity-0 group-hover:opacity-100" onClick={(e) => { e.stopPropagation(); }}>
          <Heart size={16} />
        </button>
      </div>
      <div className="p-4 space-y-2">
        <div className="flex items-start justify-between">
          <h3 className="font-semibold truncate max-w-[70%]">{listing.title}</h3>
          <div className="flex items-center gap-1 text-yellow-400 text-sm">
            <Star size={14} fill="currentColor" /> {listing.rating}
          </div>
        </div>
        <p className="text-white/60 text-sm flex items-center gap-1"><MapPin size={12} /> {listing.location}</p>
        <div className="flex items-center gap-4 text-xs text-white/50">
          <span className="flex items-center gap-1"><Maximize size={12} /> {listing.size}m²</span>
          <span className="flex items-center gap-1"><Home size={12} /> {listing.bedrooms} hab</span>
        </div>
        <p className="text-xl font-bold gradient-text">{listing.price.toLocaleString()}€</p>
        <div className="flex flex-wrap gap-1.5">
          {(listing.tags || []).slice(0, 3).map(tag => (
            <span key={tag} className="px-2 py-0.5 bg-white/5 rounded text-xs">{tag}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

function FeaturedCarousel({ listings, onQuickView }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const featured = useMemo(() => (listings || []).filter(l => l.featured), [listings]);

  const next = useCallback(() => setCurrentIndex(prev => (prev + 1) % Math.max(featured.length, 1)), [featured.length]);
  const prev = useCallback(() => setCurrentIndex(prev => (prev - 1 + featured.length) % Math.max(featured.length, 1)), [featured.length]);

  useEffect(() => {
    const timer = setInterval(next, 5000);
    return () => clearInterval(timer);
  }, [next]);

  if (featured.length === 0) return null;

  return (
    <div className="relative mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold gradient-text">Destacados</h2>
        <div className="flex gap-1">
          <button onClick={prev} className="p-2 bg-white/5 hover:bg-white/10 rounded-lg transition-all"><ChevronLeft size={18} /></button>
          <button onClick={next} className="p-2 bg-white/5 hover:bg-white/10 rounded-lg transition-all"><ChevronRight size={18} /></button>
        </div>
      </div>
      <div className="overflow-hidden rounded-xl">
        <div className="flex transition-transform duration-500" style={{ transform: `translateX(-${currentIndex * 100}%)` }}>
          {featured.map(listing => (
            <div key={listing.id} className="min-w-full flex-shrink-0 px-1">
              <div className="glass p-0 overflow-hidden cursor-pointer" onClick={() => onQuickView(listing)}>
                <div className="h-64 bg-gradient-to-br from-[#2E86AB]/30 to-[#F18F01]/30 flex items-center justify-center relative">
                  <div className="text-6xl opacity-20"><Building size={96} /></div>
                  <div className="absolute bottom-4 left-4 right-4 bg-black/60 backdrop-blur-sm p-4 rounded-xl">
                    <h3 className="text-xl font-bold">{listing.title}</h3>
                    <p className="text-white/70 text-sm">{listing.location}</p>
                    <p className="text-2xl font-bold gradient-text mt-1">{listing.price.toLocaleString()}€</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Pagination({ currentPage, totalPages, onPageChange }) {
  return (
    <div className="flex items-center justify-center gap-2 mt-8">
      <button onClick={() => onPageChange(currentPage - 1)} disabled={currentPage === 1} className="p-2 bg-white/5 hover:bg-white/10 rounded-lg disabled:opacity-30 transition-all">
        <ChevronLeft size={18} />
      </button>
      {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          className={`w-10 h-10 rounded-lg text-sm transition-all ${
            page === currentPage ? 'bg-[#2E86AB] text-white' : 'bg-white/5 hover:bg-white/10 text-white/70'
          }`}
        >
          {page}
        </button>
      ))}
      <button onClick={() => onPageChange(currentPage + 1)} disabled={currentPage === totalPages} className="p-2 bg-white/5 hover:bg-white/10 rounded-lg disabled:opacity-30 transition-all">
        <ChevronRight size={18} />
      </button>
    </div>
  );
}

export default function App() {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('Todas');
  const [priceRange, setPriceRange] = useState(1000000);
  const [minRating, setMinRating] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [quickViewListing, setQuickViewListing] = useState(null);
  const [viewMode, setViewMode] = useState('grid');
  const [sortBy, setSortBy] = useState('precio');
  const [sortOrder, setSortOrder] = useState('desc');

  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = ':root { --accent: #00C9A7; --accent2: #1E3A5F; }';
      document.head.appendChild(style);
    return () => style.remove();
  }, []);

  useEffect(() => {
    async function fetchData() {
      const data = await apiFetch('/api/listings');
      setListings(data || mockListings);
      setLoading(false);
    }
    fetchData();
  }, []);

  const filteredListings = useMemo(() => {
    let result = listings || [];
    if (selectedCategory !== 'Todas') result = result.filter(l => l.category === selectedCategory);
    if (searchQuery) result = result.filter(l => l.title.toLowerCase().includes(searchQuery.toLowerCase()) || l.location.toLowerCase().includes(searchQuery.toLowerCase()));
    result = result.filter(l => l.price <= priceRange);
    result = result.filter(l => l.rating >= minRating);
    result.sort((a, b) => {
      let val = sortBy === 'precio' ? a.price - b.price : sortBy === 'rating' ? a.rating - b.rating : a.size - b.size;
      return sortOrder === 'asc' ? val : -val;
    });
    return result;
  }, [listings, selectedCategory, searchQuery, priceRange, minRating, sortBy, sortOrder]);

  const itemsPerPage = 8;
  const totalPages = Math.ceil((filteredListings || []).length / itemsPerPage);
  const paginatedListings = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return (filteredListings || []).slice(start, start + itemsPerPage);
  }, [filteredListings, currentPage]);

  useEffect(() => { setCurrentPage(1); }, [searchQuery, selectedCategory, priceRange, minRating]);

  return (
    <div className="flex h-screen overflow-hidden bg-[#06080f] text-slate-100 font-[Inter]">
      <Sidebar selectedCategory={selectedCategory} setSelectedCategory={setSelectedCategory} priceRange={priceRange} setPriceRange={setPriceRange} minRating={minRating} setMinRating={setMinRating} sidebarOpen={sidebarOpen} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-14 flex items-center justify-between px-6 border-b border-white/5 flex-shrink-0">
          <div className="flex items-center gap-4 flex-1">
            <button className="lg:hidden p-2 hover:bg-white/5 rounded-lg" onClick={() => setSidebarOpen(!sidebarOpen)}>
              <Filter size={18} />
            </button>
            <div className="relative flex-1 max-w-lg">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
              <input
                type="text"
                placeholder="Buscar viviendas..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-[#2E86AB] transition-all"
              />
            </div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-white/5 border border-white/10 rounded-xl py-2 px-3 text-sm focus:outline-none focus:border-[#2E86AB]"
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex border border-white/10 rounded-xl overflow-hidden">
              <button onClick={() => setViewMode('grid')} className={`p-2 ${viewMode === 'grid' ? 'bg-[#2E86AB]/20 text-[#2E86AB]' : 'hover:bg-white/5'}`}><Grid3X3 size={16} /></button>
              <button onClick={() => setViewMode('list')} className={`p-2 ${viewMode === 'list' ? 'bg-[#2E86AB]/20 text-[#2E86AB]' : 'hover:bg-white/5'}`}><List size={16} /></button>
            </div>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-white/5 border border-white/10 rounded-xl py-2 px-3 text-sm focus:outline-none focus:border-[#2E86AB]"
            >
              <option value="precio">Precio</option>
              <option value="rating">Valoración</option>
              <option value="size">Tamaño</option>
            </select>
            <button onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')} className="p-2 hover:bg-white/5 rounded-lg transition-all">
              <ArrowUpDown size={16} className="text-white/60" />
            </button>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          <div className="mb-6">
            <h1 className="text-3xl font-bold gradient-text mb-2">InmoDirect</h1>
            <p className="text-white/50">Vende y compra viviendas sin comisiones de terceros</p>
          </div>

          <div className="flex items-center gap-4 mb-6 text-sm text-white/50">
            <span className="flex items-center gap-1"><Shield size={14} className="text-[#2E86AB]" /> Sin comisiones</span>
            <span className="flex items-center gap-1"><TrendingUp size={14} className="text-[#F18F01]" /> Transparencia total</span>
            <span className="flex items-center gap-1"><Users size={14} /> Propietarios directos</span>
            <span className="flex items-center gap-1"><Clock size={14} /> Proceso ágil</span>
          </div>

          <FeaturedCarousel listings={listings} onQuickView={setQuickViewListing} />

          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-white/50">{filteredListings.length} viviendas encontradas</p>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="glass p-0 overflow-hidden shimmer h-80" />
              ))}
            </div>
          ) : paginatedListings.length === 0 ? (
            <div className="text-center py-20 text-white/40">
              <Building size={48} className="mx-auto mb-4 opacity-30" />
              <p className="text-lg">No se encontraron viviendas con estos filtros</p>
              <button onClick={() => { setSearchQuery(''); setSelectedCategory('Todas'); setPriceRange(1000000); setMinRating(1); }} className="mt-4 text-[#2E86AB] hover:underline">Limpiar filtros</button>
            </div>
          ) : viewMode === 'grid' ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {paginatedListings.map(listing => (
                <ListingCard key={listing.id} listing={listing} onQuickView={setQuickViewListing} />
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {paginatedListings.map(listing => (
                <div key={listing.id} className="glass p-4 flex items-center gap-4 cursor-pointer hover:bg-white/5 transition-all fade-in" onClick={() => setQuickViewListing(listing)}>
                  <div className="w-20 h-20 bg-gradient-to-br from-[#2E86AB]/20 to-[#F18F01]/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Building size={32} className="opacity-30" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold truncate">{listing.title}</h3>
                    <p className="text-white/60 text-sm flex items-center gap-1"><MapPin size={12} /> {listing.location}</p>
                    <div className="flex items-center gap-3 text-xs text-white/50 mt-1">
                      <span>{listing.size}m²</span>
                      <span>{listing.bedrooms} hab</span>
                      <span className="flex items-center gap-1 text-yellow-400"><Star size={10} fill="currentColor" /> {listing.rating}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-bold gradient-text">{listing.price.toLocaleString()}€</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {totalPages > 1 && (
            <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={setCurrentPage} />
          )}
        </main>
      </div>
      <QuickViewModal listing={quickViewListing} onClose={() => setQuickViewListing(null)} />
    </div>
  );
}