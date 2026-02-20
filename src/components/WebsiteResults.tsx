import { motion } from "framer-motion";
import { CheckCircle2, XCircle, AlertCircle, ArrowRight, Sparkles } from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { WebsiteAnalysisResponse } from "@/types/api";

interface WebsiteResultsProps {
  results: WebsiteAnalysisResponse;
  onUpgradeToFullScan: () => void;
  onBack: () => void;
}

export const WebsiteResults = ({ results, onUpgradeToFullScan, onBack }: WebsiteResultsProps) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return "Excellent";
    if (score >= 60) return "Good";
    if (score >= 40) return "Needs Work";
    return "Critical";
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case "high":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "medium":
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case "low":
        return <CheckCircle2 className="w-5 h-5 text-blue-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getPriorityBadgeColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-100 text-red-800 border-red-200";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "low":
        return "bg-blue-100 text-blue-800 border-blue-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const { https_enabled, mobile_friendly, online_ordering_links_count } = results.analysis_data;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="font-display text-3xl sm:text-4xl font-bold text-foreground mb-2">
          Website Analysis Complete
        </h1>
        <p className="text-muted-foreground">
          Here's your quick website health check for <span className="font-semibold">{results.url}</span>
        </p>
      </motion.div>

      {/* Score Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="border-2">
          <CardHeader className="text-center pb-4">
            <CardTitle className="text-lg text-muted-foreground">Website Score</CardTitle>
            <div className="flex items-center justify-center gap-4 mt-4">
              <div className={`text-6xl font-bold ${getScoreColor(results.website_score)}`}>
                {Math.round(results.website_score)}
              </div>
              <div className="text-left">
                <div className="text-2xl font-semibold text-foreground">
                  {getScoreLabel(results.website_score)}
                </div>
                <div className="text-sm text-muted-foreground">out of 100</div>
              </div>
            </div>
          </CardHeader>
          <CardContent className="border-t pt-6">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="space-y-2">
                <div className="flex items-center justify-center">
                  {https_enabled ? (
                    <CheckCircle2 className="w-6 h-6 text-green-500" />
                  ) : (
                    <XCircle className="w-6 h-6 text-red-500" />
                  )}
                </div>
                <div className="text-sm font-medium">HTTPS</div>
                <div className="text-xs text-muted-foreground">
                  {https_enabled ? "Enabled" : "Disabled"}
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-center">
                  {mobile_friendly ? (
                    <CheckCircle2 className="w-6 h-6 text-green-500" />
                  ) : (
                    <XCircle className="w-6 h-6 text-red-500" />
                  )}
                </div>
                <div className="text-sm font-medium">Mobile</div>
                <div className="text-xs text-muted-foreground">
                  {mobile_friendly ? "Friendly" : "Not Optimized"}
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-center">
                  {online_ordering_links_count > 0 ? (
                    <CheckCircle2 className="w-6 h-6 text-green-500" />
                  ) : (
                    <XCircle className="w-6 h-6 text-red-500" />
                  )}
                </div>
                <div className="text-sm font-medium">Ordering</div>
                <div className="text-xs text-muted-foreground">
                  {online_ordering_links_count > 0 ? "Available" : "Not Found"}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Recommendations */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Recommendations</CardTitle>
            <CardDescription>
              Top {results.recommendations.length} actions to improve your website
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {results.recommendations.map((rec, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className="flex gap-4 p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
              >
                <div className="flex-shrink-0 mt-1">
                  {getPriorityIcon(rec.priority)}
                </div>
                <div className="flex-1 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-semibold text-foreground">{rec.title}</h4>
                    <Badge variant="outline" className={getPriorityBadgeColor(rec.priority)}>
                      {rec.priority}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{rec.description}</p>
                  <div className="text-xs text-muted-foreground">
                    Category: {rec.category}
                  </div>
                </div>
              </motion.div>
            ))}
          </CardContent>
        </Card>
      </motion.div>

      {/* Upgrade CTA */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="border-2 border-primary/20 bg-gradient-to-br from-primary/5 to-primary/10">
          <CardContent className="pt-6">
            <div className="flex flex-col sm:flex-row items-center gap-6">
              <div className="flex-shrink-0">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                  <Sparkles className="w-8 h-8 text-primary" />
                </div>
              </div>
              <div className="flex-1 text-center sm:text-left">
                <h3 className="font-display text-xl font-bold text-foreground mb-2">
                  Want the Full Picture?
                </h3>
                <p className="text-muted-foreground mb-4">
                  Get a comprehensive analysis including Google Business Profile, reviews, 
                  online ordering integration, and more. See exactly how you compare to competitors.
                </p>
                <div className="flex flex-col sm:flex-row gap-3">
                  <Button
                    onClick={onUpgradeToFullScan}
                    className="gradient-hero text-primary-foreground hover:opacity-90"
                  >
                    Get Your Full Restaurant Grade
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                  <Button variant="outline" onClick={onBack}>
                    Check Another Website
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
