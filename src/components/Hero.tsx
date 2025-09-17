import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import heroImage from "@/assets/hero-pottery.jpg";

export const Hero = () => {
  return (
    <section className="relative min-h-[60vh] flex items-center justify-center overflow-hidden">
      <div className="absolute inset-0 bg-gradient-hero opacity-10"></div>
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-20"
        style={{ backgroundImage: `url(${heroImage})` }}
      ></div>
      
      <div className="relative z-10 container mx-auto px-4 text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-6xl font-bold text-foreground leading-tight">
            Discover
            <span className="text-transparent bg-gradient-hero bg-clip-text ml-3">
              Artisan
            </span>
            <br />
            Crafted Stories
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Connect with local artisans and discover unique, handcrafted pieces that tell a story. 
            Each item is lovingly made by skilled hands and carries the heritage of its creator.
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input 
              placeholder="Search artisans, crafts..." 
              className="pl-10 h-12 border-2 focus:border-primary"
            />
          </div>
          <Button size="lg" className="h-12 px-8 bg-gradient-hero hover:opacity-90 transition-opacity">
            Explore
          </Button>
        </div>
        
        {/* Test Link - Hardcoded Artisan */}
        <div className="text-center">
          <a 
            href="/artisan/maria-santos" 
            className="inline-block px-6 py-3 bg-terracotta text-primary-foreground rounded-lg hover:opacity-90 transition-opacity"
          >
            Test: View Maria Santos (Potter)
          </a>
        </div>
        
        <div className="flex flex-wrap justify-center gap-6 text-sm text-muted-foreground">
          <span>🏺 Pottery</span>
          <span>🧺 Textiles</span>
          <span>📖 Leather Goods</span>
          <span>🪵 Woodwork</span>
          <span>🔥 Glasswork</span>
        </div>
      </div>
    </section>
  );
};