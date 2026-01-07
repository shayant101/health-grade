import { motion } from "framer-motion";
import { Globe, Building2, Star, ShoppingCart, ArrowLeft, Download } from "lucide-react";
import { ScoreCircle } from "./ScoreCircle";
import { CategoryCard } from "./CategoryCard";
import { IssuesOpportunities } from "./IssuesOpportunities";
import { Button } from "./ui/button";

interface ResultsData {
  overall: number;
  website: { score: number; insights: string[] };
  google: { score: number; insights: string[] };
  reviews: { score: number; insights: string[] };
  ordering: { score: number; insights: string[] };
  issues: { title: string; description: string; severity: "high" | "medium" | "low" }[];
  opportunities: { title: string; description: string; impact: "high" | "medium" }[];
}

interface ResultsDashboardProps {
  restaurantName: string;
  results: ResultsData;
  onBack: () => void;
  onGetReport: () => void;
}

const getHealthExplanation = (score: number, name: string) => {
  if (score >= 90) {
    return `${name} has an excellent digital presence. You're ahead of most competitors!`;
  }
  if (score >= 75) {
    return `${name} has a strong online presence with room for optimization.`;
  }
  if (score >= 55) {
    return `${name}'s digital presence needs attention. There are clear opportunities to improve.`;
  }
  return `${name}'s digital presence is at risk. Immediate action is recommended.`;
};

export const ResultsDashboard = ({
  restaurantName,
  results,
  onBack,
  onGetReport,
}: ResultsDashboardProps) => {
  return (
    <div className="w-full max-w-5xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between mb-8"
      >
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span className="text-sm">New Search</span>
        </button>
        <Button onClick={onGetReport} className="gradient-hero text-primary-foreground hover:opacity-90">
          <Download className="w-4 h-4 mr-2" />
          Get Full Report
        </Button>
      </motion.div>

      {/* Overall Score Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-card rounded-2xl p-8 shadow-xl border border-border mb-8 text-center"
      >
        <h1 className="font-display text-2xl sm:text-3xl font-bold text-foreground mb-2">
          Digital Health Score for
        </h1>
        <p className="text-xl text-primary font-semibold mb-8">{restaurantName}</p>
        
        <div className="flex justify-center mb-6">
          <ScoreCircle score={results.overall} size="lg" />
        </div>
        
        <p className="text-muted-foreground max-w-xl mx-auto">
          {getHealthExplanation(results.overall, restaurantName)}
        </p>
      </motion.div>

      {/* Category Breakdown */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="mb-8"
      >
        <h2 className="font-display text-xl font-semibold text-foreground mb-4">
          Category Breakdown
        </h2>
        <div className="grid sm:grid-cols-2 gap-4">
          <CategoryCard
            title="Website"
            score={results.website.score}
            icon={Globe}
            insights={results.website.insights}
            delay={0.3}
          />
          <CategoryCard
            title="Google Business Profile"
            score={results.google.score}
            icon={Building2}
            insights={results.google.insights}
            delay={0.4}
          />
          <CategoryCard
            title="Reviews & Reputation"
            score={results.reviews.score}
            icon={Star}
            insights={results.reviews.insights}
            delay={0.5}
          />
          <CategoryCard
            title="Online Ordering"
            score={results.ordering.score}
            icon={ShoppingCart}
            insights={results.ordering.insights}
            delay={0.6}
          />
        </div>
      </motion.div>

      {/* Issues & Opportunities */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mb-8"
      >
        <h2 className="font-display text-xl font-semibold text-foreground mb-4">
          Issues & Opportunities
        </h2>
        <IssuesOpportunities issues={results.issues} opportunities={results.opportunities} />
      </motion.div>

      {/* CTA */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="bg-gradient-to-br from-primary/10 to-accent/5 rounded-2xl p-8 text-center border border-primary/20"
      >
        <h3 className="font-display text-xl font-bold text-foreground mb-2">
          Ready to Improve Your Score?
        </h3>
        <p className="text-muted-foreground mb-6 max-w-md mx-auto">
          Get a detailed report with step-by-step recommendations tailored for your restaurant.
        </p>
        <Button onClick={onGetReport} size="lg" className="gradient-hero text-primary-foreground hover:opacity-90">
          Get My Full Report
        </Button>
      </motion.div>
    </div>
  );
};
