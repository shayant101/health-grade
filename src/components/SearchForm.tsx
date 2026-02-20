import { motion } from "framer-motion";
import { Search, Globe, Zap } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useState } from "react";

interface SearchFormProps {
  onSearch: (name: string, city: string) => void;
  onQuickWebsiteCheck?: (url: string) => void;
}

export const SearchForm = ({ onSearch, onQuickWebsiteCheck }: SearchFormProps) => {
  const [mode, setMode] = useState<"restaurant" | "website">("restaurant");
  const [name, setName] = useState("");
  const [city, setCity] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");

  const handleRestaurantSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim() && city.trim()) {
      onSearch(name.trim(), city.trim());
    }
  };

  const handleWebsiteSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (websiteUrl.trim() && onQuickWebsiteCheck) {
      onQuickWebsiteCheck(websiteUrl.trim());
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-4">
      {/* Mode Toggle */}
      <div className="flex gap-2 justify-center">
        <Button
          type="button"
          variant={mode === "restaurant" ? "default" : "outline"}
          onClick={() => setMode("restaurant")}
          className="flex items-center gap-2"
        >
          <Search className="w-4 h-4" />
          Full Restaurant Scan
        </Button>
        <Button
          type="button"
          variant={mode === "website" ? "default" : "outline"}
          onClick={() => setMode("website")}
          className="flex items-center gap-2"
        >
          <Zap className="w-4 h-4" />
          Quick Website Check
        </Button>
      </div>

      {/* Restaurant Search Form */}
      {mode === "restaurant" && (
        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          onSubmit={handleRestaurantSubmit}
          className="w-full"
        >
          <div className="bg-card rounded-2xl p-2 shadow-xl border border-border flex flex-col sm:flex-row gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Restaurant name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="pl-12 h-14 border-0 bg-transparent text-base focus-visible:ring-0 focus-visible:ring-offset-0"
                required
              />
            </div>
            <div className="w-px bg-border hidden sm:block" />
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <Input
                type="text"
                placeholder="City or ZIP code"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="pl-12 h-14 border-0 bg-transparent text-base focus-visible:ring-0 focus-visible:ring-offset-0"
                required
              />
            </div>
            <Button
              type="submit"
              className="h-14 px-8 gradient-hero text-primary-foreground hover:opacity-90 font-semibold text-base"
            >
              Check My Restaurant
            </Button>
          </div>
          <p className="text-xs text-muted-foreground text-center mt-2">
            Full analysis: Website, Google, Reviews & Ordering (10-15 seconds)
          </p>
        </motion.form>
      )}

      {/* Website-Only Form */}
      {mode === "website" && (
        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          onSubmit={handleWebsiteSubmit}
          className="w-full"
        >
          <div className="bg-card rounded-2xl p-2 shadow-xl border border-border flex flex-col sm:flex-row gap-2">
            <div className="flex-1 relative">
              <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Enter website URL (e.g., yourrestaurant.com)"
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
                className="pl-12 h-14 border-0 bg-transparent text-base focus-visible:ring-0 focus-visible:ring-offset-0"
                required
              />
            </div>
            <Button
              type="submit"
              className="h-14 px-8 bg-gradient-to-r from-yellow-500 to-orange-500 text-white hover:opacity-90 font-semibold text-base"
            >
              <Zap className="w-4 h-4 mr-2" />
              Quick Check
            </Button>
          </div>
          <p className="text-xs text-muted-foreground text-center mt-2">
            Fast website-only analysis: Performance, Mobile & Security (2-5 seconds)
          </p>
        </motion.form>
      )}
    </div>
  );
};
