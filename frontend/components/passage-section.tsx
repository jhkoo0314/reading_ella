import { TranslationPanel, type TranslationPanelState } from "@/components/translation-panel";
import { TtsControls } from "@/components/tts-controls";

type PassageSectionProps = {
  title: string;
  text: string;
  topic: string;
  wordCount: number;
  translationOpen: boolean;
  translationState: TranslationPanelState;
  isPlaying: boolean;
  onToggleTranslation: () => void;
  onPlay: () => void;
  onStop: () => void;
};

export function PassageSection({
  title,
  text,
  topic,
  wordCount,
  translationOpen,
  translationState,
  isPlaying,
  onToggleTranslation,
  onPlay,
  onStop,
}: PassageSectionProps) {
  return (
    <div className="diary-panel slide-up">
      <div className="passage-meta" style={{ paddingLeft: 20, marginBottom: "1rem" }}>
        <span className="badge badge--accent" style={{ marginRight: 8 }}>🎈 {topic}</span>
        <span className="badge badge--muted">🧩 단어: {wordCount}개</span>
      </div>

      <h2 className="diary-title">{title}</h2>
      <p className="diary-text">{text}</p>

      <div className="section-toolbar" style={{ marginTop: "2rem", paddingLeft: 20, display: "flex", gap: "1rem" }}>
        <button className="badge badge--muted" type="button" onClick={onToggleTranslation} style={{ padding: "0.5rem 1rem", border: "1px solid var(--border)", background: "var(--surface-muted)" }}>
          {translationOpen ? "🙈 한국어 숨기기" : "👀 한국어 보기"}
        </button>
        <TtsControls playLabel="지문 읽기" isPlaying={isPlaying} onPlay={onPlay} onStop={onStop} />
      </div>

      <div style={{ paddingLeft: 20, marginTop: "1rem" }}>
        {translationOpen ? <TranslationPanel state={translationState} /> : null}
      </div>
    </div>
  );
}
