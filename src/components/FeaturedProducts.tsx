import { ProductCard } from "./ProductCard";
import { Button } from "@/components/ui/button";

import basketImage from "@/assets/product-basket.jpg";
import journalImage from "@/assets/product-journal.jpg";
import cuttingBoardImage from "@/assets/product-cutting-board.jpg";
import glassVaseImage from "@/assets/product-glass-vase.jpg";
import ceramicMugImage from "@/assets/product-ceramic-mug.jpg";
import heroImage from "@/assets/hero-pottery.jpg";

const mockProducts = [
  {
    id: "1",
    title: "Handwoven Natural Fiber Basket",
    artisan: "Maria Santos",
    price: 74,
    image: basketImage,
    category: "Textiles",
    isNew: true,
  },
  {
    id: "2", 
    title: "Embossed Leather Journal",
    artisan: "David Rodriguez",
    price: 54,
    image: journalImage,
    category: "Leather",
  },
  {
    id: "3",
    title: "Artisan Pottery Vase",
    artisan: "Elena Vasquez",
    price: 89,
    image: heroImage,
    category: "Pottery",
    isNew: true,
  },
  {
    id: "4",
    title: "Olive Wood Cutting Board",
    artisan: "Giuseppe Romano",
    price: 65,
    image: cuttingBoardImage,
    category: "Woodwork",
  },
  {
    id: "5",
    title: "Hand-blown Glass Vase",
    artisan: "Claire Dubois",
    price: 125,
    image: glassVaseImage,
    category: "Glasswork",
  },
  {
    id: "6",
    title: "Ceramic Coffee Mug",
    artisan: "Yuki Tanaka",
    price: 32,
    image: ceramicMugImage,
    category: "Pottery",
  },
];

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
          {mockProducts.map((product) => (
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