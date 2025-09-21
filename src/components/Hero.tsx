import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import { Link } from "react-router-dom";
import heroImage from "@/assets/hero-pottery.jpg";

export const Hero = () => {
  return (
    <section className="relative min-h-[70vh] flex items-center justify-center overflow-hidden pattern-lotus">
      <div className="absolute inset-0 bg-gradient-temple opacity-15"></div>
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-25"
        style={{ backgroundImage: `url(${heroImage})` }}
      ></div>
      <div className="absolute inset-0 bg-gradient-sunset opacity-5"></div>
      
      <div className="relative z-10 container mx-auto px-4 text-center space-y-10">
        <div className="space-y-6">
          <h1 className="text-5xl md:text-7xl font-serif font-bold text-foreground leading-tight">
            Discover
            <span className="text-transparent bg-gradient-temple bg-clip-text ml-4 block md:inline">
              Sacred Crafts
            </span>
            <br />
            <span className="text-3xl md:text-5xl text-saffron">& Ancient Stories</span>
          </h1>
          <p className="text-lg md:text-xl text-burnt-umber max-w-3xl mx-auto leading-relaxed font-medium">
            Journey through generations of traditional craftsmanship. Every piece carries the soul of ancient 
            techniques, passed down through sacred lineages of master artisans who honor their heritage.
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 max-w-lg mx-auto">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-saffron h-5 w-5" />
            <Input 
              placeholder="Search sacred crafts, masters..." 
              className="pl-12 h-14 border-2 border-gold/30 focus:border-saffron bg-ivory/80 backdrop-blur-sm rounded-xl text-burnt-umber placeholder:text-sandstone"
            />
          </div>
          <Button size="lg" className="h-14 px-10 bg-gradient-temple hover:scale-105 transition-bounce text-ivory font-semibold rounded-xl shadow-warm">
            Begin Journey
          </Button>
        </div>
        
        {/* Test Link - Hardcoded Artisan */}
        <div className="text-center">
          <Link 
            to="/artisans" 
            className="inline-block px-8 py-4 bg-gradient-sunset text-ivory rounded-xl hover:scale-105 transition-bounce shadow-artisan font-semibold"
          >
            Browse Artisans
          </Link>
        </div>
      </div>
    </section>
  );
};