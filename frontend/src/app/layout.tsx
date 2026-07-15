import type { Metadata } from "next";
import "./globals.css";
import { AppLayout } from "@/components/layout/AppLayout";
import { Toaster } from "sonner";
import { ThemeProvider } from "@/components/shared/ThemeProvider";

export const metadata: Metadata = {
  title: "GradeWise AI — Intelligent Basis Weight Control",
  description:
    "AI-Powered Decision Support System for Predictive Basis Weight Control During Paper Grade Transitions",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        <ThemeProvider>
          <AppLayout>{children}</AppLayout>
          <Toaster
            position="top-right"
            toastOptions={{
              className: "glass-dark border border-white/10",
            }}
          />
        </ThemeProvider>
      </body>
    </html>
  );
}
