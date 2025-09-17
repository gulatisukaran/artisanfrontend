import { useParams, Navigate } from "react-router-dom";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ArtisanStory } from "@/components/ArtisanStory";
import { ArtisanContact } from "@/components/ArtisanContact";
import { ProductCard } from "@/components/ProductCard";
import { getArtisanById } from "@/data/artisans";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

const ArtisanPage = () => {
  const { artisanId } = useParams<{ artisanId: string }>();
  
  if (!artisanId) {
    return <Navigate to="/" replace />;
  }
  
  const artisan = getArtisanById(artisanId);
  
  if (!artisan) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main>
        {/* Breadcrumb Navigation */}
        <section className="py-6 border-b border-border">
          <div className="container mx-auto px-4">
            <Button 
              variant="ghost" 
              onClick={() => window.history.back()}
              className="text-muted-foreground hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Marketplace
            </Button>
          </div>
        </section>

        {/* Artisan Story */}
        <ArtisanStory artisan={artisan} />
        
        {/* Product Catalog */}
        <section className="py-16 bg-background">
          <div className="container mx-auto px-4">
            <div className="text-center space-y-4 mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-foreground">
                {artisan.name}'s Creations
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Explore the handcrafted pieces that showcase years of dedication, 
                skill, and cultural heritage in every detail.
              </p>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {artisan.products.map((product) => (
                <ProductCard 
                  key={product.id} 
                  {...product}
                  artisan={artisan.name}
                />
              ))}
            </div>
            
            {artisan.products.length === 1 && (
              <div className="text-center mt-12">
                <p className="text-muted-foreground mb-4">
                  Looking for something specific? Contact {artisan.name} directly for custom pieces.
                </p>
              </div>
            )}
          </div>
        </section>
        
        {/* Contact Section */}
        <ArtisanContact artisan={artisan} />
      </main>
      
      <Footer />
    </div>
  );
};

export default ArtisanPage;