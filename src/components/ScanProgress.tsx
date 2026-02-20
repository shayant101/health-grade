import { motion } from "framer-motion";
import { Check } from "lucide-react";
import { useEffect, useState, useRef } from "react";
import { api } from "@/services/api";
import { ScanResponse } from "@/types/api";
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
  scanId: string;
  onComplete: (data: any) => void;
}

export const ScanProgress = ({ scanId, onComplete }: ScanProgressProps) => {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<string>('pending');
  const [currentScan, setCurrentScan] = useState<ScanResponse | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  
  // Prevent double-completion in React Strict Mode
  const hasCompletedRef = useRef(false);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!scanId || hasCompletedRef.current) return;

    console.log('🔄 Starting polling for scan:', scanId);

    const pollScan = async () => {
      try {
        const scan = await api.getScan(scanId);
        console.log('📊 Scan status:', scan.status, 'Score:', scan.overall_score);
        
        setCurrentScan(scan);
        setStatus(scan.status);

        // Update progress based on status
        if (scan.status === 'pending') {
          setProgress(10);
        } else if (scan.status === 'in_progress') {
          setProgress(50);
        } else if (scan.status === 'completed') {
          setProgress(100);
          
          // Stop polling
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
          
          // Prevent double-completion
          if (!hasCompletedRef.current) {
            hasCompletedRef.current = true;
            console.log('✅ Scan completed! Overall score:', scan.overall_score);
            
            // For Priority 1: Pass minimal data (just overall score)
            // We'll keep mock data for categories until Priority 2+
            onComplete({
              overall: scan.overall_score || 0,
              scanData: scan // Pass full scan for debugging
            });
          }
        } else if (scan.status === 'failed') {
          setProgress(0);
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
          console.error('❌ Scan failed:', scan.error_message);
          // TODO: Show error message to user
        }
      } catch (error) {
        console.error('❌ Polling error:', error);
        // Don't stop polling on error - might be temporary network issue
      }
    };

    // Initial poll immediately
    pollScan();

    // Intelligent polling: Only poll if status is pending or in_progress
    pollingIntervalRef.current = setInterval(() => {
      // Only poll if not completed/failed
      if (status !== 'completed' && status !== 'failed') {
        pollScan();
      } else {
        // Stop polling if completed/failed
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      }
    }, 2000); // Poll every 2 seconds

    // Cleanup on unmount
    return () => {
      if (pollingIntervalRef.current) {
        console.log('🛑 Stopping polling');
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [scanId, status, onComplete]);

  // Animate steps based on progress
  useEffect(() => {
    if (progress >= 20 && currentStep < 1) {
      setCompletedSteps(['discover']);
      setCurrentStep(1);
    } else if (progress >= 40 && currentStep < 2) {
      setCompletedSteps(['discover', 'website']);
      setCurrentStep(2);
    } else if (progress >= 60 && currentStep < 3) {
      setCompletedSteps(['discover', 'website', 'google']);
      setCurrentStep(3);
    } else if (progress >= 80 && currentStep < 4) {
      setCompletedSteps(['discover', 'website', 'google', 'reviews']);
      setCurrentStep(4);
    } else if (progress >= 100 && currentStep < 5) {
      setCompletedSteps(['discover', 'website', 'google', 'reviews', 'ordering']);
      setCurrentStep(5);
    }
  }, [progress, currentStep]);

  return (
    <div className="w-full max-w-md mx-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-card rounded-2xl p-8 shadow-xl border border-border"
      >
        {/* Debug info */}
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-xs text-blue-800">
          <div>Status: <strong>{status}</strong></div>
          <div>Progress: <strong>{progress}%</strong></div>
          <div>Scan ID: <strong className="font-mono">{scanId}</strong></div>
        </div>

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

        {/* Progress bar */}
        <div className="mb-6">
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-primary to-primary/80"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
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
