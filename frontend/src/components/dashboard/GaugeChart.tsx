"use client";

import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

interface GaugeChartProps {
  value: number;
  min: number;
  max: number;
  target: number;
}

export default function GaugeChart({ value, min, max, target }: GaugeChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const size = 200;
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;
    ctx.scale(dpr, dpr);

    const cx = size / 2;
    const cy = size / 1.6;
    const radius = 100;
    const startAngle = Math.PI * 0.75;
    const endAngle = Math.PI * 2.25;

    // Background arc
    ctx.beginPath();
    ctx.arc(cx, cy, radius, startAngle, endAngle);
    ctx.strokeStyle = "rgba(255,255,255,0.08)";
    ctx.lineWidth = 18;
    ctx.stroke();

    // Value arc
    const valueAngle = startAngle + ((value - min) / (max - min)) * (endAngle - startAngle);

    // Gradient for the arc
    const gradient = ctx.createLinearGradient(0, 0, size, size);
    gradient.addColorStop(0, "#3b82f6");
    gradient.addColorStop(0.5, "#10b981");
    gradient.addColorStop(1, "#ef4444");

    ctx.beginPath();
    ctx.arc(cx, cy, radius, startAngle, valueAngle);
    ctx.strokeStyle = value >= min && value <= max ? gradient : "#ef4444";
    ctx.lineWidth = 18;
    ctx.lineCap = "round";
    ctx.stroke();

    // Target marker
    const targetAngle = startAngle + ((target - min) / (max - min)) * (endAngle - startAngle);
    const tx = cx + Math.cos(targetAngle) * (radius - 9);
    const ty = cy + Math.sin(targetAngle) * (radius - 9);
    ctx.beginPath();
    ctx.arc(tx, ty, 5, 0, Math.PI * 2);
    ctx.fillStyle = "#10b981";
    ctx.fill();
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 2;
    ctx.stroke();

    // Center value
    ctx.fillStyle = "#fff";
    ctx.font = "bold 36px Inter, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(value.toFixed(1), cx, cy + 12);

    ctx.fillStyle = "rgba(255,255,255,0.5)";
    ctx.font = "11px Inter, sans-serif";
    ctx.fillText("GSM", cx, cy + 32);

    // Min/Max labels
    ctx.fillStyle = "rgba(255,255,255,0.4)";
    ctx.font = "10px Inter, sans-serif";
    ctx.textAlign = "center";
    const minX = cx + Math.cos(startAngle) * (radius + 22);
    const minY = cy + Math.sin(startAngle) * (radius + 22);
    const maxX = cx + Math.cos(endAngle) * (radius + 22);
    const maxY = cy + Math.sin(endAngle) * (radius + 22);
    ctx.fillText(min.toString(), minX, minY);
    ctx.fillText(max.toString(), maxX, maxY);
  }, [value, min, max, target]);

  return (
    <canvas
      ref={canvasRef}
      className="mx-auto"
      width={200}
      height={200}
    />
  );
}
