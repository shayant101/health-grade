import { motion } from "framer-motion";
import { AlertTriangle, Lightbulb, Check } from "lucide-react";

interface Issue {
  title: string;
  description: string;
  severity: "high" | "medium" | "low";
}

interface Opportunity {
  title: string;
  description: string;
  impact: "high" | "medium";
}

interface IssuesOpportunitiesProps {
  issues: Issue[];
  opportunities: Opportunity[];
}

export const IssuesOpportunities = ({ issues, opportunities }: IssuesOpportunitiesProps) => {
  return (
    <div className="grid md:grid-cols-2 gap-6">
      {/* Issues */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-card rounded-xl p-6 shadow-md border border-border"
      >
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 rounded-lg bg-score-risk/10">
            <AlertTriangle className="w-5 h-5 text-score-risk" />
          </div>
          <h3 className="font-display font-semibold text-lg text-foreground">
            Issues Hurting Performance
          </h3>
        </div>
        <div className="space-y-3">
          {issues.map((issue, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
              className="p-3 bg-muted/30 rounded-lg"
            >
              <div className="flex items-start gap-2">
                <span
                  className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                    issue.severity === "high"
                      ? "bg-score-risk"
                      : issue.severity === "medium"
                      ? "bg-score-attention"
                      : "bg-muted-foreground"
                  }`}
                />
                <div>
                  <p className="font-medium text-foreground text-sm">{issue.title}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{issue.description}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Opportunities */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-card rounded-xl p-6 shadow-md border border-border"
      >
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 rounded-lg bg-score-excellent/10">
            <Lightbulb className="w-5 h-5 text-score-excellent" />
          </div>
          <h3 className="font-display font-semibold text-lg text-foreground">
            Quick Win Opportunities
          </h3>
        </div>
        <div className="space-y-3">
          {opportunities.map((opp, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
              className="p-3 bg-muted/30 rounded-lg"
            >
              <div className="flex items-start gap-2">
                <Check
                  className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                    opp.impact === "high" ? "text-score-excellent" : "text-score-strong"
                  }`}
                />
                <div>
                  <p className="font-medium text-foreground text-sm">{opp.title}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{opp.description}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};
