"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { BookOpen, Search, Star, Lightbulb, TrendingUp } from "lucide-react";

const knowledgeEntries = [
  {
    id: 1,
    from: "70 GSM",
    to: "120 GSM",
    category: "Best Practice",
    rating: 4.8,
    title: "Optimal Machine Speed Reduction Profile",
    content: "For 70→120 GSM transitions, reduce machine speed in 5 m/min decrements every 15 seconds rather than continuous ramping. This stepped approach minimizes basis weight oscillation by allowing the forming section to stabilize between adjustments.",
    results: "Stabilization time improved by 32%, waste reduced by 18%",
    author: "Engineer_01",
    date: "2026-07-10",
  },
  {
    id: 2,
    from: "Any",
    to: "Any",
    category: "Critical Insight",
    rating: 4.9,
    title: "Pre-warming Dryer Sections Before Large GSM Jumps",
    content: "When transitioning to grades 50+ GSM above current, pre-warm the dryer section to target temperature +5°C for 3 minutes before initiating the transition. This prevents the temporary moisture spike that causes GSM overshoot.",
    results: "GSM overshoot eliminated in 94% of cases",
    author: "Supervisor_01",
    date: "2026-07-08",
  },
  {
    id: 3,
    from: "100 GSM",
    to: "80 GSM",
    category: "Lessons Learned",
    rating: 4.5,
    title: "Downward Transition Flow Rate Management",
    content: "Decreasing flow rate too quickly during downward transitions causes fiber clumping. Maintain flow rate within 5% of original for first 2 minutes, then reduce gradually over 5 minutes.",
    results: "Quality defects reduced by 45%",
    author: "Operator_02",
    date: "2026-07-05",
  },
  {
    id: 4,
    from: "Any",
    to: "Any",
    category: "Best Practice",
    rating: 4.7,
    title: "Chemical Dosage Optimization During Transitions",
    content: "Increase retention aid dosage by 15% during the first 2 minutes of any transition. This compensates for the temporary disruption in fiber retention caused by changing process conditions.",
    results: "First-pass retention improved by 8%",
    author: "Engineer_01",
    date: "2026-06-28",
  },
  {
    id: 5,
    from: "120 GSM",
    to: "200 GSM",
    category: "Critical Insight",
    rating: 4.6,
    title: "Headbox Pressure Adjustment for Heavy Grades",
    content: "For transitions to grades above 150 GSM, increase headbox pressure to 3.0+ bar BEFORE reducing speed. The higher pressure ensures proper fiber orientation in heavier sheets.",
    results: "Formation quality improved by 22%",
    author: "Engineer_02",
    date: "2026-06-20",
  },
];

export default function KnowledgePage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");

  const filtered = knowledgeEntries.filter((e) => {
    const matchSearch =
      !search ||
      e.title.toLowerCase().includes(search.toLowerCase()) ||
      e.content.toLowerCase().includes(search.toLowerCase());
    const matchCategory = category === "All" || e.category === category;
    return matchSearch && matchCategory;
  });

  const categories = ["All", "Best Practice", "Critical Insight", "Lessons Learned"];

  return (
    <div className="space-y-8 animate-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">AI Knowledge Base</h1>
        <p className="text-muted-foreground mt-1">
          Organizational knowledge repository — lessons learned, best practices, and transition insights
        </p>
      </div>

      {/* Search & Filter */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search knowledge base..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-sm focus:outline-none focus:border-blue-500/50"
          />
        </div>
        <div className="flex gap-2">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                category === cat
                  ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                  : "bg-accent/30 text-muted-foreground hover:text-foreground"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Knowledge Cards */}
      <div className="space-y-4">
        {filtered.map((entry, i) => (
          <motion.div
            key={entry.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card border-l-4 border-blue-500"
          >
            <div className="flex items-start justify-between mb-2">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400">
                    {entry.category}
                  </span>
                  {entry.from !== "Any" && (
                    <span className="text-xs text-muted-foreground">
                      {entry.from} → {entry.to}
                    </span>
                  )}
                </div>
                <h3 className="text-lg font-semibold">{entry.title}</h3>
              </div>
              <div className="flex items-center gap-1 text-amber-400">
                <Star className="w-4 h-4 fill-current" />
                <span className="text-sm font-medium">{entry.rating}</span>
              </div>
            </div>

            <p className="text-sm text-muted-foreground mb-3 leading-relaxed">{entry.content}</p>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <span>By {entry.author}</span>
                <span>{entry.date}</span>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-emerald-400">
                <TrendingUp className="w-3.5 h-3.5" />
                <span>{entry.results}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
          <BookOpen className="w-16 h-16 mb-4 opacity-30" />
          <p>No entries found matching your search</p>
        </div>
      )}
    </div>
  );
}
