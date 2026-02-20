import { motion } from "framer-motion";
import { MapPin, Star, Store, ArrowLeft } from "lucide-react";
import { Button } from "./ui/button";

interface RestaurantData {
  name: string;
  website: string;
  address: string;
  rating: number;
  reviewCount: number;
  type: string;
}

interface RestaurantConfirmationProps {
  restaurant: RestaurantData;
  onConfirm: () => void;
  onBack: () => void;
}

export const RestaurantConfirmation = ({
  restaurant,
  onConfirm,
  onBack,
}: RestaurantConfirmationProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-lg mx-auto"
    >
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span className="text-sm">Back to search</span>
      </button>

      <div className="bg-card rounded-2xl p-6 shadow-xl border border-border">
        <h2 className="font-display text-xl font-semibold text-foreground mb-4">
          Is this your restaurant?
        </h2>

        <div className="flex gap-4 mb-6">
          <div className="w-20 h-20 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
            <Store className="w-10 h-10 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-display font-bold text-lg text-foreground truncate">
              {restaurant.name}
            </h3>
            <p className="text-sm text-muted-foreground mb-2">{restaurant.type}</p>
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-1">
                <Star className="w-4 h-4 text-score-attention fill-current" />
                <span className="font-medium text-foreground">{restaurant.rating}</span>
                <span className="text-muted-foreground">({restaurant.reviewCount} reviews)</span>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-3 mb-6">
          <div className="flex items-start gap-2 p-3 bg-muted/30 rounded-lg">
            <MapPin className="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
            <p className="text-sm text-muted-foreground">{restaurant.address}</p>
          </div>
          <div className="flex items-start gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <span className="text-xs text-blue-600 mt-0.5">🌐</span>
            <p className="text-sm text-blue-800 font-mono break-all">{restaurant.website}</p>
          </div>
        </div>

        <div className="flex gap-3">
          <Button variant="outline" className="flex-1" onClick={onBack}>
            Not my restaurant
          </Button>
          <Button className="flex-1 gradient-hero text-primary-foreground hover:opacity-90" onClick={onConfirm}>
            Yes, scan this restaurant
          </Button>
        </div>
      </div>
    </motion.div>
  );
};
