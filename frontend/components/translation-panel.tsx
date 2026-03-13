import { LoadingBlock } from "@/components/loading-block";


export type TranslationPanelData = {
  title?: string;
  text?: string;
  choices?: string[];
  sourceLabel: string;
};

export type TranslationPanelState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ready"; data: TranslationPanelData }
  | { status: "error"; message: string };

type TranslationPanelProps = {
  state: TranslationPanelState;
};


export function TranslationPanel({ state }: TranslationPanelProps) {
  if (state.status === "idle") {
    return null;
  }

  if (state.status === "loading") {
    return (
      <div className="translation-panel">
        <LoadingBlock label="번역을 준비하는 중입니다." />
      </div>
    );
  }

  if (state.status === "error") {
    return (
      <div className="translation-panel translation-panel--error" role="status">
        <p className="translation-panel__text">{state.message}</p>
      </div>
    );
  }

  const { title, text, choices, sourceLabel } = state.data;

  return (
    <div className="translation-panel" role="status">
      {title ? <strong className="translation-panel__title">{title}</strong> : null}
      {text ? <p className="translation-panel__text">{text}</p> : null}
      {choices && choices.length > 0 ? (
        <ol className="translation-panel__choices">
          {choices.map((choice, index) => (
            <li key={`${choice}-${index}`}>{choice}</li>
          ))}
        </ol>
      ) : null}
      <p className="translation-panel__source">{sourceLabel}</p>
    </div>
  );
}
