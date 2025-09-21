import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Badge } from "@/components/ui/badge";
import { MapPin, Star } from "lucide-react";

const bgImages = [
  '/artisan-bg-1.jpg',
  '/artisan-bg-2.jpg',
  '/artisan-bg-3.jpg',
  '/artisan-bg-4.jpg',
];

const ArtisanProfilePage = () => {
  const { artisanId } = useParams<{ artisanId: string }>();
  const [artisan, setArtisan] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [artisanImage, setArtisanImage] = useState<string | null>(null);
  const [galleryImages, setGalleryImages] = useState<string[]>([]);
  // Pick a random background for visual variety
  const bgImage = bgImages[(artisanId?.charCodeAt(0) || 0) % bgImages.length];

  useEffect(() => {
    if (!artisanId) return;
    setLoading(true);
    fetch(`https://agentic-fastapi-app-950029052556.europe-west1.run.app/user/${artisanId}/profile`)
      .then(res => res.json())
      .then(data => {
        if (data) setArtisan(data);
        else setArtisan(null);
        setLoading(false);
      })
      .catch(() => setLoading(false));
    // Fetch all product images for this artisan from the media API
    fetch(`https://agentic-fastapi-app-950029052556.europe-west1.run.app/user/${artisanId}/media`)
      .then(res => res.json())
      .then(media => {
        const images: string[] = [];
        if (media.items && media.items.length > 0) {
          media.items.forEach((item: any, idx: number) => {
            if (item.edited_image_base64) {
              const imgData = `data:image/png;base64,${item.edited_image_base64}`;
              images.push(imgData);
              // Store in localStorage for reuse elsewhere
              localStorage.setItem(`artisan_gallery_${artisanId}_${idx}`, imgData);
            }
          });
        }
        setGalleryImages(images);
      });
    // Get main profile image from localStorage
    const img = localStorage.getItem(`artisan_image_${artisanId}`);
    setArtisanImage(img);
  }, [artisanId]);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-xl text-burnt-umber">Loading artisan profile...</div>;
  }
  if (!artisan) {
    return <div className="min-h-screen flex items-center justify-center text-xl text-burnt-umber">Artisan not found.</div>;
  }

  // Extract tagline if present
  let tagline = "";
  if (artisan.backstory && artisan.backstory.includes("Tagline:")) {
    tagline = artisan.backstory.split("Tagline:")[1].trim();
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-ivory to-cream flex flex-col">
      <Header />
      {/* Hero Section */}
      <section className="relative min-h-[50vh] flex items-center justify-center overflow-hidden pattern-lotus">
        <div className="absolute inset-0 bg-gradient-temple opacity-20"></div>
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-30"
          style={{ backgroundImage: `url(${bgImage})` }}
        ></div>
        <div className="relative z-10 w-full max-w-3xl mx-auto px-4 py-16 text-center space-y-6">
          <div className="flex justify-center">
            {artisanImage ? (
              <img
                src={artisanImage}
                alt={artisan.name}
                className="w-32 h-32 rounded-full object-cover border-4 border-gold shadow-lg"
              />
            ) : (
              <div className="w-32 h-32 rounded-full bg-sandstone flex items-center justify-center text-6xl font-bold text-burnt-umber border-4 border-gold shadow-lg">
                {artisan.name?.[0] || "?"}
              </div>
            )}
          </div>
          <h1 className="text-4xl md:text-6xl font-serif font-bold text-foreground leading-tight">
            {artisan.name}
          </h1>
          {tagline && (
            <div className="text-xl md:text-2xl text-marigold font-semibold italic">{tagline}</div>
          )}
          <div className="flex flex-wrap justify-center gap-4 mt-4">
            <Badge variant="outline" className="text-base text-saffron border-saffron/30">
              {artisan.craft_type}
            </Badge>
            <Badge variant="outline" className="text-base text-sandstone border-sandstone/30">
              {artisan.materials}
            </Badge>
            <span className="flex items-center gap-2 text-base text-burnt-umber">
              <MapPin className="h-5 w-5 text-saffron" />
              {artisan.state}
            </span>
            <span className="flex items-center gap-2 text-base text-burnt-umber">
              <Star className="h-5 w-5 text-gold fill-current" />
              {artisan.years_experience || "-"} yrs experience
            </span>
            <span className="text-base text-saffron font-medium">
              {artisan.price_range ? (isNaN(Number(artisan.price_range)) ? artisan.price_range.replace(/Rs\s?/gi, "₹ ") : `₹ ${artisan.price_range}`) : "-"}
            </span>
          </div>
        </div>
      </section>
      {/* Info Section */}
      <main className="flex-1 container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto bg-ivory/95 rounded-2xl shadow-lg p-8 mb-12">
          <h2 className="text-2xl font-serif font-bold text-foreground mb-6">About {artisan.name}</h2>
          <div className="mb-6">
            <h4 className="text-lg font-semibold text-burnt-umber mb-2">Backstory</h4>
            <p className="text-base text-sandstone whitespace-pre-line">
              {artisan.backstory?.split("Tagline:")[0].trim()}
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-lg font-semibold text-burnt-umber mb-2">Languages</h4>
              <span className="text-base text-saffron">{artisan.languages || "-"}</span>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-burnt-umber mb-2">Brand Style</h4>
              <span className="text-base text-saffron">{artisan.brand_style || "-"}</span>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-burnt-umber mb-2">Sales Channels</h4>
              <span className="text-base text-saffron">{artisan.sales_channels || "-"}</span>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-burnt-umber mb-2">Price Range</h4>
              <span className="text-base text-saffron">{artisan.price_range ? (isNaN(Number(artisan.price_range)) ? artisan.price_range.replace(/Rs\s?/gi, "₹ ") : `₹ ${artisan.price_range}`) : "-"}</span>
            </div>
          </div>
        </div>
        {/* Gallery Section */}
        {galleryImages.length > 0 && (
          <div className="max-w-4xl mx-auto mb-12">
            <h3 className="text-2xl font-bold text-foreground mb-6">Artisan's Product Gallery</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
              {galleryImages.map((img, idx) => (
                <div key={idx} className="bg-ivory rounded-xl shadow p-4 flex flex-col items-center">
                  <img src={img} alt={`Artisan product ${idx + 1}`} className="w-full h-64 object-cover rounded-lg mb-2" />
                  <span className="text-sm text-sandstone">Product {idx + 1}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
};

export default ArtisanProfilePage;
