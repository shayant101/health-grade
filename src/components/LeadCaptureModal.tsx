import { motion, AnimatePresence } from "framer-motion";
import { X, FileText, MessageSquare } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useState } from "react";

interface LeadCaptureModalProps {
  isOpen: boolean;
  onClose: () => void;
  restaurantName: string;
  score: number;
}

export const LeadCaptureModal = ({
  isOpen,
  onClose,
  restaurantName,
  score,
}: LeadCaptureModalProps) => {
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, this would send to backend
    setSubmitted(true);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-foreground/20 backdrop-blur-sm"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            onClick={(e) => e.stopPropagation()}
            className="bg-card rounded-2xl p-8 shadow-2xl border border-border w-full max-w-md relative"
          >
            <button
              onClick={onClose}
              className="absolute top-4 right-4 p-2 rounded-lg hover:bg-muted transition-colors"
            >
              <X className="w-5 h-5 text-muted-foreground" />
            </button>

            {!submitted ? (
              <>
                <div className="text-center mb-6">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full gradient-hero flex items-center justify-center shadow-glow">
                    <FileText className="w-8 h-8 text-primary-foreground" />
                  </div>
                  <h2 className="font-display text-2xl font-bold text-foreground mb-2">
                    Get Your Full Report
                  </h2>
                  <p className="text-muted-foreground text-sm">
                    Receive a detailed breakdown of your digital health score with actionable recommendations for <span className="font-semibold text-foreground">{restaurantName}</span>
                  </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1.5">
                      Email Address *
                    </label>
                    <Input
                      type="email"
                      placeholder="you@restaurant.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1.5">
                      Phone Number <span className="text-muted-foreground">(optional)</span>
                    </label>
                    <Input
                      type="tel"
                      placeholder="(555) 123-4567"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="w-full"
                    />
                  </div>
                  <Button type="submit" className="w-full gradient-hero text-primary-foreground hover:opacity-90 h-12 font-semibold">
                    Get My Full Report
                  </Button>
                </form>

                <div className="mt-4 pt-4 border-t border-border">
                  <button className="w-full flex items-center justify-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors py-2">
                    <MessageSquare className="w-4 h-4" />
                    Talk to an Expert Instead
                  </button>
                </div>
              </>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center py-4"
              >
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-score-excellent/10 flex items-center justify-center">
                  <FileText className="w-8 h-8 text-score-excellent" />
                </div>
                <h2 className="font-display text-2xl font-bold text-foreground mb-2">
                  Report Sent!
                </h2>
                <p className="text-muted-foreground text-sm mb-6">
                  Check your inbox for the full digital health report for {restaurantName}.
                </p>
                <Button variant="outline" onClick={onClose} className="w-full">
                  Close
                </Button>
              </motion.div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
