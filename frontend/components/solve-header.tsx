"use client";

import { motion } from "framer-motion";
import type { AssistToggles } from "@/lib/types/app";

type SolveHeaderProps = {
  packId: string;
  level: string;
  topic: string;
  toggles: AssistToggles;
  unansweredCount: number;
  totalQuestions: number;
  isSubmitting: boolean;
  onHomeClick: () => void;
  onSubmitClick: () => void;
};

export function SolveHeader({
  packId,
  level,
  topic,
  unansweredCount,
  totalQuestions,
  isSubmitting,
  onHomeClick,
  onSubmitClick,
}: SolveHeaderProps) {
  return (
    <motion.header 
      className="solve-header"
      style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: '1rem 2rem' }}
      initial={{ opacity: 0, y: -20, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, type: "spring", bounce: 0.4 }}
    >
      <div className="solve-header__meta" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '0.4rem', margin: 0 }}>
        <div style={{ display: 'flex', gap: '0.4rem' }}>
          <span className="badge badge--accent">{level} 반</span>
          <span className="badge">{packId} 세트</span>
        </div>
        {unansweredCount > 0 ? (
          <span className="badge badge--muted" style={{ fontSize: '0.8rem', minHeight: 'auto', padding: '0.1rem 0.5rem' }}>🔥 {unansweredCount}문제 남았어요!</span>
        ) : (
          <span className="badge badge--accent" style={{ fontSize: '0.8rem', minHeight: 'auto', padding: '0.1rem 0.5rem' }}>✨ 와! 다 풀었어요!</span>
        )}
      </div>

      <div className="solve-header__body" style={{ flex: 1, padding: '0 2rem' }}>
        <p className="solve-header__eyebrow" style={{ marginBottom: '0.2rem' }}>🚀 오늘의 미션 ({totalQuestions - unansweredCount} / {totalQuestions})</p>
        <h1 className="solve-header__title" style={{ fontSize: '1.5rem', marginBottom: 0 }}>{topic}</h1>
      </div>

      <div className="inline-button-row" style={{ gap: '0.8rem' }}>
        <motion.button 
          className="inline-button" 
          style={{ padding: '0.6rem 1rem', fontSize: '0.9rem' }}
          type="button" 
          onClick={onHomeClick} 
          disabled={isSubmitting}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          🏠 홈
        </motion.button>
        <motion.button
          className="button button--primary"
          style={{ padding: '0.6rem 1rem', fontSize: '1rem' }}
          type="button"
          disabled={unansweredCount > 0 || isSubmitting}
          onClick={onSubmitClick}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {isSubmitting ? "채점 중..." : "🚀 제출"}
        </motion.button>
      </div>
    </motion.header>
  );
}
