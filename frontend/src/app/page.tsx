"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { API_BASE, formatNumber, formatPercent } from "@/lib/utils";
import {
  TrendingUp,
  TrendingDown,
  Gauge,
  Clock,
  ThumbsUp,
  BarChart3,
  AlertTriangle,
  BrainCircuit,
  Zap,
} from "lucide-react";
import dynamic from "next/dynamic";

const TrendChart = dynamic(() => import("@/components/dashboard/TrendChart"), { ssr: false });
const GaugeChart = dynamic(() => import("@/components/dashboard/GaugeChart"), { ssr: false });

interface KPIData {
  estimated_waste_reduced_kg: number;
  paper_saved_kg: number;
  production_efficiency: number;
  average_stabilization_time: number;
  operator_acceptance_rate: number;
  recommendation_success_rate: number;
  total_predictions: number;
  total_recommendations: number;
  total_alerts: number;
  average_confidence: number;
}

export default function DashboardPage() {
  const [kpi, setKpi] = useState<KPIData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/analytics/kpi`)
      .then((r) => r.json())
      .then((data) => {
        setKpi(data);
        setLoading(false);
      })
      .catch(() => {
        // Fallback demo data
        setKpi({
          estimated_waste_reduced_kg: 2847.5,
          paper_saved_kg: 2420.4,
          production_efficiency: 93.2,
          average_stabilization_time: 245.6,
          operator_acceptance_rate: 87.3,
          recommendation_success_rate: 82.1,
          total_predictions: 12847,
          total_recommendations: 3842,
          total_alerts: 562,
          average_confidence: 0.86,
        });
        setLoading(false);
      });
  }, []);

  const kpiCards = kpi
    ? [
        {
          label: "Production Efficiency",
          value: formatPercent(kpi.production_efficiency),
          icon: Gauge,
          trending: "up",
          color: "text-emerald-400",
          bg: "from-emerald-500/20 to-emerald-500/5",
        },
        {
          label: "Waste Reduced",
          value: `${formatNumber(kpi.estimated_waste_reduced_kg)} kg`,
          icon: TrendingDown,
          trending: "up",
          color: "text-emerald-400",
          bg: "from-green-500/20 to-green-500/5",
        },
        {
          label: "Avg Stabilization Time",
          value: `${formatNumber(kpi.average_stabilization_time)}s`,
          icon: Clock,
          trending: "down",
          color: "text-blue-400",
          bg: "from-blue-500/20 to-blue-500/5",
        },
        {
          label: "Operator Acceptance",
          value: formatPercent(kpi.operator_acceptance_rate),
          icon: ThumbsUp,
          trending: "up",
          color: "text-cyan-400",
          bg: "from-cyan-500/20 to-cyan-500/5",
        },
        {
          label: "AI Predictions",
          value: kpi.total_predictions.toLocaleString(),
          icon: BrainCircuit,
          trending: "neutral",
          color: "text-violet-400",
          bg: "from-violet-500/20 to-violet-500/5",
        },
        {
          label: "Active Alerts",
          value: kpi.total_alerts.toString(),
          icon: AlertTriangle,
          trending: "neutral",
          color: "text-amber-400",
          bg: "from-amber-500/20 to-amber-500/5",
        },
      ]
    : [];

  return (
    <div className="space-y-8 animate-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          Production Command Center
        </h1>
        <p className="text-muted-foreground mt-1">
          Real-time overview of paper machine operations and AI-driven insights
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {loading
          ? Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="glass-card animate-pulse">
                <div className="h-4 w-20 bg-white/10 rounded mb-3" />
                <div className="h-8 w-24 bg-white/10 rounded" />
              </div>
            ))
          : kpiCards.map((card, i) => (
              <motion.div
                key={card.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
                className="kpi-widget"
              >
                <div className="flex items-center justify-between">
                  <span className="kpi-label">{card.label}</span>
                  <card.icon className={`w-5 h-5 ${card.color}`} />
                </div>
                <span className={`kpi-value ${card.color}`}>{card.value}</span>
                <div className={`h-1 rounded-full bg-gradient-to-r ${card.bg}`} />
              </motion.div>
            ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart */}
        <div className="chart-container lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Basis Weight Trend (Last 24 Hours)</h3>
            <span className="text-xs text-muted-foreground bg-accent/50 px-2 py-1 rounded-full">
              PM-01 • 120 GSM Target
            </span>
          </div>
          <TrendChart />
        </div>

        {/* Gauge */}
        <div className="chart-container flex flex-col items-center justify-center">
          <h3 className="text-lg font-semibold mb-2">Real-Time GSM</h3>
          <GaugeChart value={119.7} min={117} max={123} target={120} />
          <div className="flex gap-4 mt-4">
            <div className="text-center">
              <span className="text-xs text-muted-foreground block">Current</span>
              <span className="text-lg font-bold text-emerald-400">119.7</span>
            </div>
            <div className="text-center">
              <span className="text-xs text-muted-foreground block">Target</span>
              <span className="text-lg font-bold">120.0</span>
            </div>
            <div className="text-center">
              <span className="text-xs text-muted-foreground block">Deviation</span>
              <span className="text-lg font-bold text-amber-400">-0.25%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Predictions */}
        <div className="glass-card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BrainCircuit className="w-5 h-5 text-blue-400" />
            Recent AI Predictions
          </h3>
          <div className="space-y-3">
            {[
              { gsm: 119.7, risk: "green", time: "2 min ago", confidence: 0.92 },
              { gsm: 121.3, risk: "yellow", time: "17 min ago", confidence: 0.84 },
              { gsm: 118.2, risk: "green", time: "32 min ago", confidence: 0.91 },
              { gsm: 122.8, risk: "red", time: "47 min ago", confidence: 0.72 },
              { gsm: 120.1, risk: "green", time: "1 hr ago", confidence: 0.95 },
            ].map((pred, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-accent/30">
                <div className="flex items-center gap-3">
                  <span className={`status-dot status-${pred.risk}`} />
                  <span className="font-mono font-medium">{pred.gsm} GSM</span>
                </div>
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <span>{(pred.confidence * 100).toFixed(0)}% confidence</span>
                  <span>{pred.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="glass-card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            Recent Alerts
          </h3>
          <div className="space-y-3">
            {[
              { priority: "red", title: "GSM Deviation Detected", msg: "Basis weight 2.5% above target at PM-01" },
              { priority: "yellow", title: "Moisture Content Rising", msg: "Moisture trending upward — check dryer temp" },
              { priority: "green", title: "Transition Stabilized", msg: "Grade transition 80→120 GSM stabilized in 4.2 min" },
              { priority: "yellow", title: "Speed Variation", msg: "Machine speed fluctuating ±3% from setpoint" },
            ].map((alert, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-accent/30">
                <span className={`status-dot status-${alert.priority} mt-0.5`} />
                <div>
                  <span className="font-medium text-sm">{alert.title}</span>
                  <p className="text-xs text-muted-foreground mt-0.5">{alert.msg}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
