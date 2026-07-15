"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Bell, AlertTriangle, CheckCircle2, XCircle, Clock } from "lucide-react";

interface Alert {
  id: number;
  priority: "green" | "yellow" | "red";
  title: string;
  message: string;
  reason: string;
  action: string;
  impact: string;
  time: string;
  acknowledged: boolean;
  resolved: boolean;
}

const initialAlerts: Alert[] = [
  {
    id: 1,
    priority: "red",
    title: "Critical GSM Deviation",
    message: "Basis weight at 123.8 GSM — 3.2% above 120 GSM target. Machine speed may need reduction.",
    reason: "Machine speed trending 3.1% above optimal setpoint. Combined with elevated dryer temperature causing excess moisture removal.",
    action: "Reduce machine speed from 785 to 762 m/min. Lower dryer temperature from 128.4 to 124.0°C.",
    impact: "Expected: GSM returns to 120±1 within 2-3 minutes. Estimated 35 kg waste prevention.",
    time: "2 min ago",
    acknowledged: false,
    resolved: false,
  },
  {
    id: 2,
    priority: "yellow",
    title: "Moisture Content Rising",
    message: "Moisture content trending upward — currently 5.8% vs target 5.2%. May affect final GSM.",
    reason: "Dryer section temperature gradually decreasing due to steam pressure fluctuation.",
    action: "Monitor dryer temperature for 5 minutes. If below 124°C, increase steam pressure.",
    impact: "Proactive monitoring prevents GSM drift of 0.5-1.0 GSM.",
    time: "15 min ago",
    acknowledged: true,
    resolved: false,
  },
  {
    id: 3,
    priority: "green",
    title: "Grade Transition Stabilized",
    message: "Grade transition from 80 GSM to 100 GSM successfully stabilized in 198 seconds.",
    reason: "AI-recommended parameter adjustments were applied by operator.",
    action: "No action required. Continue monitoring for 10 minutes.",
    impact: "Transition completed 32% faster than historical average.",
    time: "45 min ago",
    acknowledged: true,
    resolved: true,
  },
  {
    id: 4,
    priority: "yellow",
    title: "Chemical Dosage Variation",
    message: "Chemical dosage oscillating ±8% from setpoint. Retention may be affected.",
    reason: "Possible dosing pump inconsistency or chemical supply variation.",
    action: "Check dosing pump calibration. Verify chemical tank levels.",
    impact: "Prevents basis weight variation of up to 2 GSM.",
    time: "1 hr ago",
    acknowledged: false,
    resolved: false,
  },
  {
    id: 5,
    priority: "green",
    title: "Model Performance Update",
    message: "Basis weight prediction model accuracy: RMSE 0.87, MAE 0.65, R² 0.94. Performance stable.",
    reason: "Weekly model monitoring check completed.",
    action: "No action needed. Model performing within expected parameters.",
    impact: "AI predictions maintain >90% reliability.",
    time: "2 hr ago",
    acknowledged: true,
    resolved: true,
  },
];

export default function AlertsPage() {
  const [alerts, setAlerts] = useState(initialAlerts);
  const [filter, setFilter] = useState<string>("all");

  const filtered = alerts.filter((a) => {
    if (filter === "unacknowledged") return !a.acknowledged;
    if (filter === "active") return !a.resolved;
    return filter === "all" || a.priority === filter;
  });

  const handleAcknowledge = (id: number) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, acknowledged: true } : a))
    );
  };

  const handleResolve = (id: number) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, resolved: true, acknowledged: true } : a))
    );
  };

  const counts = {
    total: alerts.length,
    red: alerts.filter((a) => a.priority === "red").length,
    yellow: alerts.filter((a) => a.priority === "yellow").length,
    green: alerts.filter((a) => a.priority === "green").length,
    unacknowledged: alerts.filter((a) => !a.acknowledged).length,
  };

  return (
    <div className="space-y-8 animate-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Intelligent Alerts</h1>
          <p className="text-muted-foreground mt-1">
            Priority-based alerts with reasons, recommendations, and expected impact
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-sm">
            <span className="status-dot status-red" /> {counts.red} Critical
          </span>
          <span className="flex items-center gap-1.5 text-sm">
            <span className="status-dot status-yellow" /> {counts.yellow} Warning
          </span>
          <span className="flex items-center gap-1.5 text-sm">
            <span className="status-dot status-green" /> {counts.green} Info
          </span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2">
        {[
          { key: "all", label: "All" },
          { key: "red", label: "Critical" },
          { key: "yellow", label: "Warning" },
          { key: "green", label: "Info" },
          { key: "unacknowledged", label: `Unacknowledged (${counts.unacknowledged})` },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              filter === tab.key
                ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                : "bg-accent/30 text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Alerts */}
      <div className="space-y-4">
        {filtered.map((alert, i) => (
          <motion.div
            key={alert.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.08 }}
            className={`glass-card border-l-4 ${
              alert.priority === "red"
                ? "border-red-500"
                : alert.priority === "yellow"
                ? "border-amber-500"
                : "border-emerald-500"
            } ${alert.resolved ? "opacity-60" : ""}`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <span className={`status-dot status-${alert.priority}`} />
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">{alert.title}</h3>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        alert.priority === "red"
                          ? "bg-red-500/20 text-red-400"
                          : alert.priority === "yellow"
                          ? "bg-amber-500/20 text-amber-400"
                          : "bg-emerald-500/20 text-emerald-400"
                      }`}
                    >
                      {alert.priority.toUpperCase()}
                    </span>
                    {alert.resolved && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400">
                        RESOLVED
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground mt-0.5">
                    <Clock className="w-3 h-3" />
                    <span>{alert.time}</span>
                  </div>
                </div>
              </div>
            </div>

            <p className="text-sm mb-3">{alert.message}</p>

            <div className="space-y-2 mb-4">
              <div className="p-2.5 rounded-lg bg-red-500/5 border border-red-500/10">
                <span className="text-xs text-red-400 font-medium">Reason:</span>
                <p className="text-xs text-muted-foreground mt-0.5">{alert.reason}</p>
              </div>
              <div className="p-2.5 rounded-lg bg-blue-500/5 border border-blue-500/10">
                <span className="text-xs text-blue-400 font-medium">Recommended Action:</span>
                <p className="text-xs text-muted-foreground mt-0.5">{alert.action}</p>
              </div>
              <div className="p-2.5 rounded-lg bg-emerald-500/5 border border-emerald-500/10">
                <span className="text-xs text-emerald-400 font-medium">Expected Impact:</span>
                <p className="text-xs text-muted-foreground mt-0.5">{alert.impact}</p>
              </div>
            </div>

            <div className="flex gap-2">
              {!alert.acknowledged && (
                <button
                  onClick={() => handleAcknowledge(alert.id)}
                  className="px-3 py-1.5 rounded-lg bg-blue-500/20 text-blue-400 text-xs font-medium hover:bg-blue-500/30 transition-colors"
                >
                  Acknowledge
                </button>
              )}
              {!alert.resolved && (
                <button
                  onClick={() => handleResolve(alert.id)}
                  className="px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 text-xs font-medium hover:bg-emerald-500/30 transition-colors"
                >
                  Mark Resolved
                </button>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
