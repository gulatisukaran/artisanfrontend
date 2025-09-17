import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Heart } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="bg-muted/30 border-t border-border">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-transparent bg-gradient-hero bg-clip-text">
              ArtisanMarket
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Connecting artisans with customers who appreciate handcrafted quality and unique stories.
            </p>
          </div>
          
          <div className="space-y-4">
            <h4 className="font-medium text-foreground">Categories</h4>
            <div className="space-y-2 text-sm">
              <a href="#" className="block text-muted-foreground hover:text-primary transition-colors">
                Pottery & Ceramics
              </a>
              <a href="#" className="block text-muted-foreground hover:text-primary transition-colors">
                Textiles & Weaving
              </a>
              <a href="#" className="block text-muted-foreground hover:text-primary transition-colors">
                Woodworking
              </a>
              <a href="#" className="block text-muted-foreground hover:text-primary transition-colors">
                Leather Goods
              </a>
            </div>
          </div>
          
          <div className="space-y-4">
            <h4 className="font-medium text-foreground">Support</h4>
            <div className="space-y-2 text-sm">
              <a href="#" className="block text-muted-foreground hover:text-primary transition-colors">
                For Artisans
              </a>
              <a href="#" className="block text-muted-foreground hover:text-primary transition-colors">
                For Customers
              </a>
              <a href="#" className="block text-muted-foreground hover:text-primary transition-colors">
                Contact Us
              </a>
              <a href="#" className="block text-muted-foreground hover:text-primary transition-colors">
                Help Center
              </a>
            </div>
          </div>
          
          <div className="space-y-4">
            <h4 className="font-medium text-foreground">Stay Updated</h4>
            <p className="text-sm text-muted-foreground">
              Get notified about new artisans and exclusive pieces.
            </p>
            <div className="space-y-2">
              <Input placeholder="Your email" className="text-sm" />
              <Button size="sm" className="w-full bg-gradient-hero hover:opacity-90">
                Subscribe
              </Button>
            </div>
          </div>
        </div>
        
        <div className="mt-8 pt-8 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground">
            © 2024 ArtisanMarket. Made with <Heart className="inline h-4 w-4 text-terracotta" /> for artisans worldwide.
          </p>
          <div className="flex space-x-6 text-sm">
            <a href="#" className="text-muted-foreground hover:text-primary transition-colors">
              Privacy
            </a>
            <a href="#" className="text-muted-foreground hover:text-primary transition-colors">
              Terms
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};