"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { History, Search, CheckCircle2, Clock, TrendingUp } from "lucide-react";

const historicalTransitions = [
  {
    id: 1,
    from: "70 GSM Copy Paper",
    to: "120 GSM Card Stock",
    startedAt: "2026-07-14 08:30",
    stabilizationTime: 285,
    success: true,
    waste: 42.5,
    settings: { machine_speed: 720, dryer_temperature: 130, headbox_pressure: 2.8 },
    lessons: "Gradual speed reduction over 5 min yielded best results. Chemical dosage adjustment critical in first 2 min.",
  },
  {
    id: 2,
    from: "80 GSM Bond Paper",
    to: "100 GSM Cover Paper",
    startedAt: "2026-07-14 14:15",
    stabilizationTime: 198,
    success: true,
    waste: 28.3,
    settings: { machine_speed: 750, dryer_temperature: 125, headbox_pressure: 2.7 },
    lessons: "Small GSM jump — minimal adjustments needed. Focus on dryer temp control.",
  },
  {
    id: 3,
    from: "100 GSM Cover Paper",
    to: "150 GSM Heavy Card",
    startedAt: "2026-07-13 10:45",
    stabilizationTime: 420,
    success: true,
    waste: 65.1,
    settings: { machine_speed: 680, dryer_temperature: 135, headbox_pressure: 3.0 },
    lessons: "Larger GSM jump requires patience. Speed reduction should be stepped, not continuous.",
  },
  {
    id: 4,
    from: "90 GSM Ledger Paper",
    to: "70 GSM Copy Paper",
    startedAt: "2026-07-13 06:00",
    stabilizationTime: 312,
    success: false,
    waste: 89.2,
    settings: { machine_speed: 820, dryer_temperature: 118, headbox_pressure: 2.3 },
    lessons: "Downward transition trickier than expected. Speed increase caused oscillation. Step changes recommended.",
  },
  {
    id: 5,
    from: "120 GSM Card Stock",
    to: "200 GSM Board",
    startedAt: "2026-07-12 16:20",
    stabilizationTime: 510,
    success: true,
    waste: 78.9,
    settings: { machine_speed: 620, dryer_temperature: 142, headbox_pressure: 3.2 },
    lessons: "Large upward transition. Key was pre-heating dryers before speed reduction.",
  },
];

export default function HistoryPage() {
  const [searchFrom, setSearchFrom] = useState("");
  const [searchTo, setSearchTo] = useState("");
  const [filtered, setFiltered] = useState(historicalTransitions);

  const handleSearch = () => {
    const results = historicalTransitions.filter((t) => {
      const fromMatch = !searchFrom || t.from.toLowerCase().includes(searchFrom.toLowerCase());
      const toMatch = !searchTo || t.to.toLowerCase().includes(searchTo.toLowerCase());
      return fromMatch && toMatch;
    });
    setFiltered(results);
  };

  const avgStabTime = filtered.reduce((sum, t) => sum + t.stabilizationTime, 0) / Math.max(filtered.length, 1);
  const successRate = (filtered.filter((t) => t.success).length / Math.max(filtered.length, 1)) * 100;

  return (
    <div className="space-y-8 animate-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Historical Grade Transitions</h1>
        <p className="text-muted-foreground mt-1">
          Analyze past transitions, learn from experience, and apply best practices
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card !py-4 text-center">
          <Clock className="w-5 h-5 text-blue-400 mx-auto mb-1" />
          <span className="text-2xl font-bold">{avgStabTime.toFixed(0)}s</span>
          <span className="text-xs text-muted-foreground block">Avg Stabilization Time</span>
        </div>
        <div className="glass-card !py-4 text-center">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
          <span className="text-2xl font-bold">{successRate.toFixed(0)}%</span>
          <span className="text-xs text-muted-foreground block">Success Rate</span>
        </div>
        <div className="glass-card !py-4 text-center">
          <TrendingUp className="w-5 h-5 text-purple-400 mx-auto mb-1" />
          <span className="text-2xl font-bold">{filtered.length}</span>
          <span className="text-xs text-muted-foreground block">Total Transitions</span>
        </div>
      </div>

      {/* Search */}
      <div className="glass-card">
        <div className="flex flex-col md:flex-row gap-4">
          <input
            type="text"
            placeholder="From grade (e.g., 70 GSM)..."
            value={searchFrom}
            onChange={(e) => setSearchFrom(e.target.value)}
            className="flex-1 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-sm focus:outline-none focus:border-blue-500/50"
          />
          <input
            type="text"
            placeholder="To grade (e.g., 120 GSM)..."
            value={searchTo}
            onChange={(e) => setSearchTo(e.target.value)}
            className="flex-1 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-sm focus:outline-none focus:border-blue-500/50"
          />
          <button
            onClick={handleSearch}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 text-white font-medium flex items-center gap-2 hover:from-blue-500 hover:to-cyan-500"
          >
            <Search className="w-4 h-4" />
            Search
          </button>
        </div>
      </div>

      {/* Results */}
      <div className="space-y-4">
        {filtered.map((t, i) => (
          <motion.div
            key={t.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card border-l-4"
            style={{ borderLeftColor: t.success ? "#10b981" : "#ef4444" }}
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold">{t.from}</span>
                  <span className="text-muted-foreground">→</span>
                  <span className="font-semibold">{t.to}</span>
                </div>
                <span className="text-xs text-muted-foreground">{t.startedAt}</span>
              </div>
              <span
                className={`text-xs px-2 py-0.5 rounded-full ${
                  t.success
                    ? "bg-emerald-500/20 text-emerald-400"
                    : "bg-red-500/20 text-red-400"
                }`}
              >
                {t.success ? "SUCCESS" : "FAILED"}
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3 text-sm">
              <div>
                <span className="text-xs text-muted-foreground">Stabilization</span>
                <p className="font-mono font-medium">{t.stabilizationTime}s</p>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Waste Generated</span>
                <p className="font-mono font-medium">{t.waste} kg</p>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Machine Speed</span>
                <p className="font-mono font-medium">{t.settings.machine_speed} m/min</p>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Dryer Temp</span>
                <p className="font-mono font-medium">{t.settings.dryer_temperature}°C</p>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-accent/30">
              <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                📝 Lessons Learned
              </span>
              <p className="text-sm mt-1">{t.lessons}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
