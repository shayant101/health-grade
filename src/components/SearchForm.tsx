import { motion } from "framer-motion";
import { Search, MapPin } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useState } from "react";

interface SearchFormProps {
  onSearch: (name: string, city: string) => void;
}

export const SearchForm = ({ onSearch }: SearchFormProps) => {
  const [name, setName] = useState("");
  const [city, setCity] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim() && city.trim()) {
      onSearch(name.trim(), city.trim());
    }
  };

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      onSubmit={handleSubmit}
      className="w-full max-w-2xl mx-auto"
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
          <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
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
    </motion.form>
  );
};
