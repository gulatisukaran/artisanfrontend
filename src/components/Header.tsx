import { Button } from "@/components/ui/button";
import { Heart, ShoppingBag, User } from "lucide-react";

export const Header = () => {
  return (
    <header className="sticky top-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <h1 className="text-2xl font-bold text-transparent bg-gradient-hero bg-clip-text">
            ArtisanMarket
          </h1>
          
          <nav className="hidden md:flex items-center space-x-6">
            <a href="#" className="text-foreground hover:text-primary transition-colors">
              Pottery
            </a>
            <a href="#" className="text-foreground hover:text-primary transition-colors">
              Textiles
            </a>
            <a href="#" className="text-foreground hover:text-primary transition-colors">
              Woodwork
            </a>
            <a href="#" className="text-foreground hover:text-primary transition-colors">
              Artisans
            </a>
          </nav>
        </div>
        
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" className="hidden sm:flex">
            <Heart className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon">
            <ShoppingBag className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon">
            <User className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
};