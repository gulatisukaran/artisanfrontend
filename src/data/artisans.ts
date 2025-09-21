import basketImage from "@/assets/product-basket.jpg";
import journalImage from "@/assets/product-journal.jpg";
import cuttingBoardImage from "@/assets/product-cutting-board.jpg";
import glassVaseImage from "@/assets/product-glass-vase.jpg";
import ceramicMugImage from "@/assets/product-ceramic-mug.jpg";
import heroImage from "@/assets/hero-pottery.jpg";

import raviImage from "@/assets/artisan-maria.jpg"; // Will represent Ravi Kumar
import priyankaImage from "@/assets/artisan-david.jpg"; // Will represent Priyanka Sharma
import rameshImage from "@/assets/artisan-elena.jpg"; // Will represent Ramesh Vishwakarma

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
    id: "ravi-kumar",
    name: "Ravi Kumar",
    image: raviImage,
    location: "Jaipur, Rajasthan",
    specialties: ["Block Printing", "Natural Dyes", "Sanganeri Patterns"],
    experience: "Fourth-generation textile artisan with 30+ years of experience",
    story: "Ravi Kumar ji belongs to the ancient lineage of master block printers from Sanganer, near Jaipur. His great-grandfather started this sacred craft in 1920, and since then, four generations have devoted their lives to preserving the traditional art of hand block printing. Ravi ji learned the intricate patterns and natural dyeing techniques from his father at the tender age of 12. Each wooden block he carves tells a story - from the delicate lotus motifs to the geometric patterns inspired by Mughal architecture. He uses only natural dyes made from turmeric, indigo, madder root, and pomegranate rind, keeping the ancient tradition alive. His workshop employs 15 local artisans, and he takes pride in training young craftsmen to ensure this sacred art doesn't disappear. For Ravi ji, every print is a prayer, every pattern a piece of heritage.",
    achievements: [
      "National Award for Excellence in Handloom & Handicrafts (2020)",
      "Featured in UNESCO's Living Heritage Artisans of India",
      "Sahitya Kala Parishad Delhi recognition for cultural preservation",
      "Supplies to leading fashion houses in Mumbai and Delhi"
    ],
    whatsapp: "+91-9876543210",
    email: "ravi.kumar@sacredcrafts.in",
    products: [
      {
        id: "textile-1",
        title: "Hand Block Printed Cotton Dupatta",
        price: 2800,
        image: basketImage,
        category: "textiles",
        isNew: true,
        description: "Exquisite hand block printed cotton dupatta featuring traditional Sanganeri patterns. Made with natural dyes and taking 7 days to complete, each piece showcases the intricate artistry passed down through generations."
      }
    ]
  },
  {
    id: "priyanka-sharma",
    name: "Priyanka Sharma",
    image: priyankaImage,
    location: "Varanasi, Uttar Pradesh",
    specialties: ["Banarasi Weaving", "Silk Textiles", "Zardozi Embroidery"],
    experience: "Master weaver specializing in authentic Banarasi silk sarees for 25+ years",
    story: "Priyanka Sharma ji comes from a family of traditional Banarasi weavers in the holy city of Varanasi. Her journey began when she was just 14, learning the sacred art of silk weaving from her mother-in-law, a renowned master weaver. The ancient wooden handlooms in her workshop have been weaving magic for over 80 years, creating the finest Banarasi silk sarees adorned with intricate gold and silver zari work. Each saree takes 3-6 months to complete, with patterns inspired by Mughal motifs, flora and fauna, and geometric designs. Priyanka ji has mastered the difficult art of 'kadhua' technique, where each motif is woven separately, making it reversible. She believes that every thread carries the blessings of Ma Ganga and the spiritual energy of Kashi. Her workshop supports 20 families, preserving not just the craft but the livelihood of the weaving community.",
    achievements: [
      "Padma Shri recommendation for contribution to handloom industry",
      "Featured weaver at India International Trade Fair for 5 consecutive years",
      "Recognized by Ministry of Textiles as Master Craftsperson",
      "Her sarees are worn by celebrities at Cannes Film Festival"
    ],
    whatsapp: "+91-9123456789",
    email: "priyanka.sharma@sacredcrafts.in",
    products: [
      {
        id: "journal-1",
        title: "Handwoven Silk Diary Cover",
        price: 3200,
        image: journalImage,
        category: "textiles",
        description: "Luxurious silk diary cover woven with traditional Banarasi patterns and gold zari work. Each cover is handwoven on traditional pit looms, taking 15 days to complete. Perfect for preserving your precious thoughts and memories."
      }
    ]
  },
  {
    id: "ramesh-vishwakarma",
    name: "Ramesh Vishwakarma", 
    image: rameshImage,
    location: "Khurja, Uttar Pradesh",
    specialties: ["Blue Pottery", "Ceramic Arts", "Traditional Glazing"],
    experience: "Master potter specializing in authentic Khurja pottery for 35+ years",
    story: "Ramesh Vishwakarma ji belongs to the revered Vishwakarma community, considered the divine architects and craftsmen in Hindu tradition. Born in Khurja, the pottery capital of India, he learned the sacred art of clay molding from his grandfather at age 10. His hands have shaped thousands of pieces - from delicate tea sets to magnificent decorative vases. Ramesh ji has mastered the ancient technique of blue pottery, originally brought to India by Persian artisans and perfected over centuries. Each piece goes through multiple firings at temperatures reaching 1000°C, and the distinctive blue and white patterns are hand-painted using cobalt oxide. His workshop follows traditional methods - the clay is prepared using a 500-year-old recipe, and natural glazes create the lustrous finish. For Ramesh ji, pottery is meditation, and every vessel he creates carries the divine energy of Vishwakarma, the celestial architect.",
    achievements: [
      "National Award for Master Craftsperson by Government of India",
      "Featured in National Geographic's 'Artisans of India' documentary",
      "Pottery displayed in National Crafts Museum, New Delhi",
      "Teaching traditional techniques at National Institute of Design, Ahmedabad"
    ],
    whatsapp: "+91-9876512345",
    email: "ramesh.vishwakarma@sacredcrafts.in",
    products: [
      {
        id: "pottery-1",
        title: "Traditional Blue Pottery Vase",
        price: 4500,
        image: heroImage,
        category: "pottery",
        isNew: true,
        description: "Authentic Khurja blue pottery vase featuring hand-painted traditional patterns. Each piece is thrown on the potter's wheel and fired in traditional kilns. Takes 21 days from clay preparation to final glazing. A masterpiece of Indian ceramic art."
      },
      {
        id: "mug-1", 
        title: "Handcrafted Ceramic Kulhad Set",
        price: 800,
        image: ceramicMugImage,
        category: "pottery",
        description: "Set of 4 traditional ceramic kulhads (clay cups) perfect for serving tea or lassi. Each kulhad is hand-thrown and fired using traditional methods. Eco-friendly and adds authentic flavor to your beverages."
      }
    ]
  },
  {
    id: "lakshmi-devi",
    name: "Lakshmi Devi",
    image: raviImage, // Reusing available image
    location: "Channapatna, Karnataka",
    specialties: ["Wooden Toys", "Lacquer Work", "Traditional Turning"],
    experience: "Master craftsperson in Channapatna toys with 28+ years experience",
    story: "Lakshmi Devi belongs to the artisan families of Channapatna, known worldwide for their colorful wooden toys. She learned the craft from her husband's family when she got married at 19. The ancient art of lacquer toy making involves turning wood on traditional lathes and applying natural lac colors. Each toy is not just a plaything but carries the blessing of craftsmanship passed down for over 200 years. Lakshmi ji's nimble fingers can transform a simple piece of hale wood into beautiful dolls, animals, and rattles that delight children across the world. She uses only natural dyes and vegetable colors, ensuring the toys are completely safe for children. Her workshop provides employment to 12 women from the village, empowering them through this traditional craft.",
    achievements: [
      "Geographical Indication (GI) tag holder for Channapatna toys",
      "Featured in Prime Minister's 'Mann Ki Baat' radio program",
      "Export quality certification for toy manufacturing",
      "Training instructor at District Industries Centre"
    ],
    whatsapp: "+91-9845123456",
    email: "lakshmi.devi@sacredcrafts.in",
    products: [
      {
        id: "woodwork-1",
        title: "Traditional Wooden Toy Set",
        price: 1200,
        image: cuttingBoardImage,
        category: "woodwork",
        description: "Set of 6 handcrafted wooden toys including elephant, horse, and spinning top. Made from sustainable hale wood and colored with natural lac. Each toy is turned on traditional lathes and finished by hand."
      }
    ]
  },
  {
    id: "mohammed-ali",
    name: "Mohammed Ali Ustad",
    image: priyankaImage, // Reusing available image
    location: "Lucknow, Uttar Pradesh",
    specialties: ["Chikankari Embroidery", "Hand Stitching", "Traditional Patterns"],
    experience: "Master craftsman in Lucknowi Chikankari with 40+ years of expertise",
    story: "Mohammed Ali Ustad ji is a master of the delicate art of Chikankari, the traditional hand embroidery of Lucknow. This exquisite craft, believed to have been introduced by Noor Jahan, the wife of Mughal Emperor Jahangir, requires extraordinary skill and patience. Ustad ji learned this art from his father, who was court embroiderer to the Nawabs of Awadh. His fingers dance across fine muslin and cotton fabrics, creating intricate patterns of flowers, paisleys, and geometric designs using white thread on white fabric. Each garment takes weeks to complete, with some pieces requiring up to 6 months of meticulous handwork. The 36 different stitches of Chikankari are like a language to him, each telling its own story. Ustad ji has trained over 200 women in his locality, preserving this dying art and providing sustainable livelihoods.",
    achievements: [
      "National Award for Master Craftsperson in Embroidery",
      "Padma Shri recommendation for cultural preservation",
      "Featured artisan in 'Incredible India' campaign",
      "Supplies to leading fashion designers across India and abroad"
    ],
    whatsapp: "+91-9415123456",
    email: "mohammed.ali@sacredcrafts.in",
    products: [
      {
        id: "textile-2",
        title: "Chikankari Embroidered Kurta",
        price: 4800,
        image: basketImage,
        category: "textiles",
        isNew: true,
        description: "Exquisite hand-embroidered Chikankari kurta featuring traditional Lucknowi patterns. Each piece takes 45 days to complete with intricate shadow work and French knots. Made from premium cotton voile."
      }
    ]
  },
  {
    id: "ganga-devi",
    name: "Ganga Devi",
    image: rameshImage, // Reusing available image
    location: "Kutch, Gujarat",
    specialties: ["Mirror Work", "Kutchi Embroidery", "Traditional Stitching"],
    experience: "Master embroidery artist specializing in Kutch work for 32+ years",
    story: "Ganga Devi belongs to the Ahir community of Kutch, renowned for their exquisite mirror work embroidery. She learned this ancient craft from her mother-in-law, who taught her the 16 different types of stitches used in traditional Kutchi embroidery. Each piece of her work tells the story of the desert - camels, peacocks, elephants, and geometric patterns inspired by the mud architecture of traditional homes. The tiny mirrors (called 'abhla') are stitched by hand using silk threads in vibrant colors - magenta, orange, yellow, and green. Her work survived the devastating earthquake of 2001, and she played a crucial role in reviving the craft in her village. Ganga Devi believes that every stitch is a prayer to the divine, and the mirrors reflect not just light but the soul of the artisan.",
    achievements: [
      "UNESCO Award of Excellence for Handicrafts",
      "Featured in Smithsonian's Festival of India",
      "Master trainer for Government of Gujarat's skill development program",
      "Her work is displayed in Victoria and Albert Museum, London"
    ],
    whatsapp: "+91-9898123456",
    email: "ganga.devi@sacredcrafts.in",
    products: [
      {
        id: "textile-3",
        title: "Kutch Mirror Work Bag",
        price: 2200,
        image: glassVaseImage,
        category: "textiles",
        description: "Traditional Kutchi bag featuring intricate mirror work and colorful embroidery. Each bag takes 20 days to complete with hand-stitched mirrors and traditional motifs. Perfect blend of utility and artistry."
      }
    ]
  },
  {
    id: "suresh-soni",
    name: "Suresh Soni",
    image: raviImage, // Reusing available image
    location: "Jaipur, Rajasthan",
    specialties: ["Kundan Jewelry", "Gold Work", "Precious Stone Setting"],
    experience: "Master jeweler in traditional Kundan work with 38+ years experience",
    story: "Suresh Soni ji belongs to the legendary Soni community of Jaipur, the traditional goldsmiths who have been crafting exquisite jewelry for Maharajas for centuries. His ancestors were court jewelers to the rulers of Amber and Jaipur. The art of Kundan, where uncut diamonds and precious stones are set in pure gold using ancient techniques, requires extraordinary precision and years of training. Suresh ji learned this sacred craft from his grandfather, who taught him that working with gold is not just a profession but a divine calling. Each piece he creates involves 8-12 artisans working for weeks - from the goldsmith who shapes the base to the meenakari artist who adds colorful enamel work on the reverse. His workshop follows traditional methods passed down for over 400 years, and every piece carries the royal heritage of Rajasthan.",
    achievements: [
      "Heritage Craftsman Award by Rajasthan Government",
      "Featured in National Geographic's 'Treasures of India'",
      "Supplies jewelry to leading Bollywood productions",
      "Master trainer at Rajasthan Institute of Gems and Jewelry"
    ],
    whatsapp: "+91-9829123456",
    email: "suresh.soni@sacredcrafts.in",
    products: [
      {
        id: "jewelry-1",
        title: "Traditional Kundan Earrings",
        price: 8500,
        image: ceramicMugImage,
        category: "golden",
        isNew: true,
        description: "Exquisite Kundan earrings featuring uncut diamonds set in 22k gold with traditional meenakari work. Each pair takes 30 days to complete using age-old techniques. A piece of royal Rajasthani heritage."
      }
    ]
  },
  {
    id: "ashok-kumar",
    name: "Ashok Kumar",
    image: priyankaImage, // Reusing available image
    location: "Varanasi, Uttar Pradesh", 
    specialties: ["Rudraksha Beads", "Prayer Malas", "Sacred Jewelry"],
    experience: "Master craftsman in sacred bead making for 26+ years",
    story: "Ashok Kumar ji has devoted his life to the sacred art of creating prayer beads and Rudraksha malas in the holy city of Varanasi. His family has been serving pilgrims and devotees for three generations, creating authentic spiritual jewelry that carries divine vibrations. Each Rudraksha bead is carefully selected from the sacred trees of Nepal and Indonesia, tested for authenticity, and blessed in the temples of Kashi Vishwanath. Ashok ji knows the ancient science of Rudraksha - each bead with different mukhi (faces) carries specific spiritual powers. His hands string together not just beads, but prayers and blessings. Every mala is completed with a Gauri Shankar bead and energized through Vedic mantras. His workshop near the ghats of Ganga serves spiritual seekers from around the world, providing authentic prayer beads that aid in meditation and spiritual practice.",
    achievements: [
      "Certified authentic Rudraksha dealer by Rudraksha Research Centre",
      "Featured in 'Spiritual India' documentary series",
      "Supplies to major ashrams and spiritual organizations across India",
      "Expert consultant for archaeological Rudraksha findings"
    ],
    whatsapp: "+91-9335123456",
    email: "ashok.kumar@sacredcrafts.in",
    products: [
      {
        id: "beads-1",
        title: "108 Bead Rudraksha Mala",
        price: 3500,
        image: basketImage,
        category: "beads",
        description: "Authentic 108-bead Rudraksha mala made from 5-mukhi Rudraksha beads. Each bead is individually tested for authenticity and energized with Vedic mantras. Complete with silver capping and comfortable cotton thread."
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