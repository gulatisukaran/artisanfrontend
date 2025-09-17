import basketImage from "@/assets/product-basket.jpg";
import journalImage from "@/assets/product-journal.jpg";
import cuttingBoardImage from "@/assets/product-cutting-board.jpg";
import glassVaseImage from "@/assets/product-glass-vase.jpg";
import ceramicMugImage from "@/assets/product-ceramic-mug.jpg";
import heroImage from "@/assets/hero-pottery.jpg";

import mariaImage from "@/assets/artisan-maria.jpg";
import davidImage from "@/assets/artisan-david.jpg";
import elenaImage from "@/assets/artisan-elena.jpg";

export interface Product {
  id: string;
  title: string;
  price: number;
  image: string;
  category: string;
  isNew?: boolean;
  description: string;
}

export interface Artisan {
  id: string;
  name: string;
  image: string;
  location: string;
  specialties: string[];
  experience: string;
  story: string;
  achievements: string[];
  whatsapp: string;
  email: string;
  products: Product[];
}

export const artisansData: Artisan[] = [
  {
    id: "maria-santos",
    name: "Maria Santos",
    image: mariaImage,
    location: "Oaxaca, Mexico",
    specialties: ["Traditional Weaving", "Natural Fibers", "Zapotec Patterns"],
    experience: "Third-generation weaver with 25+ years of experience",
    story: "Maria learned the ancient art of Zapotec weaving from her grandmother at the age of 8. Growing up in the mountains of Oaxaca, she was surrounded by the rich textile traditions of her ancestors. Her hands learned to work with cotton, wool, and natural dyes extracted from cochineal, indigo, and other native plants. Each piece she creates tells a story of her heritage, incorporating traditional patterns that have been passed down through generations. Maria believes that every thread carries the spirit of her people, and through her work, she keeps alive the cultural legacy of the Zapotec civilization. Her textiles are not just decorative items, but vessels of history and identity.",
    achievements: [
      "Featured in the National Museum of Mexican Arts, Chicago",
      "Winner of the UNESCO Prize for Traditional Crafts (2019)",
      "Master Weaver certification from the Oaxacan Cultural Institute",
      "Collaborated with international fashion designers on sustainable collections"
    ],
    whatsapp: "5215551234567",
    email: "maria.santos@artisanmarket.com",
    products: [
      {
        id: "basket-1",
        title: "Handwoven Natural Fiber Basket",
        price: 74,
        image: basketImage,
        category: "Textiles",
        isNew: true,
        description: "A beautiful basket woven with traditional Zapotec patterns using natural palm fibers and cotton. Each basket takes 3-4 days to complete and features intricate geometric designs passed down through generations."
      }
    ]
  },
  {
    id: "david-rodriguez",
    name: "David Rodriguez",
    image: davidImage,
    location: "Guadalajara, Mexico",
    specialties: ["Leather Crafting", "Hand Tooling", "Traditional Techniques"],
    experience: "Master leather artisan with 20+ years perfecting his craft",
    story: "David's journey into leather crafting began when he was 16, working alongside his uncle in a small workshop in Guadalajara's historic district. What started as a summer job became a lifelong passion. He spent years learning traditional Mexican leather working techniques, from selecting the finest hides to hand-tooling intricate patterns inspired by pre-Columbian art. David sources his leather from local tanneries that use traditional, eco-friendly methods, ensuring each piece not only looks beautiful but also supports sustainable practices. His work combines functionality with artistry, creating pieces that age gracefully and tell stories through their wear. Every journal, bag, and accessory he creates is imbued with the warmth and character that only comes from true handcrafted work.",
    achievements: [
      "Master Artisan recognition from the Mexican Leather Workers Guild",
      "Featured in Architectural Digest's 'Modern Mexican Crafts' edition",
      "Supplies leather goods to boutique hotels across Mexico",
      "Teaching workshops on traditional leather techniques"
    ],
    whatsapp: "5215559876543",
    email: "david.rodriguez@artisanmarket.com",
    products: [
      {
        id: "journal-1",
        title: "Embossed Leather Journal",
        price: 54,
        image: journalImage,
        category: "Leather",
        description: "Hand-tooled leather journal featuring traditional Mexican patterns. Made from premium vegetable-tanned leather that develops a beautiful patina over time. Perfect for writers, artists, and dreamers."
      }
    ]
  },
  {
    id: "elena-vasquez",
    name: "Elena Vasquez", 
    image: elenaImage,
    location: "Puebla, Mexico",
    specialties: ["Talavera Pottery", "Ceramic Arts", "Traditional Glazing"],
    experience: "Master ceramicist specializing in authentic Talavera pottery for 30+ years",
    story: "Elena's hands have been shaping clay since she was a child, playing in her father's pottery workshop in Puebla. Born into a family of ceramic artists, she grew up surrounded by the ancient traditions of Talavera pottery, a craft that dates back to the 16th century. Elena spent her youth learning the meticulous 16-step process that creates authentic Talavera pieces - from preparing the special clay mixture to the final firing that brings out the brilliant cobalt blues and warm earth tones. Each piece she creates must meet the strict standards set by the Regulatory Council of Talavera, ensuring authenticity and quality. Her work bridges the gap between traditional techniques and contemporary design, creating pieces that honor the past while speaking to modern sensibilities. For Elena, pottery is meditation, cultural preservation, and artistic expression all rolled into one.",
    achievements: [
      "Certified Master of Talavera by the Regulatory Council of Talavera",
      "Works displayed in the International Museum of Ceramic Art",
      "Featured artisan at the Smithsonian Folklife Festival",
      "Teaches Talavera techniques at the Universidad de las Américas Puebla"
    ],
    whatsapp: "5215554567890",
    email: "elena.vasquez@artisanmarket.com",
    products: [
      {
        id: "pottery-1",
        title: "Artisan Pottery Vase",
        price: 89,
        image: heroImage,
        category: "Pottery",
        isNew: true,
        description: "Authentic Talavera pottery vase featuring hand-painted traditional patterns. Each piece is unique and takes 45 days to complete from clay preparation to final firing. A true work of art for your home."
      },
      {
        id: "mug-1", 
        title: "Ceramic Coffee Mug",
        price: 32,
        image: ceramicMugImage,
        category: "Pottery",
        description: "Handcrafted ceramic mug with a unique glaze that creates beautiful color variations. Perfect for your morning coffee or evening tea. Each mug is wheel-thrown and fired in traditional kilns."
      }
    ]
  }
];

export const getArtisanById = (id: string): Artisan | undefined => {
  return artisansData.find(artisan => artisan.id === id);
};

export const getArtisanByName = (name: string): Artisan | undefined => {
  return artisansData.find(artisan => artisan.name === name);
};