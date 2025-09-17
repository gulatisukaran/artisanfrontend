import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { MessageCircle, Phone, Mail, MapPin } from "lucide-react";

interface ArtisanContactProps {
  artisan: {
    name: string;
    whatsapp: string;
    email: string;
    location: string;
  };
}

export const ArtisanContact = ({ artisan }: ArtisanContactProps) => {
  const whatsappMessage = encodeURIComponent(
    `Hi ${artisan.name}! I'm interested in your handcrafted pieces from ArtisanMarket. Could you tell me more about your available items?`
  );
  
  const whatsappUrl = `https://wa.me/${artisan.whatsapp}?text=${whatsappMessage}`;

  return (
    <section className="py-16 bg-background">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center space-y-4 mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground">
              Connect with {artisan.name}
            </h2>
            <p className="text-lg text-muted-foreground">
              Ready to commission a piece or learn more about their craft? Get in touch directly.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <Card className="border-2 border-terracotta/20 shadow-card-hover">
              <CardContent className="p-8 text-center space-y-6">
                <div className="w-16 h-16 mx-auto bg-gradient-hero rounded-full flex items-center justify-center">
                  <MessageCircle className="h-8 w-8 text-primary-foreground" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-semibold text-foreground">
                    WhatsApp Chat
                  </h3>
                  <p className="text-muted-foreground">
                    Start a conversation and discuss your custom piece directly
                  </p>
                </div>
                <Button 
                  size="lg" 
                  className="w-full bg-gradient-hero hover:opacity-90 transition-opacity"
                  onClick={() => window.open(whatsappUrl, '_blank')}
                >
                  <MessageCircle className="h-5 w-5 mr-2" />
                  Chat on WhatsApp
                </Button>
              </CardContent>
            </Card>
            
            <Card className="border border-border">
              <CardContent className="p-8 space-y-6">
                <h3 className="text-xl font-semibold text-foreground">
                  Other Ways to Connect
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <Phone className="h-5 w-5 text-terracotta" />
                    <div>
                      <p className="font-medium text-foreground">Phone</p>
                      <p className="text-sm text-muted-foreground">+{artisan.whatsapp}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <Mail className="h-5 w-5 text-terracotta" />
                    <div>
                      <p className="font-medium text-foreground">Email</p>
                      <p className="text-sm text-muted-foreground">{artisan.email}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <MapPin className="h-5 w-5 text-terracotta" />
                    <div>
                      <p className="font-medium text-foreground">Location</p>
                      <p className="text-sm text-muted-foreground">{artisan.location}</p>
                    </div>
                  </div>
                </div>
                
                <div className="pt-4 border-t border-border">
                  <p className="text-xs text-muted-foreground">
                    Response time: Usually within 2-4 hours during business days
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};