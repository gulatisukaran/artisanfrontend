import { ProductCard } from "./ProductCard";
import { Button } from "@/components/ui/button";
import { artisansData } from "@/data/artisans";

// Get all products from all artisans
const allProducts = artisansData.flatMap(artisan => 
  artisan.products.map(product => ({
    ...product,
    artisan: artisan.name
  }))
);

export const FeaturedProducts = () => {
  return (
    <section className="py-16 bg-background">
      <div className="container mx-auto px-4">
        <div className="text-center space-y-4 mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground">
            Featured Artisan Pieces
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Discover unique, handcrafted items from talented artisans around the world. 
            Each piece tells a story and reflects the passion of its creator.
          </p>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {allProducts.map((product) => (
            <ProductCard key={product.id} {...product} />
          ))}
        </div>
        
        <div className="text-center">
          <Button 
            variant="outline" 
            size="lg"
            className="border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground"
          >
            View All Products
          </Button>
        </div>
      </div>
    </section>
  );
};