import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Heart, ShoppingBag, User, Search } from "lucide-react";
import { Link } from "react-router-dom";
import { useState, useRef } from "react";

export const Header = () => {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    if (value.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    timeoutRef.current = setTimeout(() => {
      fetch("https://agentic-fastapi-app-950029052556.europe-west1.run.app/db/all")
        .then(res => res.json())
        .then(data => {
          const profiles = Array.isArray(data.user_profiles) ? data.user_profiles : [];
          const filtered = profiles.filter((artisan: any) =>
            (artisan.name && artisan.name.toLowerCase().includes(value.toLowerCase())) ||
            (artisan.craft_type && artisan.craft_type.toLowerCase().includes(value.toLowerCase())) ||
            (typeof artisan.materials === 'string' && artisan.materials.toLowerCase().includes(value.toLowerCase()))
          );
          setSuggestions(filtered.slice(0, 8));
          setShowSuggestions(true);
        });
    }, 250);
  };

  const handleSuggestionClick = (artisan: any) => {
    window.location.href = `/artisans?category=${encodeURIComponent(artisan.craft_type || "")}`;
    setShowSuggestions(false);
    setQuery(artisan.craft_type || "");
  };

  return (
    <header className="sticky top-0 z-50 bg-ivory/95 backdrop-blur supports-[backdrop-filter]:bg-ivory/80 border-b border-gold/20 shadow-warm">
      <div className="container mx-auto px-4 h-20 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        {/* Mobile search bar */}
        <div className="block md:hidden w-full pt-2 relative">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-saffron h-5 w-5" />
            <Input
              value={query}
              onChange={handleSearchChange}
              onFocus={() => query.length > 1 && setShowSuggestions(true)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
              placeholder="Search crafts, masters..."
              className="pl-10 h-11 border-2 border-gold/30 focus:border-saffron bg-ivory/80 backdrop-blur-sm rounded-xl text-burnt-umber placeholder:text-sandstone"
            />
            {showSuggestions && suggestions.length > 0 && (
              <ul className="absolute left-0 right-0 mt-1 bg-white border border-gold/30 rounded shadow-lg z-50 max-h-60 overflow-auto">
                {suggestions.map((artisan, idx) => (
                  <li
                    key={artisan.user_id || idx}
                    className="px-4 py-2 hover:bg-sandstone cursor-pointer text-left"
                    onMouseDown={() => handleSuggestionClick(artisan)}
                  >
                    <span className="font-semibold text-burnt-umber">{artisan.name}</span>
                    {artisan.craft_type && (
                      <span className="ml-2 text-xs text-saffron">({artisan.craft_type})</span>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
        <div className="flex items-center w-full md:w-auto space-x-10">
          <Link to="/" className="text-3xl font-serif font-bold text-transparent bg-gradient-temple bg-clip-text">
            🪷 Sacred Crafts
          </Link>
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              to="/artisans?category=pottery" 
              className="text-burnt-umber hover:text-saffron transition-colors font-medium"
            >
              Sacred Pottery
            </Link>
            <Link 
              to="/artisans?category=textiles" 
              className="text-burnt-umber hover:text-marigold transition-colors font-medium"
            >
              Blessed Textiles
            </Link>
            <Link 
              to="/artisans?category=woodwork" 
              className="text-burnt-umber hover:text-peacock-blue transition-colors font-medium"
            >
              Temple Arts
            </Link>
            <Link 
              to="/artisans" 
              className="text-burnt-umber hover:text-lotus-pink transition-colors font-medium"
            >
              Masters
            </Link>
          </nav>
        </div>
        {/* Desktop search bar */}
        <div className="hidden md:flex items-center space-x-3 flex-1 max-w-xs relative">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-saffron h-5 w-5" />
            <Input
              value={query}
              onChange={handleSearchChange}
              onFocus={() => query.length > 1 && setShowSuggestions(true)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
              placeholder="Search crafts, masters..."
              className="pl-10 h-11 border-2 border-gold/30 focus:border-saffron bg-ivory/80 backdrop-blur-sm rounded-xl text-burnt-umber placeholder:text-sandstone"
            />
            {showSuggestions && suggestions.length > 0 && (
              <ul className="absolute left-0 right-0 mt-1 bg-white border border-gold/30 rounded shadow-lg z-50 max-h-60 overflow-auto">
                {suggestions.map((artisan, idx) => (
                  <li
                    key={artisan.user_id || idx}
                    className="px-4 py-2 hover:bg-sandstone cursor-pointer text-left"
                    onMouseDown={() => handleSuggestionClick(artisan)}
                  >
                    <span className="font-semibold text-burnt-umber">{artisan.name}</span>
                    {artisan.craft_type && (
                      <span className="ml-2 text-xs text-saffron">({artisan.craft_type})</span>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-3 mt-2 md:mt-0">
          <Button variant="ghost" size="icon" className="hidden sm:flex text-saffron hover:text-marigold hover:bg-saffron/10">
            <Heart className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon" className="text-peacock-blue hover:text-saffron hover:bg-peacock-blue/10">
            <ShoppingBag className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon" className="text-lotus-pink hover:text-gold hover:bg-lotus-pink/10">
            <User className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
};