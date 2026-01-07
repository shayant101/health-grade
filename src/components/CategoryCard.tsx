import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";
import { ScoreCircle } from "./ScoreCircle";

interface CategoryCardProps {
  title: string;
  score: number;
  icon: LucideIcon;
  insights: string[];
  delay?: number;
}

const getStatusText = (score: number) => {
  if (score >= 90) return "Excellent";
  if (score >= 75) return "Strong";
  if (score >= 55) return "Needs Work";
  return "At Risk";
};

export const CategoryCard = ({ title, score, icon: Icon, insights, delay = 0 }: CategoryCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="bg-card rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow border border-border"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-primary/10">
            <Icon className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="font-display font-semibold text-foreground">{title}</h3>
            <p className="text-sm text-muted-foreground">{getStatusText(score)}</p>
          </div>
        </div>
        <ScoreCircle score={score} size="sm" showLabel={false} />
      </div>
      <div className="space-y-2">
        {insights.map((insight, index) => (
          <div key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
            <span className="text-primary mt-0.5">•</span>
            <span>{insight}</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
};
