"use client";

import { motion } from "framer-motion";
import { Sparkles, Lightbulb, TrendingUp, AlertTriangle } from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";

const importanceData = [
  { feature: "Machine Speed", importance: 0.284 },
  { feature: "Dryer Temp", importance: 0.218 },
  { feature: "Headbox Pressure", importance: 0.176 },
  { feature: "Moisture Content", importance: 0.152 },
  { feature: "Chemical Dosage", importance: 0.098 },
  { feature: "Flow Rate", importance: 0.072 },
];

const contributions = [
  { parameter: "Machine Speed", current: 785, optimal: 762, impact: -0.35, explanation: "Speed too high → thinner paper" },
  { parameter: "Dryer Temperature", current: 128.4, optimal: 124.0, impact: -0.22, explanation: "Excessive drying → lower GSM" },
  { parameter: "Headbox Pressure", current: 2.65, optimal: 2.58, impact: +0.12, explanation: "Slightly under optimal" },
  { parameter: "Moisture Content", current: 5.2, optimal: 5.6, impact: +0.08, explanation: "Slightly low moisture" },
];

export default function ExplainabilityPage() {
  return (
    <div className="space-y-8 animate-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Explainable AI</h1>
        <p className="text-muted-foreground mt-1">
          Understand why each prediction was made — every decision is transparent
        </p>
      </div>

      {/* Explanation Summary */}
      <div className="glass-card border-l-4 border-blue-500">
        <div className="flex items-start gap-3">
          <Lightbulb className="w-6 h-6 text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold">Why was this prediction made?</h3>
            <p className="text-sm text-muted-foreground mt-1">
              The AI predicted a Basis Weight of 118.9 GSM (1.1 GSM below target) because
              Machine Speed is 2.6% above optimal range, causing thinner paper deposition.
              Dryer Temperature is also 3.5% above optimal, removing excess moisture.
              These two factors contribute 50.2% of the total deviation.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Feature Importance Chart */}
        <div className="chart-container">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-400" />
            Feature Importance
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={importanceData} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
              <XAxis type="number" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11 }} />
              <YAxis
                dataKey="feature"
                type="category"
                stroke="rgba(255,255,255,0.3)"
                tick={{ fontSize: 11 }}
                width={120}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(15, 23, 42, 0.95)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "12px",
                  color: "#fff",
                }}
              />
              <Bar dataKey="importance" fill="url(#barGradient)" radius={[0, 4, 4, 0]} barSize={24} />
              <defs>
                <linearGradient id="barGradient" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#06b6d4" />
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Parameter Contributions */}
        <div className="glass-card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-400" />
            Parameter Contributions
          </h3>
          <div className="space-y-3">
            {contributions.map((param, i) => (
              <motion.div
                key={param.parameter}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="p-3 rounded-xl bg-accent/30"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium">{param.parameter}</span>
                  <span className={`text-xs font-mono ${param.impact < 0 ? "text-red-400" : "text-emerald-400"}`}>
                    {param.impact > 0 ? "+" : ""}{param.impact.toFixed(2)} GSM
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>Current: <span className="font-mono text-foreground">{param.current}</span></span>
                  <span>→</span>
                  <span>Optimal: <span className="font-mono text-emerald-400">{param.optimal}</span></span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">{param.explanation}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Root Cause Analysis */}
      <div className="glass-card">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          Root Cause Analysis
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20">
            <span className="text-xs text-red-400 uppercase tracking-wider font-medium">Primary Cause</span>
            <p className="text-sm mt-1 font-medium">Machine Speed</p>
            <p className="text-xs text-muted-foreground mt-1">
              785 m/min exceeds optimal 762 m/min. Each 1 m/min increase reduces GSM by ~0.015.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20">
            <span className="text-xs text-amber-400 uppercase tracking-wider font-medium">Secondary Cause</span>
            <p className="text-sm mt-1 font-medium">Dryer Temperature</p>
            <p className="text-xs text-muted-foreground mt-1">
              128.4°C vs optimal 124.0°C. Excess heat removes 0.15 GSM per degree.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20">
            <span className="text-xs text-blue-400 uppercase tracking-wider font-medium">Tertiary Factor</span>
            <p className="text-sm mt-1 font-medium">Headbox Pressure</p>
            <p className="text-xs text-muted-foreground mt-1">
              Minor 0.07 bar below optimal. Small impact on fiber distribution.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
