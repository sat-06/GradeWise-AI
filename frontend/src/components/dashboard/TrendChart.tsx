"use client";

import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";

const generateTrendData = () => {
  const data = [];
  const now = new Date();
  for (let i = 24 * 60; i >= 0; i -= 10) {
    const time = new Date(now.getTime() - i * 60000);
    data.push({
      time: time.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
      basisWeight: 120 + Math.sin(i / 30) * 1.5 + Math.random() * 0.8 - 0.4,
      target: 120,
      upperLimit: 123,
      lowerLimit: 117,
    });
  }
  return data;
};

export default function TrendChart() {
  const data = generateTrendData();

  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <defs>
          <linearGradient id="gsmGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="targetGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#10b981" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis
          dataKey="time"
          stroke="rgba(255,255,255,0.3)"
          tick={{ fontSize: 11 }}
          interval={Math.floor(data.length / 8)}
        />
        <YAxis
          stroke="rgba(255,255,255,0.3)"
          tick={{ fontSize: 11 }}
          domain={[115, 125]}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "rgba(15, 23, 42, 0.95)",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: "12px",
            backdropFilter: "blur(12px)",
            color: "#fff",
          }}
        />
        <Area
          type="monotone"
          dataKey="upperLimit"
          stroke="rgba(255,255,255,0.05)"
          fill="none"
          strokeDasharray="5 5"
        />
        <Area
          type="monotone"
          dataKey="lowerLimit"
          stroke="rgba(255,255,255,0.05)"
          fill="none"
          strokeDasharray="5 5"
        />
        <Area
          type="monotone"
          dataKey="target"
          stroke="#10b981"
          fill="url(#targetGradient)"
          strokeWidth={1.5}
          strokeDasharray="4 4"
        />
        <Area
          type="monotone"
          dataKey="basisWeight"
          stroke="#3b82f6"
          fill="url(#gsmGradient)"
          strokeWidth={2.5}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
