import type { Level } from "@/lib/types/api";
import { motion } from "framer-motion";

const LEVEL_OPTIONS: Array<{
  level: Level;
  emoji: string;
  label: string;
  description: string;
}> = [
  {
    level: "GT",
    emoji: "🌱",
    label: "GT 반",
    description: "씨앗 단계",
  },
  {
    level: "S",
    emoji: "🌿",
    label: "S 반",
    description: "새싹 단계",
  },
  {
    level: "MGT",
    emoji: "🌸",
    label: "MGT 반",
    description: "꽃잎 단계",
  },
];

type DifficultySelectorProps = {
  selectedLevel: Level | null;
  onSelect: (level: Level) => void;
};

export function DifficultySelector({ selectedLevel, onSelect }: DifficultySelectorProps) {
  return (
    <div className="island-selector-grid" role="list" aria-label="난이도 선택">
      {LEVEL_OPTIONS.map((option) => {
        const isSelected = option.level === selectedLevel;

        return (
          <motion.button
            key={option.level}
            className={`island-btn ${isSelected ? "island-btn--selected" : ""}`}
            type="button"
            onClick={() => onSelect(option.level)}
            aria-pressed={isSelected}
            whileHover={{ scale: 1.05, y: -10 }}
            whileTap={{ scale: 0.95 }}
          >
            <span className="island-btn__emoji">{option.emoji}</span>
            <span className="island-btn__label">{option.label}</span>
            <span className="island-btn__desc">{option.description}</span>
          </motion.button>
        );
      })}
    </div>
  );
}
