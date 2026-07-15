"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { BrainCircuit, AlertTriangle, TrendingUp, Zap } from "lucide-react";

export default function PredictionsPage() {
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<any>(null);

  const [params, setParams] = useState({
    machine_speed: 785,
    headbox_pressure: 2.65,
    dryer_temperature: 128.4,
    moisture_content: 5.2,
    chemical_dosage: 1.92,
    flow_rate: 2680,
  });

  const handlePredict = async () => {
    setLoading(true);
    // Simulate API call
    await new Promise((r) => setTimeout(r, 1500));

    const target = 120;
    const predicted =
      target +
      -0.015 * (params.machine_speed - 800) +
      4.0 * (params.headbox_pressure - 2.5) +
      -0.15 * (params.dryer_temperature - 120) +
      0.8 * (params.moisture_content - 5.5) +
      2.5 * (params.chemical_dosage - 1.8) +
      0.0008 * (params.flow_rate - 2500) +
      (Math.random() - 0.5) * 1.2;

    const dev = Math.abs(predicted - target) / target * 100;
    const risk = dev < 2 ? "green" : dev < 5 ? "yellow" : "red";
    const confidence = dev < 2 ? 0.93 : dev < 5 ? 0.82 : 0.65;

    setPrediction({
      predicted_basis_weight: predicted,
      confidence_score: confidence,
      risk_level: risk,
      deviation_percentage: dev,
      estimated_stabilization_time: max(60, dev * 120),
      feature_importance: {
        machine_speed: abs(-0.015 * (params.machine_speed - 800)),
        headbox_pressure: abs(4.0 * (params.headbox_pressure - 2.5)),
        dryer_temperature: abs(-0.15 * (params.dryer_temperature - 120)),
        moisture_content: abs(0.8 * (params.moisture_content - 5.5)),
        chemical_dosage: abs(2.5 * (params.chemical_dosage - 1.8)),
        flow_rate: abs(0.0008 * (params.flow_rate - 2500)),
      },
      root_cause: `Primary deviation driver identified: ${
        Object.entries({
          machine_speed: abs(-0.015 * (params.machine_speed - 800)),
          headbox_pressure: abs(4.0 * (params.headbox_pressure - 2.5)),
          dryer_temperature: abs(-0.15 * (params.dryer_temperature - 120)),
        }).sort((a, b) => b[1] - a[1])[0][0]
      }`,
      decision_explanation:
        dev < 2
          ? "Parameters within optimal range. No corrective action needed."
          : `Predicted deviation of ${dev.toFixed(1)}% ${predicted > target ? "above" : "below"} target. Corrective action recommended.`,
    });
    setLoading(false);
  };

  return (
    <div className="space-y-8 animate-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">AI Prediction Center</h1>
        <p className="text-muted-foreground mt-1">
          Generate AI predictions for future basis weight and deviation risk
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Parameters */}
        <div className="glass-card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-blue-400" />
            Current Machine Parameters
          </h3>
          <div className="space-y-4">
            {[
              { key: "machine_speed", label: "Machine Speed", unit: "m/min", min: 400, max: 1200 },
              { key: "headbox_pressure", label: "Headbox Pressure", unit: "bar", min: 1.5, max: 4.5 },
              { key: "dryer_temperature", label: "Dryer Temperature", unit: "°C", min: 80, max: 160 },
              { key: "moisture_content", label: "Moisture Content", unit: "%", min: 3, max: 9 },
              { key: "chemical_dosage", label: "Chemical Dosage", unit: "kg/ton", min: 0.5, max: 3.5 },
              { key: "flow_rate", label: "Flow Rate", unit: "L/min", min: 1500, max: 4000 },
            ].map((param) => (
              <div key={param.key}>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="text-muted-foreground">{param.label}</span>
                  <span className="font-mono font-medium">
                    {(params as any)[param.key].toFixed(param.key === "flow_rate" || param.key === "machine_speed" ? 0 : 2)} {param.unit}
                  </span>
                </div>
                <input
                  type="range"
                  min={param.min}
                  max={param.max}
                  step={(param.max - param.min) / 100}
                  value={(params as any)[param.key]}
                  onChange={(e) =>
                    setParams({ ...params, [param.key]: parseFloat(e.target.value) })
                  }
                  className="w-full accent-primary"
                />
              </div>
            ))}
          </div>
          <button
            onClick={handlePredict}
            disabled={loading}
            className="w-full mt-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 text-white font-semibold hover:from-blue-500 hover:to-cyan-500 transition-all duration-300 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <BrainCircuit className="w-5 h-5" />
            {loading ? "Analyzing..." : "Generate AI Prediction"}
          </button>
        </div>

        {/* Prediction Result */}
        <div className="glass-card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            Prediction Result
          </h3>

          {loading ? (
            <div className="space-y-4 animate-pulse">
              <div className="h-16 bg-white/10 rounded-xl" />
              <div className="h-32 bg-white/10 rounded-xl" />
              <div className="h-24 bg-white/10 rounded-xl" />
            </div>
          ) : prediction ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="space-y-4"
            >
              {/* Risk Level */}
              <div
                className={`p-4 rounded-xl border ${
                  prediction.risk_level === "green"
                    ? "bg-emerald-500/10 border-emerald-500/30"
                    : prediction.risk_level === "yellow"
                    ? "bg-amber-500/10 border-amber-500/30"
                    : "bg-red-500/10 border-red-500/30"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Predicted Basis Weight</span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full ${
                      prediction.risk_level === "green"
                        ? "bg-emerald-500/20 text-emerald-400"
                        : prediction.risk_level === "yellow"
                        ? "bg-amber-500/20 text-amber-400"
                        : "bg-red-500/20 text-red-400"
                    }`}
                  >
                    {prediction.risk_level.toUpperCase()}
                  </span>
                </div>
                <div className="text-4xl font-bold mt-1">
                  {prediction.predicted_basis_weight.toFixed(1)} GSM
                </div>
                <div className="flex gap-4 mt-2 text-xs text-muted-foreground">
                  <span>Deviation: {prediction.deviation_percentage.toFixed(1)}%</span>
                  <span>Confidence: {(prediction.confidence_score * 100).toFixed(0)}%</span>
                  <span>Est. Stabilization: {prediction.estimated_stabilization_time.toFixed(0)}s</span>
                </div>
              </div>

              {/* Feature Importance */}
              <div>
                <h4 className="text-sm font-medium mb-2">Feature Importance</h4>
                {Object.entries(prediction.feature_importance)
                  .sort((a: any, b: any) => b[1] - a[1])
                  .slice(0, 4)
                  .map(([key, val]: any) => (
                    <div key={key} className="flex items-center gap-2 mb-1.5">
                      <span className="text-xs text-muted-foreground w-36 truncate">{key}</span>
                      <div className="flex-1 h-2 rounded-full bg-white/5">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-500"
                          style={{
                            width: `${(val / Math.max(...Object.values(prediction.feature_importance))) * 100}%`,
                          }}
                        />
                      </div>
                      <span className="text-xs font-mono w-12 text-right">{val.toFixed(4)}</span>
                    </div>
                  ))}
              </div>

              {/* Root Cause */}
              <div className="p-3 rounded-xl bg-accent/30">
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Root Cause</span>
                <p className="text-sm mt-1">{prediction.root_cause}</p>
              </div>

              {/* Decision */}
              <div className="p-3 rounded-xl bg-accent/30">
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Decision</span>
                <p className="text-sm mt-1">{prediction.decision_explanation}</p>
              </div>
            </motion.div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
              <BrainCircuit className="w-16 h-16 mb-4 opacity-30" />
              <p>Adjust parameters and click "Generate AI Prediction"</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function abs(n: number) {
  return Math.abs(n);
}
function max(a: number, b: number) {
  return Math.max(a, b);
}
