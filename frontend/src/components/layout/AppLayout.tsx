"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Cpu,
  BrainCircuit,
  Sparkles,
  SlidersHorizontal,
  History,
  BookOpen,
  BarChart3,
  Bell,
  Settings,
  User,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  AlertTriangle,
  Zap,
  Activity,
  Gauge,
  Factory,
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard, description: "Overview & KPIs" },
  { name: "Live Monitoring", href: "/monitoring", icon: Activity, description: "Real-time machine data" },
  { name: "AI Predictions", href: "/predictions", icon: BrainCircuit, description: "Predictive engine" },
  { name: "Explainable AI", href: "/explainability", icon: Sparkles, description: "Prediction explanations" },
  { name: "Recommendations", href: "/recommendations", icon: TrendingUp, description: "Optimal settings" },
  { name: "What-If Simulator", href: "/whatif", icon: SlidersHorizontal, description: "Digital twin" },
  { name: "Historical Insights", href: "/history", icon: History, description: "Transition analysis" },
  { name: "Knowledge Base", href: "/knowledge", icon: BookOpen, description: "Lessons learned" },
  { name: "Business Analytics", href: "/analytics", icon: BarChart3, description: "BI dashboard" },
  { name: "Alerts", href: "/alerts", icon: Bell, description: "Intelligent alerts" },
];

const bottomNav = [
  { name: "Settings", href: "/settings", icon: Settings },
  { name: "Profile", href: "/profile", icon: User },
];

export function AppLayout({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Sidebar */}
      <motion.aside
        animate={{ width: collapsed ? 72 : 280 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        className="flex flex-col border-r border-border bg-card/80 backdrop-blur-xl z-50"
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 h-16 border-b border-border">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/25">
            <Gauge className="w-5 h-5 text-white" />
          </div>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col"
            >
              <span className="text-sm font-bold tracking-tight">GradeWise</span>
              <span className="text-[10px] text-muted-foreground uppercase tracking-widest">AI Platform</span>
            </motion.div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto custom-scrollbar py-3 px-2 space-y-0.5">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link key={item.href} href={item.href}>
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative",
                    isActive
                      ? "bg-primary/15 text-primary border border-primary/20"
                      : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
                  )}
                >
                  <item.icon
                    className={cn(
                      "w-5 h-5 flex-shrink-0",
                      isActive && "text-primary"
                    )}
                  />
                  {!collapsed && (
                    <div className="flex flex-col min-w-0">
                      <span className="text-sm font-medium truncate">{item.name}</span>
                      <span className="text-[10px] text-muted-foreground/60 truncate">
                        {item.description}
                      </span>
                    </div>
                  )}
                  {isActive && !collapsed && (
                    <motion.div
                      layoutId="activeNav"
                      className="absolute right-2 w-1 h-6 rounded-full bg-primary"
                    />
                  )}
                </motion.div>
              </Link>
            );
          })}
        </nav>

        {/* Bottom */}
        <div className="border-t border-border p-2 space-y-0.5">
          {bottomNav.map((item) => (
            <Link key={item.href} href={item.href}>
              <div
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200",
                  pathname === item.href
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
                )}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {!collapsed && <span className="text-sm font-medium">{item.name}</span>}
              </div>
            </Link>
          ))}
        </div>

        {/* Collapse button */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="h-10 border-t border-border flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto custom-scrollbar">
        {/* Top Bar */}
        <header className="sticky top-0 z-40 h-16 border-b border-border bg-background/80 backdrop-blur-xl flex items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <Factory className="w-5 h-5 text-muted-foreground" />
            <span className="text-sm text-muted-foreground font-mono">
              Machine PM-01 • <span className="text-success flex items-center gap-1.5">
                <span className="status-dot status-green" />
                Running
              </span>
            </span>
          </div>
          <div className="flex items-center gap-4">
            <Bell className="w-5 h-5 text-muted-foreground cursor-pointer hover:text-foreground transition-colors" />
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-xs font-bold text-white">
              OP
            </div>
          </div>
        </header>

        {/* Page Content */}
        <motion.div
          key={pathname}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="p-6"
        >
          {children}
        </motion.div>
      </main>
    </div>
  );
}
