"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Activity,
  Gauge,
  Thermometer,
  Droplets,
  Beaker,
  Waves,
  Zap,
} from "lucide-react";
import dynamic from "next/dynamic";

const TrendChart = dynamic(() => import("@/components/dashboard/TrendChart"), { ssr: false });

interface SensorReading {
  basis_weight: number;
  machine_speed: number;
  headbox_pressure: number;
  dryer_temperature: number;
  moisture_content: number;
  chemical_dosage: number;
  flow_rate: number;
}

const defaultReading: SensorReading = {
  basis_weight: 119.7,
  machine_speed: 785,
  headbox_pressure: 2.65,
  dryer_temperature: 128.4,
  moisture_content: 5.2,
  chemical_dosage: 1.92,
  flow_rate: 2680,
};

export default function MonitoringPage() {
  const [reading, setReading] = useState<SensorReading>(defaultReading);

  useEffect(() => {
    const interval = setInterval(() => {
      setReading((prev) => ({
        basis_weight: prev.basis_weight + (Math.random() - 0.5) * 0.3,
        machine_speed: prev.machine_speed + (Math.random() - 0.5) * 5,
        headbox_pressure: prev.headbox_pressure + (Math.random() - 0.5) * 0.02,
        dryer_temperature: prev.dryer_temperature + (Math.random() - 0.5) * 0.5,
        moisture_content: Math.max(3, Math.min(9, prev.moisture_content + (Math.random() - 0.5) * 0.1)),
        chemical_dosage: prev.chemical_dosage + (Math.random() - 0.5) * 0.02,
        flow_rate: prev.flow_rate + (Math.random() - 0.5) * 10,
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const sensors = [
    { label: "Machine Speed", value: reading.machine_speed, unit: "m/min", icon: Gauge, color: "text-blue-400", min: 400, max: 1200 },
    { label: "Headbox Pressure", value: reading.headbox_pressure, unit: "bar", icon: Zap, color: "text-cyan-400", min: 1.5, max: 4.5 },
    { label: "Dryer Temperature", value: reading.dryer_temperature, unit: "°C", icon: Thermometer, color: "text-orange-400", min: 80, max: 160 },
    { label: "Moisture Content", value: reading.moisture_content, unit: "%", icon: Droplets, color: "text-blue-300", min: 3, max: 9 },
    { label: "Chemical Dosage", value: reading.chemical_dosage, unit: "kg/ton", icon: Beaker, color: "text-purple-400", min: 0.5, max: 3.5 },
    { label: "Flow Rate", value: reading.flow_rate, unit: "L/min", icon: Waves, color: "text-teal-400", min: 1500, max: 4000 },
  ];

  return (
    <div className="space-y-8 animate-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Live Machine Monitoring</h1>
        <p className="text-muted-foreground mt-1">
          Real-time sensor data from Paper Machine PM-01
        </p>
      </div>

      {/* Main GSM Display */}
      <div className="glass-card text-center py-8 border border-blue-500/20">
        <div className="text-sm text-muted-foreground uppercase tracking-wider mb-2">
          Current Basis Weight
        </div>
        <motion.div
          key={reading.basis_weight.toFixed(1)}
          initial={{ scale: 1.1 }}
          animate={{ scale: 1 }}
          className="text-7xl font-bold bg-gradient-to-r from-blue-400 via-cyan-400 to-emerald-400 bg-clip-text text-transparent tracking-tight"
        >
          {reading.basis_weight.toFixed(1)}
        </motion.div>
        <div className="text-sm text-muted-foreground mt-1">GSM • Target: 120.0</div>
        <div className="mt-4 flex items-center justify-center gap-3">
          <span className="status-dot status-green" />
          <span className="text-sm text-emerald-400">Within tolerance (±3 GSM)</span>
        </div>
      </div>

      {/* Sensor Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sensors.map((sensor, i) => (
          <motion.div
            key={sensor.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="glass-card"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-muted-foreground">{sensor.label}</span>
              <sensor.icon className={`w-5 h-5 ${sensor.color}`} />
            </div>
            <div className="flex items-end gap-2">
              <span className="text-3xl font-bold tabular-nums">
                {sensor.value.toFixed(sensor.unit === "bar" || sensor.unit === "%" ? 2 : 0)}
              </span>
              <span className="text-sm text-muted-foreground mb-1">{sensor.unit}</span>
            </div>
            {/* Mini progress bar */}
            <div className="mt-3 h-1.5 rounded-full bg-white/5 overflow-hidden">
              <motion.div
                className={`h-full rounded-full bg-gradient-to-r ${sensor.color.replace("text-", "from-")}`}
                animate={{
                  width: `${((sensor.value - sensor.min) / (sensor.max - sensor.min)) * 100}%`,
                }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Trend */}
      <div className="chart-container">
        <h3 className="text-lg font-semibold mb-4">Live Trend</h3>
        <TrendChart />
      </div>
    </div>
  );
}
