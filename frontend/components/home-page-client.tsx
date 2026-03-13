"use client";

import { useState, useSyncExternalStore } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

import { buildAssistQueryString } from "@/lib/assist-query";
import {
  getServerSessionDraftSnapshot,
  getSessionDraftSnapshot,
  saveSessionDraft,
  subscribeSessionDraft,
} from "@/lib/session-draft-storage";
import type { SessionDraft } from "@/lib/types/app";
import type { Level } from "@/lib/types/api";

export function HomePageClient() {
  const router = useRouter();
  const draft = useSyncExternalStore(
    subscribeSessionDraft,
    getSessionDraftSnapshot,
    getServerSessionDraftSnapshot,
  );
  const [showSettings, setShowSettings] = useState(false);

  function updateDraft(nextDraft: SessionDraft) {
    saveSessionDraft(nextDraft);
  }

  function handleLevelSelect(level: Level) {
    const nextDraft = { ...draft, level };
    updateDraft(nextDraft);
  }

  function handleToggleAssistApi() {
    const nextUseAssistApi = !draft.toggles.useAssistApi;
    const nextToggles = {
      ...draft.toggles,
      useAssistApi: nextUseAssistApi,
    };

    if (nextUseAssistApi && !nextToggles.useApiTranslation && !nextToggles.useApiExplain) {
      nextToggles.useApiTranslation = true;
      nextToggles.useApiExplain = true;
    }

    updateDraft({
      ...draft,
      toggles: nextToggles,
    });
  }

  function handleToggleFeature(key: "useApiTranslation" | "useApiExplain") {
    updateDraft({
      ...draft,
      toggles: {
        ...draft.toggles,
        [key]: !draft.toggles[key],
      },
    });
  }

  function handleStart() {
    if (!draft.level) return;
    router.push(`/solve/random?${buildAssistQueryString(draft.toggles, draft.level)}`);
  }

  function handleReviewOpen() {
    router.push(`/review?${buildAssistQueryString(draft.toggles)}`);
  }

  return (
    <main className="game-screen-wrapper">
      {/* 3D Animated Background blobs instead of external Spline loading */}
      <div className="spline-bg" style={{ overflow: 'hidden' }}>
        <div className="canvas-bg-layer">
          <div className="magic-blob magic-blob--pink" />
          <div className="magic-blob magic-blob--purple" />
          <div className="magic-blob magic-blob--yellow" />
        </div>
        
        {/* Decorative Floating Elements (Stars & Clouds) */}
        <div className="decorations-layer">
          <div className="game-cloud game-cloud--1">☁️</div>
          <div className="game-cloud game-cloud--2">☁️</div>
          <div className="game-star game-star--1">⭐</div>
          <div className="game-star game-star--2">⭐</div>
          <div className="game-star game-star--3">✨</div>
          <div className="game-planet-deco">🪐</div>
        </div>
      </div>

      {/* Video Game UI Layer */}
      <div className="game-ui-layer">
        <header className="game-header">
          <motion.h1 
            className="game-title"
            initial={{ y: -50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ type: "spring", stiffness: 100, damping: 10 }}
          >
            <span className="game-title-text">Reading ELLA</span>
            <div className="game-title-sparkles">✨</div>
          </motion.h1>
          <motion.button 
            className="game-settings-btn"
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowSettings(true)}
          >
            <span className="wand-icon">🪄</span> 마법 지팡이
          </motion.button>
        </header>

        <div className="game-center-content">
          <motion.div 
            className="level-planet-container"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, type: "spring" }}
          >
            <h2 className="select-prompt">오늘 탐험할 행성을 골라봐! 🚀</h2>
            <div className="planet-row">
              {(["GT", "MGT", "S"] as Level[]).map((level) => {
                const isSelected = draft.level === level;
                const badges: Record<Level, string> = { GT: "🌱 씨앗 행성", MGT: "🌿 새싹 행성", S: "🌸 꽃잎 행성" };
                return (
                  <motion.button
                    key={level}
                    className={`planet-btn planet-btn--${level.toLowerCase()} ${isSelected ? 'planet-btn--active' : ''}`}
                    whileHover={{ scale: 1.1, y: -20 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => handleLevelSelect(level)}
                  >
                    <div className="planet-sphere" />
                    <div className="planet-shadow" />
                    <span className="planet-label">{badges[level]}</span>
                  </motion.button>
                );
              })}
            </div>
          </motion.div>

          <motion.div
            className="start-action-container"
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ type: "spring", bounce: 0.5 }}
          >
            <div className="game-action-stack">
              {draft.level ? (
                <button className="game-start-btn" onClick={handleStart}>
                  <span className="btn-text">모험 시작하기!</span>
                  <span className="btn-highlight"></span>
                </button>
              ) : null}
              <button className="game-secondary-btn" onClick={handleReviewOpen}>
                지난 오답 복습하기
              </button>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Settings Modal Overlay */}
      <AnimatePresence>
        {showSettings && (
          <motion.div 
            className="game-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div 
              className="game-modal-content"
              initial={{ scale: 0.8, y: 50 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.8, y: 50 }}
            >
              <button className="game-modal-close" onClick={() => setShowSettings(false)}>❌</button>
              <h3 className="game-modal-title">🪄 마법 지팡이 (API)</h3>
              <p className="game-modal-desc">모험 중 어려울 때 도움을 받을 수 있어!</p>
              
              <div className="settings-list">
                <label className="game-toggle">
                  <span>전체 마법 켜기</span>
                  <input 
                    type="checkbox" 
                    checked={draft.toggles.useAssistApi} 
                    onChange={handleToggleAssistApi}
                  />
                  <div className="toggle-switch"></div>
                </label>
                <label className="game-toggle">
                  <span>문제 해석 도움</span>
                  <input
                    type="checkbox"
                    checked={draft.toggles.useApiTranslation}
                    onChange={() => handleToggleFeature("useApiTranslation")}
                  />
                  <div className="toggle-switch"></div>
                </label>
                <label className="game-toggle">
                  <span>오답 설명 도움</span>
                  <input
                    type="checkbox"
                    checked={draft.toggles.useApiExplain}
                    onChange={() => handleToggleFeature("useApiExplain")}
                  />
                  <div className="toggle-switch"></div>
                </label>
                <div className="game-settings-note">
                  읽어주기는 지금도 바로 됩니다. 이 기능은 기기 목소리를 먼저 사용합니다.
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
