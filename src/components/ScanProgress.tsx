import { motion } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import innowiLogo from "@/assets/innowi-logo.png";

interface ScanStep {
  id: string;
  label: string;
  duration: number;
}

const scanSteps: ScanStep[] = [
  { id: "discover", label: "Finding your restaurant online", duration: 1200 },
  { id: "website", label: "Analyzing website performance", duration: 1500 },
  { id: "google", label: "Checking Google Business Profile", duration: 1300 },
  { id: "reviews", label: "Reviewing reputation & ratings", duration: 1400 },
  { id: "ordering", label: "Evaluating ordering capabilities", duration: 1000 },
];

interface ScanProgressProps {
  onComplete: () => void;
}

export const ScanProgress = ({ onComplete }: ScanProgressProps) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);

  useEffect(() => {
    if (currentStep >= scanSteps.length) {
      setTimeout(onComplete, 500);
      return;
    }

    const timer = setTimeout(() => {
      setCompletedSteps((prev) => [...prev, scanSteps[currentStep].id]);
      setCurrentStep((prev) => prev + 1);
    }, scanSteps[currentStep].duration);

    return () => clearTimeout(timer);
  }, [currentStep, onComplete]);

  return (
    <div className="w-full max-w-md mx-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-card rounded-2xl p-8 shadow-xl border border-border"
      >
        <div className="text-center mb-8">
          <motion.div
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            className="w-16 h-16 mx-auto mb-4 rounded-2xl shadow-glow overflow-hidden"
          >
            <img src={innowiLogo} alt="Scanning" className="w-full h-full object-cover" />
          </motion.div>
          <h2 className="font-display text-2xl font-bold text-foreground mb-2">
            Scanning Your Restaurant
          </h2>
          <p className="text-muted-foreground">
            We're analyzing your digital presence. This only takes a moment.
          </p>
        </div>

        <div className="space-y-4">
          {scanSteps.map((step, index) => {
            const isCompleted = completedSteps.includes(step.id);
            const isActive = currentStep === index;

            return (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
                  isActive ? "bg-primary/5" : isCompleted ? "bg-muted/30" : ""
                }`}
              >
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center transition-all ${
                    isCompleted
                      ? "bg-score-excellent text-white"
                      : isActive
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground"
                  }`}
                >
                  {isCompleted ? (
                    <Check className="w-4 h-4" />
                  ) : isActive ? (
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 1, repeat: Infinity }}
                      className="w-2 h-2 bg-primary-foreground rounded-full"
                    />
                  ) : (
                    <span className="text-xs font-medium">{index + 1}</span>
                  )}
                </div>
                <span
                  className={`text-sm font-medium ${
                    isCompleted
                      ? "text-foreground"
                      : isActive
                      ? "text-foreground"
                      : "text-muted-foreground"
                  }`}
                >
                  {step.label}
                </span>
              </motion.div>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
};
