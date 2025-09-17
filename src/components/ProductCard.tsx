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
      className="group overflow-hidden border-0 bg-card shadow-sm hover:shadow-card-hover transition-all duration-300 hover:scale-105 cursor-pointer"
      onClick={handleCardClick}
    >
      <div className="aspect-square overflow-hidden">
        <img 
          src={image} 
          alt={title}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
        />
      </div>
      <CardContent className="p-4 space-y-2">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <h3 className="font-medium text-foreground line-clamp-2 leading-tight">
              {title}
            </h3>
            <p className="text-sm text-muted-foreground">
              by {artisan}
            </p>
          </div>
          {isNew && (
            <Badge variant="secondary" className="bg-terracotta text-primary-foreground text-xs">
              New
            </Badge>
          )}
        </div>
        <div className="flex items-center justify-between">
          <span className="text-lg font-semibold text-primary">
            ${price}
          </span>
          <Badge variant="outline" className="text-xs border-muted">
            {category}
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
};