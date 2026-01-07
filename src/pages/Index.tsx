import { useState } from "react";
import { motion } from "framer-motion";
import { UtensilsCrossed, TrendingUp, Shield, Zap } from "lucide-react";
import { SearchForm } from "@/components/SearchForm";
import { RestaurantConfirmation } from "@/components/RestaurantConfirmation";
import { ScanProgress } from "@/components/ScanProgress";
import { ResultsDashboard } from "@/components/ResultsDashboard";
import { LeadCaptureModal } from "@/components/LeadCaptureModal";

type AppState = "landing" | "confirmation" | "scanning" | "results";

// Mock data for demo
const mockRestaurant = {
  name: "The Golden Fork",
  address: "123 Main Street, San Francisco, CA 94102",
  rating: 4.3,
  reviewCount: 287,
  type: "American Restaurant",
};

const mockResults = {
  overall: 68,
  website: {
    score: 72,
    insights: [
      "Mobile load time is 4.2 seconds (should be under 3s)",
      "Missing meta descriptions on key pages",
    ],
  },
  google: {
    score: 85,
    insights: [
      "Profile is claimed and verified",
      "Business hours are up to date",
    ],
  },
  reviews: {
    score: 61,
    insights: [
      "Only 12% of reviews have owner responses",
      "Average rating dropped 0.3 stars this quarter",
    ],
  },
  ordering: {
    score: 45,
    insights: [
      "No direct online ordering available",
      "Order button hard to find on website",
    ],
  },
  issues: [
    {
      title: "Slow mobile website",
      description: "Page loads in 4.2s - customers may leave before it finishes",
      severity: "high" as const,
    },
    {
      title: "Low review response rate",
      description: "Responding to reviews builds trust and improves rankings",
      severity: "high" as const,
    },
    {
      title: "No direct ordering",
      description: "Third-party apps take 15-30% of each order",
      severity: "medium" as const,
    },
  ],
  opportunities: [
    {
      title: "Add online ordering",
      description: "Could increase revenue by 20% with direct orders",
      impact: "high" as const,
    },
    {
      title: "Respond to recent reviews",
      description: "23 reviews in the last month need responses",
      impact: "high" as const,
    },
    {
      title: "Update Google photos",
      description: "Last photo added 8 months ago - fresh photos boost engagement",
      impact: "medium" as const,
    },
  ],
};

const features = [
  {
    icon: Zap,
    title: "Instant Analysis",
    description: "Get your digital health score in under 60 seconds",
  },
  {
    icon: TrendingUp,
    title: "Actionable Insights",
    description: "Clear recommendations to improve your online presence",
  },
  {
    icon: Shield,
    title: "No Judgment",
    description: "Just guidance to help you grow your restaurant",
  },
];

const Index = () => {
  const [appState, setAppState] = useState<AppState>("landing");
  const [searchData, setSearchData] = useState({ name: "", city: "" });
  const [showLeadModal, setShowLeadModal] = useState(false);

  const handleSearch = (name: string, city: string) => {
    setSearchData({ name, city });
    setAppState("confirmation");
  };

  const handleConfirm = () => {
    setAppState("scanning");
  };

  const handleScanComplete = () => {
    setAppState("results");
  };

  const handleBack = () => {
    setAppState("landing");
    setSearchData({ name: "", city: "" });
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-40 bg-background/80 backdrop-blur-md border-b border-border">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-lg gradient-hero flex items-center justify-center">
              <UtensilsCrossed className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-display font-bold text-lg text-foreground">
              RestaurantGrader
            </span>
          </div>
        </div>
      </nav>

      <main className="pt-16">
        {appState === "landing" && (
          <div className="container mx-auto px-4">
            {/* Hero Section */}
            <section className="py-20 sm:py-32 text-center">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-3xl mx-auto mb-12"
              >
                <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-6 leading-tight">
                  How Healthy is Your{" "}
                  <span className="text-gradient">Digital Presence?</span>
                </h1>
                <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto">
                  Get a free, instant score of your restaurant's online performance. 
                  Discover what's working, what's not, and how to attract more customers.
                </p>
              </motion.div>

              <SearchForm onSearch={handleSearch} />

              {/* Social Proof */}
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="mt-8 text-sm text-muted-foreground"
              >
                Join 2,500+ restaurants that have improved their digital health
              </motion.p>
            </section>

            {/* Features */}
            <section className="pb-20 sm:pb-32">
              <div className="grid sm:grid-cols-3 gap-6 max-w-4xl mx-auto">
                {features.map((feature, index) => (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 + index * 0.1 }}
                    className="text-center p-6"
                  >
                    <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-primary/10 flex items-center justify-center">
                      <feature.icon className="w-6 h-6 text-primary" />
                    </div>
                    <h3 className="font-display font-semibold text-foreground mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-muted-foreground">{feature.description}</p>
                  </motion.div>
                ))}
              </div>
            </section>
          </div>
        )}

        {appState === "confirmation" && (
          <div className="container mx-auto px-4 py-20">
            <RestaurantConfirmation
              restaurant={{
                ...mockRestaurant,
                name: searchData.name || mockRestaurant.name,
              }}
              onConfirm={handleConfirm}
              onBack={handleBack}
            />
          </div>
        )}

        {appState === "scanning" && (
          <div className="container mx-auto px-4 py-20">
            <ScanProgress onComplete={handleScanComplete} />
          </div>
        )}

        {appState === "results" && (
          <div className="container mx-auto px-4 py-12">
            <ResultsDashboard
              restaurantName={searchData.name || mockRestaurant.name}
              results={mockResults}
              onBack={handleBack}
              onGetReport={() => setShowLeadModal(true)}
            />
          </div>
        )}
      </main>

      <LeadCaptureModal
        isOpen={showLeadModal}
        onClose={() => setShowLeadModal(false)}
        restaurantName={searchData.name || mockRestaurant.name}
        score={mockResults.overall}
      />
    </div>
  );
};

export default Index;
