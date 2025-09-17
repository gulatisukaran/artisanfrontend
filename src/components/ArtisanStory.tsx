import { Badge } from "@/components/ui/badge";
import { MapPin, Award } from "lucide-react";

interface ArtisanStoryProps {
  artisan: {
    name: string;
    image: string;
    location: string;
    specialties: string[];
    experience: string;
    story: string;
    achievements: string[];
  };
}

export const ArtisanStory = ({ artisan }: ArtisanStoryProps) => {
  return (
    <section className="py-12 bg-muted/20">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-muted-foreground">
                <MapPin className="h-4 w-4" />
                <span className="text-sm">{artisan.location}</span>
              </div>
              
              <h1 className="text-4xl md:text-5xl font-bold text-foreground">
                Meet {artisan.name}
              </h1>
              
              <div className="flex flex-wrap gap-2">
                {artisan.specialties.map((specialty) => (
                  <Badge key={specialty} variant="secondary" className="bg-terracotta-light text-warm-brown">
                    {specialty}
                  </Badge>
                ))}
              </div>
              
              <p className="text-lg text-primary font-medium">
                {artisan.experience}
              </p>
            </div>
            
            <div className="prose prose-stone max-w-none">
              <p className="text-muted-foreground leading-relaxed">
                {artisan.story}
              </p>
            </div>
            
            {artisan.achievements.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-foreground">
                  <Award className="h-5 w-5 text-terracotta" />
                  <h3 className="font-semibold">Achievements & Recognition</h3>
                </div>
                <ul className="space-y-2">
                  {artisan.achievements.map((achievement, index) => (
                    <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                      <span className="text-terracotta mt-1">•</span>
                      {achievement}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          
          <div className="relative">
            <div className="aspect-[4/5] rounded-2xl overflow-hidden shadow-artisan">
              <img 
                src={artisan.image} 
                alt={artisan.name}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-gradient-hero rounded-full opacity-20"></div>
            <div className="absolute -top-4 -left-4 w-16 h-16 bg-terracotta-light rounded-full opacity-30"></div>
          </div>
        </div>
      </div>
    </section>
  );
};