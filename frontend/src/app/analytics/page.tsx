"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { BarChart3, TrendingUp, TrendingDown, DollarSign, Package, Gauge } from "lucide-react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, AreaChart, Area } from "recharts";
import { API_BASE } from "@/lib/utils";

const kpiData = {
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
};

const weeklyData = [
  { day: "Mon", efficiency: 91, waste: 45, predictions: 320 },
  { day: "Tue", efficiency: 92, waste: 42, predictions: 335 },
  { day: "Wed", efficiency: 94, waste: 38, predictions: 310 },
  { day: "Thu", efficiency: 93, waste: 40, predictions: 345 },
  { day: "Fri", efficiency: 95, waste: 35, predictions: 330 },
  { day: "Sat", efficiency: 94, waste: 37, predictions: 315 },
  { day: "Sun", efficiency: 96, waste: 32, predictions: 340 },
];

const monthlySavings = [
  { month: "Jan", savings: 18500, waste_reduced: 2200 },
  { month: "Feb", savings: 19200, waste_reduced: 2350 },
  { month: "Mar", savings: 21400, waste_reduced: 2580 },
  { month: "Apr", savings: 23100, waste_reduced: 2750 },
  { month: "May", savings: 24800, waste_reduced: 2840 },
  { month: "Jun", savings: 26100, waste_reduced: 2970 },
  { month: "Jul", savings: 28700, waste_reduced: 3120 },
];

export default function AnalyticsPage() {
  return (
    <div className="space-y-8 animate-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Business Analytics</h1>
        <p className="text-muted-foreground mt-1">
          Business intelligence metrics — measure the financial and operational impact
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card">
          <DollarSign className="w-5 h-5 text-emerald-400 mb-2" />
          <span className="kpi-label">Cost Savings (MTD)</span>
          <span className="text-2xl font-bold text-emerald-400">$28,700</span>
          <span className="text-xs text-emerald-400/60 mt-1 block">↑ 12.4% vs last month</span>
        </div>
        <div className="glass-card">
          <Package className="w-5 h-5 text-blue-400 mb-2" />
          <span className="kpi-label">Paper Saved</span>
          <span className="text-2xl font-bold">{kpiData.paper_saved_kg.toLocaleString()} kg</span>
          <span className="text-xs text-muted-foreground mt-1 block">Cumulative</span>
        </div>
        <div className="glass-card">
          <Gauge className="w-5 h-5 text-purple-400 mb-2" />
          <span className="kpi-label">Efficiency</span>
          <span className="text-2xl font-bold">{kpiData.production_efficiency}%</span>
          <span className="text-xs text-emerald-400/60 mt-1 block">↑ 2.1% improvement</span>
        </div>
        <div className="glass-card">
          <TrendingDown className="w-5 h-5 text-amber-400 mb-2" />
          <span className="kpi-label">Avg Stabilization</span>
          <span className="text-2xl font-bold">{kpiData.average_stabilization_time}s</span>
          <span className="text-xs text-emerald-400/60 mt-1 block">↓ 15% faster</span>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Efficiency */}
        <div className="chart-container">
          <h3 className="text-lg font-semibold mb-4">Weekly Production Efficiency</h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="day" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11 }} />
              <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11 }} domain={[88, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(15, 23, 42, 0.95)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "12px",
                  color: "#fff",
                }}
              />
              <defs>
                <linearGradient id="effGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area type="monotone" dataKey="efficiency" stroke="#10b981" fill="url(#effGradient)" strokeWidth={2.5} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Monthly Savings */}
        <div className="chart-container">
          <h3 className="text-lg font-semibold mb-4">Monthly Cost Savings</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={monthlySavings}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11 }} />
              <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(15, 23, 42, 0.95)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "12px",
                  color: "#fff",
                }}
              />
              <Line
                type="monotone"
                dataKey="savings"
                stroke="#3b82f6"
                strokeWidth={2.5}
                dot={{ fill: "#3b82f6", r: 4 }}
                name="Cost Savings ($)"
              />
              <Line
                type="monotone"
                dataKey="waste_reduced"
                stroke="#10b981"
                strokeWidth={2.5}
                dot={{ fill: "#10b981", r: 4 }}
                name="Waste Reduced (kg)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Operator Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card text-center">
          <h4 className="text-sm text-muted-foreground mb-2">Operator Acceptance Rate</h4>
          <div className="relative w-24 h-24 mx-auto mb-2">
            <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="8" />
              <circle
                cx="50" cy="50" r="42" fill="none" stroke="#3b82f6" strokeWidth="8"
                strokeDasharray={`${87.3 * 2.64} 264`}
                strokeLinecap="round"
              />
            </svg>
            <span className="absolute inset-0 flex items-center justify-center text-lg font-bold">87.3%</span>
          </div>
        </div>
        <div className="glass-card text-center">
          <h4 className="text-sm text-muted-foreground mb-2">Recommendation Success</h4>
          <div className="relative w-24 h-24 mx-auto mb-2">
            <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="8" />
              <circle
                cx="50" cy="50" r="42" fill="none" stroke="#10b981" strokeWidth="8"
                strokeDasharray={`${82.1 * 2.64} 264`}
                strokeLinecap="round"
              />
            </svg>
            <span className="absolute inset-0 flex items-center justify-center text-lg font-bold">82.1%</span>
          </div>
        </div>
        <div className="glass-card text-center">
          <h4 className="text-sm text-muted-foreground mb-2">AI Prediction Confidence</h4>
          <div className="relative w-24 h-24 mx-auto mb-2">
            <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="8" />
              <circle
                cx="50" cy="50" r="42" fill="none" stroke="#8b5cf6" strokeWidth="8"
                strokeDasharray={`${86 * 2.64} 264`}
                strokeLinecap="round"
              />
            </svg>
            <span className="absolute inset-0 flex items-center justify-center text-lg font-bold">86%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
