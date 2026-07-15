"use client";

import { User, Mail, Shield, Clock } from "lucide-react";

export default function ProfilePage() {
  return (
    <div className="max-w-2xl space-y-8 animate-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Profile</h1>
        <p className="text-muted-foreground mt-1">Manage your account</p>
      </div>

      <div className="glass-card text-center">
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 mx-auto flex items-center justify-center text-2xl font-bold text-white mb-3">
          OP
        </div>
        <h2 className="text-xl font-semibold">Operator 01</h2>
        <p className="text-sm text-muted-foreground">Paper Machine PM-01</p>
      </div>

      <div className="glass-card space-y-4">
        <div className="flex items-center gap-3">
          <Mail className="w-5 h-5 text-muted-foreground" />
          <div>
            <span className="text-xs text-muted-foreground block">Email</span>
            <span className="text-sm">operator01@papermill.com</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Shield className="w-5 h-5 text-muted-foreground" />
          <div>
            <span className="text-xs text-muted-foreground block">Role</span>
            <span className="text-sm font-medium text-blue-400">Operator</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Clock className="w-5 h-5 text-muted-foreground" />
          <div>
            <span className="text-xs text-muted-foreground block">Last Active</span>
            <span className="text-sm">Today, 11:45 AM</span>
          </div>
        </div>
      </div>
    </div>
  );
}
