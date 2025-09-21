import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { getArtisanByName } from "@/data/artisans";

interface ProductCardProps {
  id: string;
  title: string;
  artisan: string;
  price: number;
  image: string;
  category: string;
  isNew?: boolean;
}

export const ProductCard = ({ 
  title, 
  artisan, 
  price, 
  image, 
  category, 
  isNew = false 
}: ProductCardProps) => {
  const navigate = useNavigate();
  
  const handleCardClick = () => {
    console.log("Product card clicked, artisan:", artisan);
    const artisanData = getArtisanByName(artisan);
    console.log("Found artisan data:", artisanData);
    
    if (artisanData) {
      console.log("Navigating to:", `/artisan/${artisanData.id}`);
      navigate(`/artisan/${artisanData.id}`);
    } else {
      console.error("No artisan data found for:", artisan);
      // Fallback navigation
      if (artisan === "Maria Santos") navigate("/artisan/maria-santos");
      else if (artisan === "David Rodriguez") navigate("/artisan/david-rodriguez");
      else if (artisan === "Elena Vasquez") navigate("/artisan/elena-vasquez");
    }
  };

  return (
    <Card 
      className="group overflow-hidden bg-gradient-card shadow-warm hover:shadow-artisan transition-bounce duration-400 hover:scale-105 cursor-pointer border-gold/20"
      onClick={handleCardClick}
    >
      <div className="aspect-square overflow-hidden relative">
        <img 
          src={image} 
          alt={title}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
        />
        <div className="absolute inset-0 bg-gradient-temple opacity-0 group-hover:opacity-10 transition-opacity duration-300"></div>
      </div>
      <CardContent className="p-5 space-y-3">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <h3 className="font-serif font-semibold text-burnt-umber line-clamp-2 leading-tight group-hover:text-saffron transition-colors">
              {title}
            </h3>
            <p className="text-sm text-sandstone font-medium">
              by {artisan}
            </p>
          </div>
          {isNew && (
            <Badge variant="secondary" className="bg-gradient-sunset text-ivory text-xs font-medium">
              Sacred
            </Badge>
          )}
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xl font-bold text-saffron font-serif">
            ${price}
          </span>
          <Badge variant="outline" className="text-xs border-gold text-burnt-umber bg-saffron-light">
            {category}
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
};