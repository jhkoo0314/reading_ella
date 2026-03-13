import { motion } from "framer-motion";
import type { PublicQuestion } from "@/lib/types/api";
import { TranslationPanel, type TranslationPanelState } from "@/components/translation-panel";
import { TtsControls } from "@/components/tts-controls";

type QuestionCardProps = {
  question: PublicQuestion;
  questionNumber: number;
  selectedIndex: number | undefined;
  questionTranslationOpen: boolean;
  questionTranslationState: TranslationPanelState;
  isQuestionBlockPlaying: boolean;
  onSelect: (choiceIndex: number) => void;
  onToggleQuestionTranslation: () => void;
  onPlayQuestionBlock: () => void;
  onStopTts: () => void;
  style?: React.CSSProperties; // Added to let parent stack cards
};

function getSkillLabel(skill: PublicQuestion["skill"]) {
  if (skill === "main_idea") return "🌟 주제 찾기";
  if (skill === "detail") return "🔍 자세히 보기";
  if (skill === "inference") return "💡 생각 넓히기";
  return "📖 단어 뜻 알기";
}

function getChoiceLabel(index: number) {
  return String.fromCharCode(65 + index);
}

export function QuestionCard({
  question,
  questionNumber,
  selectedIndex,
  questionTranslationOpen,
  questionTranslationState,
  isQuestionBlockPlaying,
  onSelect,
  onToggleQuestionTranslation,
  onPlayQuestionBlock,
  onStopTts,
  style
}: QuestionCardProps) {
  return (
    <motion.article 
      className="magic-card fade-in" 
      style={style}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.1 * questionNumber }}
    >
      <div className="card-number-badge">{questionNumber}</div>
      <div className="question-card__top" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <span className="badge badge--accent">{getSkillLabel(question.skill)}</span>
        <span className="badge badge--muted">
          {selectedIndex !== undefined ? "💖 선택완료" : "💭 안 골랐어요"}
        </span>
      </div>

      <p className="question-prompt">{question.prompt}</p>

      <fieldset className="jelly-choices">
        <legend className="sr-only">{`문항 ${questionNumber} 답 고르기`}</legend>
        {question.choices.map((choice, index) => {
          const isSelected = selectedIndex === index;

          return (
            <motion.label
              key={`${question.id}-${index}`}
              className={`jelly-choice ${isSelected ? "jelly-choice--selected" : ""}`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <input
                className="sr-only"
                type="radio"
                name={question.id}
                checked={isSelected}
                onChange={() => onSelect(index)}
              />
              <span className="jelly-choice__letter">{getChoiceLabel(index)}</span>
              <span className="jelly-choice__text" style={{ flex: 1, lineHeight: 1.4 }}>{choice}</span>
            </motion.label>
          );
        })}
      </fieldset>

      <div className="question-card__actions" style={{ marginTop: "2rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
        <div className="inline-button-row" style={{ justifyContent: "flex-start" }}>
          <button className="inline-button" type="button" onClick={onToggleQuestionTranslation}>
            {questionTranslationOpen ? "🙈 문항 번역 숨기기" : "👀 문항 번역 보기"}
          </button>
        </div>

        <div style={{ display: "flex", gap: "1rem", justifyContent: "flex-start" }}>
          <TtsControls playLabel="문항 전체 읽기" isPlaying={isQuestionBlockPlaying} onPlay={onPlayQuestionBlock} onStop={onStopTts} />
        </div>
      </div>

      <div style={{ marginTop: "1rem" }}>
        {questionTranslationOpen ? <TranslationPanel state={questionTranslationState} /> : null}
      </div>
    </motion.article>
  );
}
