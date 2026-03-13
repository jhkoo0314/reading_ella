import { motion } from "framer-motion";

type PrimaryStartButtonProps = {
  disabled: boolean;
  selectedLevelLabel: string;
  onClick: () => void;
};


export function PrimaryStartButton({
  disabled,
  selectedLevelLabel,
  onClick,
}: PrimaryStartButtonProps) {
  return (
    <div className="stack">
      <motion.div
        animate={disabled ? { y: 0 } : { y: [0, -8, 0] }}
        transition={{ repeat: disabled ? 0 : Infinity, duration: 1.5, ease: "easeInOut" }}
      >
        <button
          className="button button--primary"
          style={{ width: "100%" }}
          type="button"
          disabled={disabled}
          onClick={onClick}
        >
          {selectedLevelLabel ? `🚀 ${selectedLevelLabel} 반 출발!` : "🚀 출발하기!"}
        </button>
      </motion.div>
      <p className="inline-help" style={{ margin: 0, textAlign: "center" }}>
        {disabled
          ? "👈 먼저 반을 골라주세요!"
          : "준비가 다 되었어요! 로켓을 눌러주세요."}
      </p>
    </div>
  );
}
