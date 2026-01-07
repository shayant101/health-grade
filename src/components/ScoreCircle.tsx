import { motion } from "framer-motion";
import { useEffect, useState } from "react";

interface ScoreCircleProps {
  score: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}

const getScoreColor = (score: number) => {
  if (score >= 90) return "text-score-excellent";
  if (score >= 75) return "text-score-strong";
  if (score >= 55) return "text-score-attention";
  return "text-score-risk";
};

const getScoreStroke = (score: number) => {
  if (score >= 90) return "stroke-score-excellent";
  if (score >= 75) return "stroke-score-strong";
  if (score >= 55) return "stroke-score-attention";
  return "stroke-score-risk";
};

const getHealthLabel = (score: number) => {
  if (score >= 90) return "Excellent";
  if (score >= 75) return "Strong";
  if (score >= 55) return "Needs Attention";
  return "At Risk";
};

const sizeConfig = {
  sm: { dimension: 80, strokeWidth: 6, fontSize: "text-xl" },
  md: { dimension: 140, strokeWidth: 8, fontSize: "text-4xl" },
  lg: { dimension: 200, strokeWidth: 10, fontSize: "text-6xl" },
};

export const ScoreCircle = ({ score, size = "lg", showLabel = true }: ScoreCircleProps) => {
  const [displayScore, setDisplayScore] = useState(0);
  const config = sizeConfig[size];
  const radius = (config.dimension - config.strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  useEffect(() => {
    const duration = 1500;
    const steps = 60;
    const increment = score / steps;
    let current = 0;
    
    const timer = setInterval(() => {
      current += increment;
      if (current >= score) {
        setDisplayScore(score);
        clearInterval(timer);
      } else {
        setDisplayScore(Math.floor(current));
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [score]);

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: config.dimension, height: config.dimension }}>
        <svg
          width={config.dimension}
          height={config.dimension}
          className="-rotate-90"
        >
          {/* Background circle */}
          <circle
            cx={config.dimension / 2}
            cy={config.dimension / 2}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={config.strokeWidth}
            className="text-muted/50"
          />
          {/* Score circle */}
          <motion.circle
            cx={config.dimension / 2}
            cy={config.dimension / 2}
            r={radius}
            fill="none"
            strokeWidth={config.strokeWidth}
            strokeLinecap="round"
            className={getScoreStroke(score)}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            style={{
              strokeDasharray: circumference,
            }}
          />
        </svg>
        {/* Score number */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`font-display font-bold ${config.fontSize} ${getScoreColor(score)}`}>
            {displayScore}
          </span>
        </div>
      </div>
      {showLabel && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.5 }}
          className={`px-4 py-1.5 rounded-full text-sm font-semibold ${
            score >= 90
              ? "bg-score-excellent/10 text-score-excellent"
              : score >= 75
              ? "bg-score-strong/10 text-score-strong"
              : score >= 55
              ? "bg-score-attention/10 text-score-attention"
              : "bg-score-risk/10 text-score-risk"
          }`}
        >
          {getHealthLabel(score)}
        </motion.div>
      )}
    </div>
  );
};
