import { ProductCard } from "./ProductCard";
import { Button } from "@/components/ui/button";
import { useEffect, useState, useMemo } from "react";

const API_URL = "https://agentic-fastapi-app-950029052556.europe-west1.run.app/db/all";

export const FeaturedProducts = () => {
  const [artisans, setArtisans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [artisanImages, setArtisanImages] = useState<{ [userId: string]: string }>({});

  useEffect(() => {
    setLoading(true);
    fetch(API_URL)
      .then(res => res.json())
      .then(data => {
        setArtisans(Array.isArray(data.user_profiles) ? data.user_profiles : []);
        setLoading(false);
        // Load images from localStorage for each artisan
        const images: { [userId: string]: string } = {};
        (Array.isArray(data.user_profiles) ? data.user_profiles : []).forEach((artisan: any) => {
          const img = localStorage.getItem(`artisan_image_${artisan.user_id}`);
          if (img) images[artisan.user_id] = img;
        });
        setArtisanImages(images);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="text-center py-8 text-burnt-umber">Loading featured artisans...</div>;
  }

  // Flatten all products from all artisans, adding artisan name to each product
  const allProducts = artisans.flatMap(artisan =>
    Array.isArray(artisan.products)
      ? artisan.products.map((product: any) => ({
          ...product,
          artisan: artisan.name
        }))
      : []
  );

  // Example: show first 3 artisans as featured
  const featured = artisans.slice(0, 3);

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
            onClick={() => window.location.href = '/artisans'}
          >
            View All Products
          </Button>
        </div>

        <div className="text-center py-8">
          <h2 className="text-3xl font-serif font-bold text-center mb-8">Featured Artisans</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {featured.map((artisan) => (
              <div key={artisan.user_id} className="bg-ivory/90 rounded-xl shadow-lg p-6 text-center flex flex-col items-center">
                <div className="w-full flex justify-center mb-4">
                  <div className="w-40 h-40 rounded-2xl bg-sandstone flex items-center justify-center text-5xl font-bold text-burnt-umber overflow-hidden border-4 border-gold shadow-lg">
                    {artisanImages[artisan.user_id] ? (
                      <img
                        src={artisanImages[artisan.user_id]}
                        alt={artisan.name}
                        className="w-full h-full object-cover object-center rounded-2xl"
                      />
                    ) : (
                      artisan.name?.[0] || "?"
                    )}
                  </div>
                </div>
                <div className="text-xl font-semibold text-foreground mb-2">{artisan.name}</div>
                <div className="text-saffron mb-2">{artisan.craft_type}</div>
                <div className="text-sandstone text-sm mb-4 line-clamp-3">{artisan.backstory?.split('Tagline:')[0].trim()}</div>
                <a href={`/artisan/${artisan.user_id}`} className="inline-block mt-2 px-6 py-2 bg-saffron text-burnt-umber font-bold rounded-lg shadow hover:bg-burnt-umber hover:text-ivory transition-all">View Profile</a>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};