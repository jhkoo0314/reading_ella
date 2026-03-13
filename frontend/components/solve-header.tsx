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
      initial={{ opacity: 0, y: -20, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, type: "spring", bounce: 0.4 }}
    >
      <div className="solve-header__meta">
        <span className="badge badge--accent">{level} 반</span>
        <span className="badge">{packId} 세트</span>
        {unansweredCount > 0 ? (
          <span className="badge badge--muted">🔥 {unansweredCount}문제 남았어요!</span>
        ) : (
          <span className="badge badge--accent">✨ 와! 다 풀었어요!</span>
        )}
      </div>

      <div className="solve-header__body">
        <div>
          <p className="solve-header__eyebrow">🚀 오늘의 미션 ({totalQuestions - unansweredCount} / {totalQuestions})</p>
          <div style={{ width: "100%", height: "8px", background: "var(--surface)", borderRadius: "4px", marginTop: "4px", marginBottom: "12px", overflow: "hidden" }}>
             <motion.div 
               initial={{ width: 0 }}
               animate={{ width: `${((totalQuestions - unansweredCount) / totalQuestions) * 100}%` }}
               transition={{ duration: 0.5 }}
               style={{ height: "100%", background: "var(--accent)", borderRadius: "4px" }} 
             />
          </div>
          <h1 className="solve-header__title">{topic}</h1>
          <p className="solve-header__description">그림책을 읽듯이 천천히 읽어봐요!</p>
        </div>
        <div className="inline-button-row">
          <motion.button 
            className="inline-button" 
            type="button" 
            onClick={onHomeClick} 
            disabled={isSubmitting}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            🏠 홈으로 가기
          </motion.button>
          <motion.button
            className="button button--primary"
            type="button"
            disabled={unansweredCount > 0 || isSubmitting}
            onClick={onSubmitClick}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isSubmitting ? "채점 중..." : "🚀 다 했어요!"}
          </motion.button>
        </div>
      </div>
    </motion.header>
  );
}
