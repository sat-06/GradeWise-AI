"use client";

import { useState } from "react";
import { Settings, Bell, Database, BrainCircuit, Monitor } from "lucide-react";

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    mlRetraining: "weekly",
    alertEmail: true,
    alertSlack: false,
    dataRetention: 90,
    modelThreshold: 0.85,
    autoRecommend: false,
  });

  return (
    <div className="max-w-4xl space-y-8 animate-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">Configure GradeWise AI platform settings</p>
      </div>

      <div className="space-y-6">
        {/* ML Settings */}
        <div className="glass-card">
          <div className="flex items-center gap-3 mb-4">
            <BrainCircuit className="w-5 h-5 text-blue-400" />
            <h3 className="font-semibold">AI & ML Configuration</h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-muted-foreground">Model Retraining Schedule</label>
              <select
                value={settings.mlRetraining}
                onChange={(e) => setSettings({ ...settings, mlRetraining: e.target.value })}
                className="w-full mt-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly (Recommended)</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-muted-foreground">
                Prediction Confidence Threshold: {(settings.modelThreshold * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min={0.5}
                max={0.99}
                step={0.01}
                value={settings.modelThreshold}
                onChange={(e) =>
                  setSettings({ ...settings, modelThreshold: parseFloat(e.target.value) })
                }
                className="w-full mt-1 accent-primary"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Auto-apply recommendations</span>
              <button
                onClick={() =>
                  setSettings({ ...settings, autoRecommend: !settings.autoRecommend })
                }
                className={`w-12 h-6 rounded-full transition-colors ${
                  settings.autoRecommend ? "bg-blue-600" : "bg-white/10"
                }`}
              >
                <div
                  className={`w-5 h-5 rounded-full bg-white transition-transform ${
                    settings.autoRecommend ? "translate-x-6" : "translate-x-0.5"
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="glass-card">
          <div className="flex items-center gap-3 mb-4">
            <Bell className="w-5 h-5 text-amber-400" />
            <h3 className="font-semibold">Notifications</h3>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">Email alerts</span>
              <button
                onClick={() => setSettings({ ...settings, alertEmail: !settings.alertEmail })}
                className={`w-12 h-6 rounded-full transition-colors ${
                  settings.alertEmail ? "bg-blue-600" : "bg-white/10"
                }`}
              >
                <div
                  className={`w-5 h-5 rounded-full bg-white transition-transform ${
                    settings.alertEmail ? "translate-x-6" : "translate-x-0.5"
                  }`}
                />
              </button>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Slack notifications</span>
              <button
                onClick={() => setSettings({ ...settings, alertSlack: !settings.alertSlack })}
                className={`w-12 h-6 rounded-full transition-colors ${
                  settings.alertSlack ? "bg-blue-600" : "bg-white/10"
                }`}
              >
                <div
                  className={`w-5 h-5 rounded-full bg-white transition-transform ${
                    settings.alertSlack ? "translate-x-6" : "translate-x-0.5"
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Data Settings */}
        <div className="glass-card">
          <div className="flex items-center gap-3 mb-4">
            <Database className="w-5 h-5 text-purple-400" />
            <h3 className="font-semibold">Data Management</h3>
          </div>
          <div>
            <label className="text-sm text-muted-foreground">
              Data Retention Period: {settings.dataRetention} days
            </label>
            <input
              type="range"
              min={30}
              max={365}
              step={30}
              value={settings.dataRetention}
              onChange={(e) =>
                setSettings({ ...settings, dataRetention: parseInt(e.target.value) })
              }
              className="w-full mt-1 accent-primary"
            />
          </div>
        </div>

        <button className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 text-white font-semibold hover:from-blue-500 hover:to-cyan-500 transition-colors">
          Save Settings
        </button>
      </div>
    </div>
  );
}
