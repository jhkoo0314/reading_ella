"use client";

import { motion } from "framer-motion";

type AppShellProps = {
  children: React.ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <>
      {/* Background Animated Canvas Layer */}
      <div className="canvas-bg-layer">
        <div className="magic-blob magic-blob--pink" />
        <div className="magic-blob magic-blob--purple" />
        <div className="magic-blob magic-blob--yellow" />
      </div>

      <motion.main
        className="app-shell"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
      >
        {children}
      </motion.main>
    </>
  );
}
