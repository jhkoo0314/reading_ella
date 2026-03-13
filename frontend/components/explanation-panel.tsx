import { LoadingBlock } from "@/components/loading-block";


export type ExplanationPanelData = {
  explanation: string;
  sourceLabel: string;
  modelLabel?: string;
};

export type ExplanationPanelState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ready"; data: ExplanationPanelData }
  | { status: "error"; message: string };

type ExplanationPanelProps = {
  state: ExplanationPanelState;
};


export function ExplanationPanel({ state }: ExplanationPanelProps) {
  if (state.status === "idle") {
    return null;
  }

  if (state.status === "loading") {
    return (
      <div className="explanation-panel">
        <LoadingBlock label="해설을 준비하는 중입니다." />
      </div>
    );
  }

  if (state.status === "error") {
    return (
      <div className="explanation-panel explanation-panel--error" role="status">
        <p className="translation-panel__text">{state.message}</p>
      </div>
    );
  }

  return (
    <div className="explanation-panel" role="status">
      <p className="translation-panel__text">{state.data.explanation}</p>
      <p className="translation-panel__source">
        {state.data.sourceLabel}
        {state.data.modelLabel ? ` · ${state.data.modelLabel}` : ""}
      </p>
    </div>
  );
}
