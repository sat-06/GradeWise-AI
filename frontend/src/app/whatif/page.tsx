"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { SlidersHorizontal, Play, RotateCcw } from "lucide-react";

interface ParamState {
  value: number;
  min: number;
  max: number;
  unit: string;
  optimal: number;
  step: number;
}

export default function WhatIfPage() {
  const [params, setParams] = useState<Record<string, ParamState>>({
    machine_speed: { value: 785, min: 400, max: 1200, unit: "m/min", optimal: 762, step: 1 },
    headbox_pressure: { value: 2.65, min: 1.5, max: 4.5, unit: "bar", optimal: 2.70, step: 0.01 },
    dryer_temperature: { value: 128.4, min: 80, max: 160, unit: "°C", optimal: 124.0, step: 0.1 },
    moisture_content: { value: 5.2, min: 3.0, max: 9.0, unit: "%", optimal: 5.6, step: 0.1 },
    chemical_dosage: { value: 1.92, min: 0.5, max: 3.5, unit: "kg/ton", optimal: 1.85, step: 0.01 },
    flow_rate: { value: 2680, min: 1500, max: 4000, unit: "L/min", optimal: 2720, step: 1 },
  });

  const [result, setResult] = useState<any>(null);

  const targetGSM = 120;

  const handleSimulate = () => {
    const predicted =
      targetGSM +
      -0.015 * (params.machine_speed.value - 762) +
      4.0 * (params.headbox_pressure.value - 2.70) +
      -0.15 * (params.dryer_temperature.value - 124.0) +
      0.8 * (params.moisture_content.value - 5.6) +
      2.5 * (params.chemical_dosage.value - 1.85) +
      0.0008 * (params.flow_rate.value - 2720);

    const dev = Math.abs(predicted - targetGSM) / targetGSM * 100;
    const risk = dev < 2 ? "green" : dev < 5 ? "yellow" : "red";
    const waste = Math.max(0, (5 - dev) * 5.2);

    setResult({
      predicted_basis_weight: predicted,
      risk_level: risk,
      confidence: dev < 2 ? 0.92 : dev < 5 ? 0.80 : 0.62,
      deviation_from_target: dev,
      estimated_waste_reduction: waste,
      production_impact: dev < 1 ? "✅ Minimal impact" : dev < 3 ? "🟡 Moderate impact" : "🔴 Significant impact",
    });
  };

  const handleReset = () => {
    setParams((prev) => {
      const reset: Record<string, ParamState> = {};
      Object.entries(prev).forEach(([key, p]) => {
        reset[key] = { ...p, value: p.optimal };
      });
      return reset;
    });
    setResult(null);
  };

  return (
    <div className="space-y-8 animate-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">What-If Simulator</h1>
        <p className="text-muted-foreground mt-1">
          Digital twin simulation — adjust parameters and instantly see the predicted impact
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Parameter Sliders */}
        <div className="glass-card lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <SlidersHorizontal className="w-5 h-5 text-blue-400" />
              Machine Parameters
            </h3>
            <div className="flex gap-2">
              <button
                onClick={handleReset}
                className="px-3 py-1.5 rounded-lg bg-accent/50 text-muted-foreground hover:text-foreground transition-colors text-sm flex items-center gap-1.5"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Reset
              </button>
              <button
                onClick={handleSimulate}
                className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 text-white text-sm font-medium flex items-center gap-1.5 hover:from-blue-500 hover:to-cyan-500 transition-colors"
              >
                <Play className="w-3.5 h-3.5" />
                Simulate
              </button>
            </div>
          </div>

          <div className="space-y-5">
            {Object.entries(params).map(([key, param]) => {
              const deviation = ((param.value - param.optimal) / param.optimal * 100);
              const isDev = Math.abs(deviation) > 2;
              return (
                <div key={key}>
                  <div className="flex justify-between items-end mb-1.5">
                    <span className="text-sm text-muted-foreground capitalize">
                      {key.replace(/_/g, " ")}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className={`font-mono font-medium ${isDev ? "text-amber-400" : "text-emerald-400"}`}>
                        {param.value.toFixed(param.step < 1 ? 2 : 0)} {param.unit}
                      </span>
                      {isDev && (
                        <span className={`text-xs ${deviation > 0 ? "text-red-400" : "text-blue-400"}`}>
                          ({deviation > 0 ? "+" : ""}{deviation.toFixed(1)}%)
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="relative">
                    <input
                      type="range"
                      min={param.min}
                      max={param.max}
                      step={param.step * 10}
                      value={param.value}
                      onChange={(e) =>
                        setParams({
                          ...params,
                          [key]: { ...param, value: parseFloat(e.target.value) },
                        })
                      }
                      className="w-full accent-primary"
                    />
                    {/* Optimal marker */}
                    <div
                      className="absolute top-1/2 -translate-y-1/2 w-0.5 h-4 bg-emerald-400 rounded-full"
                      style={{
                        left: `${((param.optimal - param.min) / (param.max - param.min)) * 100}%`,
                      }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-muted-foreground mt-0.5">
                    <span>{param.min}</span>
                    <span className="text-emerald-400/60">optimal: {param.optimal}</span>
                    <span>{param.max}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Simulation Result */}
        <div className="glass-card">
          <h3 className="text-lg font-semibold mb-4">Simulation Result</h3>

          {result ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="space-y-4"
            >
              <div className={`p-4 rounded-xl border ${
                result.risk_level === "green"
                  ? "bg-emerald-500/10 border-emerald-500/30"
                  : result.risk_level === "yellow"
                  ? "bg-amber-500/10 border-amber-500/30"
                  : "bg-red-500/10 border-red-500/30"
              }`}>
                <span className="text-xs text-muted-foreground">Predicted Basis Weight</span>
                <div className="text-4xl font-bold mt-1">
                  {result.predicted_basis_weight.toFixed(1)} GSM
                </div>
                <span className={`text-xs ${
                  result.risk_level === "green" ? "text-emerald-400" :
                  result.risk_level === "yellow" ? "text-amber-400" : "text-red-400"
                }`}>
                  {result.risk_level.toUpperCase()} RISK
                </span>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Deviation</span>
                  <span className="font-mono">{result.deviation_from_target.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Confidence</span>
                  <span className="font-mono">{(result.confidence * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Waste Reduction</span>
                  <span className="font-mono text-emerald-400">{result.estimated_waste_reduction.toFixed(1)} kg</span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-accent/30">
                <p className="text-sm">{result.production_impact}</p>
              </div>
            </motion.div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
              <SlidersHorizontal className="w-16 h-16 mb-4 opacity-30" />
              <p className="text-center">Adjust parameters and click "Simulate"</p>
              <p className="text-xs mt-1 text-center">
                See the predicted impact before making actual changes
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
