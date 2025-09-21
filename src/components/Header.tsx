import { Button } from "@/components/ui/button";
import { Heart, ShoppingBag, User } from "lucide-react";

export const Header = () => {
  return (
    <header className="sticky top-0 z-50 bg-ivory/95 backdrop-blur supports-[backdrop-filter]:bg-ivory/80 border-b border-gold/20 shadow-warm">
      <div className="container mx-auto px-4 h-18 flex items-center justify-between">
        <div className="flex items-center space-x-10">
          <h1 className="text-3xl font-serif font-bold text-transparent bg-gradient-temple bg-clip-text">
            🪷 Sacred Crafts
          </h1>
          
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#" className="text-burnt-umber hover:text-saffron transition-colors font-medium">
              Sacred Pottery
            </a>
            <a href="#" className="text-burnt-umber hover:text-marigold transition-colors font-medium">
              Blessed Textiles
            </a>
            <a href="#" className="text-burnt-umber hover:text-peacock-blue transition-colors font-medium">
              Temple Arts
            </a>
            <a href="#" className="text-burnt-umber hover:text-lotus-pink transition-colors font-medium">
              Masters
            </a>
          </nav>
        </div>
        
        <div className="flex items-center space-x-3">
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