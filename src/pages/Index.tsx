import { useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, Shield, Zap } from "lucide-react";
import { SearchForm } from "@/components/SearchForm";
import { RestaurantConfirmation } from "@/components/RestaurantConfirmation";
import { ScanProgress } from "@/components/ScanProgress";
import { ResultsDashboard } from "@/components/ResultsDashboard";
import { WebsiteResults } from "@/components/WebsiteResults";
import { LeadCaptureModal } from "@/components/LeadCaptureModal";
import { api } from "@/services/api";
import { WebsiteAnalysisResponse } from "@/types/api";
import innowiLogo from "@/assets/innowi-logo.png";

type AppState = "landing" | "confirmation" | "scanning" | "results" | "website-analyzing" | "website-results";

// Mock data for demo
const mockRestaurant = {
  name: "The Golden Fork",
  website: "https://www.thegoldenfork.com",
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
  const [restaurant, setRestaurant] = useState(mockRestaurant);
  const [showLeadModal, setShowLeadModal] = useState(false);
  const [scanId, setScanId] = useState<string | null>(null);
  const [isCreatingScan, setIsCreatingScan] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);
  const [results, setResults] = useState(mockResults);
  const [realOverallScore, setRealOverallScore] = useState<number | null>(null);
  const [websiteResults, setWebsiteResults] = useState<WebsiteAnalysisResponse | null>(null);
  const [isAnalyzingWebsite, setIsAnalyzingWebsite] = useState(false);

  const handleSearch = (name: string, city: string) => {
    setSearchData({ name, city });
    // For Priority 1: Use mock restaurant data with the searched name
    // In Priority 2+: This will call restaurant search API
    setRestaurant({
      ...mockRestaurant,
      name: name || mockRestaurant.name,
    });
    setAppState("confirmation");
  };

  const handleConfirm = async () => {
    setIsCreatingScan(true);
    setScanError(null);
    
    try {
      // Call backend to create scan
      const { scan_id } = await api.createScan(
        restaurant.name,
        restaurant.website
      );
      
      console.log('✅ Scan created:', scan_id);
      setScanId(scan_id);
      setAppState("scanning");
    } catch (error) {
      console.error('❌ Scan creation failed:', error);
      setScanError(error instanceof Error ? error.message : 'Failed to create scan');
      // For now, show error but don't block UI
      // TODO: Add error toast notification
    } finally {
      setIsCreatingScan(false);
    }
  };

  const handleScanComplete = (data: any) => {
    console.log('🎉 Scan complete callback received:', data);
    
    // Store real overall score
    setRealOverallScore(data.overall);
    
    // For Priority 1: Keep mock data for categories
    // Just replace the overall score
    const resultsWithRealScore = {
      ...mockResults, // Keep mock category data
      overall: data.overall // Use real overall score
    };
    
    setResults(resultsWithRealScore);
    setAppState("results");
  };

  const handleQuickWebsiteCheck = async (url: string) => {
    setIsAnalyzingWebsite(true);
    setScanError(null);
    setAppState("website-analyzing");
    
    try {
      console.log('🌐 Starting website-only analysis for:', url);
      const results = await api.analyzeWebsite(url);
      console.log('✅ Website analysis complete:', results);
      
      setWebsiteResults(results);
      setAppState("website-results");
    } catch (error) {
      console.error('❌ Website analysis failed:', error);
      setScanError(error instanceof Error ? error.message : 'Failed to analyze website');
      setAppState("landing");
    } finally {
      setIsAnalyzingWebsite(false);
    }
  };

  const handleUpgradeToFullScan = () => {
    // When user wants to upgrade from website-only to full scan
    if (websiteResults) {
      setRestaurant({
        ...mockRestaurant,
        website: websiteResults.url,
        name: new URL(websiteResults.url).hostname.replace('www.', ''),
      });
      setAppState("confirmation");
    }
  };

  const handleBack = () => {
    setAppState("landing");
    setSearchData({ name: "", city: "" });
    setWebsiteResults(null);
    setScanError(null);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-40 bg-background/80 backdrop-blur-md border-b border-border">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <img src={innowiLogo} alt="Innowi Logo" className="w-9 h-9 rounded-lg" />
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

              <SearchForm
                onSearch={handleSearch}
                onQuickWebsiteCheck={handleQuickWebsiteCheck}
              />

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
              restaurant={restaurant}
              onConfirm={handleConfirm}
              onBack={handleBack}
            />
            {scanError && (
              <div className="max-w-lg mx-auto mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm">
                Error: {scanError}
              </div>
            )}
          </div>
        )}

        {appState === "scanning" && scanId && (
          <div className="container mx-auto px-4 py-20">
            <ScanProgress
              scanId={scanId}
              onComplete={handleScanComplete}
            />
          </div>
        )}

        {appState === "website-analyzing" && (
          <div className="container mx-auto px-4 py-20">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="max-w-md mx-auto text-center space-y-6"
            >
              <div className="w-16 h-16 mx-auto">
                <div className="w-full h-full border-4 border-primary border-t-transparent rounded-full animate-spin" />
              </div>
              <div>
                <h2 className="font-display text-2xl font-bold text-foreground mb-2">
                  Analyzing Your Website...
                </h2>
                <p className="text-muted-foreground">
                  Checking performance, mobile responsiveness, and security
                </p>
              </div>
            </motion.div>
          </div>
        )}

        {appState === "website-results" && websiteResults && (
          <div className="container mx-auto px-4 py-12">
            <WebsiteResults
              results={websiteResults}
              onUpgradeToFullScan={handleUpgradeToFullScan}
              onBack={handleBack}
            />
          </div>
        )}

        {appState === "results" && (
          <div className="container mx-auto px-4 py-12">
            <ResultsDashboard
              restaurantName={restaurant.name}
              results={results}
              onBack={handleBack}
              onGetReport={() => setShowLeadModal(true)}
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-background">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
            <span>Powered by</span>
            <img
              src={innowiLogo}
              alt="Innowi"
              className="h-6 w-auto"
            />
          </div>
        </div>
      </footer>

      <LeadCaptureModal
        isOpen={showLeadModal}
        onClose={() => setShowLeadModal(false)}
        restaurantName={restaurant.name}
        score={results.overall}
      />
    </div>
  );
};

export default Index;
