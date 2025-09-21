import { useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MapPin, Star, MessageCircle, Mail } from "lucide-react";

const API_URL = "https://agentic-fastapi-app-950029052556.europe-west1.run.app/db/all";

const ArtisansPage = () => {
  const [searchParams] = useSearchParams();
  const category = searchParams.get('category');
  const [artisans, setArtisans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(API_URL)
      .then(res => res.json())
      .then(data => {
        // The API returns { user_profiles: [...] }
        setArtisans(Array.isArray(data.user_profiles) ? data.user_profiles : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  // Filter artisans based on category if provided
  const filteredArtisans = category 
    ? artisans.filter(artisan =>
        (typeof artisan.craft_type === 'string' && artisan.craft_type.toLowerCase().includes(category.toLowerCase())) ||
        (Array.isArray(artisan.materials) && artisan.materials.some((mat: string) => mat.toLowerCase().includes(category.toLowerCase())))
      )
    : artisans;

  const getCategoryTitle = (category: string | null) => {
    if (!category) return "All Artisans";
    const categoryMap: { [key: string]: string } = {
      'pottery': 'Sacred Pottery Masters',
      'textiles': 'Blessed Textile Artisans', 
      'beads': 'Prayer Bead Craftsmen',
      'woodwork': 'Temple Woodwork Masters',
      'golden': 'Golden Craft Artisans'
    };
    return categoryMap[category.toLowerCase()] || `${category} Artisans`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-ivory to-cream">
      <Header />
      <main className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-serif font-bold text-foreground mb-4">
            {getCategoryTitle(category)}
          </h1>
          <p className="text-lg text-burnt-umber max-w-2xl mx-auto">
            Discover master artisans who preserve ancient traditions through their sacred crafts.
            {category && ` Explore our collection of ${category} specialists.`}
          </p>
          {category && (
            <div className="mt-6">
              <Badge variant="secondary" className="text-saffron bg-gold/20 border-gold">
                {filteredArtisans.length} {filteredArtisans.length === 1 ? 'Artisan' : 'Artisans'} Found
              </Badge>
            </div>
          )}
        </div>

        {loading ? (
          <div className="text-center py-12 text-burnt-umber text-xl">Loading artisans...</div>
        ) : filteredArtisans.length === 0 ? (
          <div className="text-center py-12">
            <h3 className="text-2xl font-semibold text-burnt-umber mb-4">
              No artisans found for "{category}"
            </h3>
            <p className="text-sandstone mb-6">
              We're constantly adding new master craftspeople to our platform.
            </p>
            <Button 
              onClick={() => window.history.back()} 
              className="bg-gradient-temple text-ivory"
            >
              Go Back
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredArtisans.map((artisan) => (
              <Card 
                key={artisan.user_id} 
                className="group hover:shadow-artisan transition-all duration-300 hover:-translate-y-2 border-gold/20 bg-ivory/80 backdrop-blur-sm"
              >
                <CardHeader className="p-0">
                  <div className="relative overflow-hidden rounded-t-lg">
                    {/* No image in API, so use a placeholder or initials */}
                    <div className="w-full h-64 flex items-center justify-center bg-sandstone text-5xl font-bold text-burnt-umber">
                      {artisan.name?.[0] || "?"}
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="p-6">
                  <CardTitle className="text-xl font-serif text-foreground mb-2">
                    {artisan.name}
                  </CardTitle>
                  
                  <div className="flex items-center text-burnt-umber mb-3">
                    <MapPin className="h-4 w-4 mr-1 text-saffron" />
                    <span className="text-sm">{artisan.state}</span>
                  </div>
                  
                  <p className="text-sm text-sandstone mb-4 line-clamp-3">
                    {artisan.backstory}
                  </p>
                  
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold text-burnt-umber mb-2">Specialties:</h4>
                    <div className="flex flex-wrap gap-1">
                      {artisan.craft_type && (
                        <Badge 
                          variant="outline" 
                          className="text-xs text-saffron border-saffron/30"
                        >
                          {artisan.craft_type}
                        </Badge>
                      )}
                      {artisan.materials && typeof artisan.materials === 'string' && (
                        <Badge variant="outline" className="text-xs text-sandstone border-sandstone/30">
                          {artisan.materials}
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center text-sm text-burnt-umber">
                      <Star className="h-4 w-4 text-gold mr-1 fill-current" />
                      <span>{artisan.years_experience || "-"} yrs experience</span>
                    </div>
                    <span className="text-sm text-saffron font-medium">
                      {artisan.price_range
                        ? artisan.price_range.replace(/Rs\s?/gi, "₹ ")
                        : "-"}
                    </span>
                  </div>
                  
                  <div className="flex gap-2">
                    <Button 
                      size="sm" 
                      className="flex-1 bg-gradient-temple text-ivory hover:scale-105 transition-transform"
                      // onClick={() => window.location.href = `/artisan/${artisan.user_id}`}
                      disabled
                    >
                      View Profile
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
        
        {filteredArtisans.length > 0 && !loading && (
          <div className="text-center mt-12">
            <p className="text-burnt-umber mb-4">
              Can't find what you're looking for?
            </p>
            <Button variant="outline" className="border-saffron text-saffron hover:bg-saffron/10">
              Request Custom Craft
            </Button>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
};

export default ArtisansPage;
