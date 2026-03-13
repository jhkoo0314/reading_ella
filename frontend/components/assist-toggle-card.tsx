import type { AssistToggles } from "@/lib/types/app";


type AssistToggleKey = keyof AssistToggles;

const TOGGLE_OPTIONS: Array<{
  key: AssistToggleKey;
  label: string;
  description: string;
  dependsOnMaster: boolean;
}> = [
  {
    key: "useAssistApi",
    label: "Use Assist API",
    description: "외부 보조 기능 전체 사용을 허용합니다. 기본값은 OFF입니다.",
    dependsOnMaster: false,
  },
  {
    key: "useApiTranslation",
    label: "Use API Translation",
    description: "로컬 번역이 없을 때만 추가 번역 요청을 허용합니다.",
    dependsOnMaster: true,
  },
  {
    key: "useApiTts",
    label: "Use API TTS",
    description: "브라우저 TTS 대신 외부 음성 사용을 허용합니다.",
    dependsOnMaster: true,
  },
  {
    key: "useApiExplain",
    label: "Use API Explain",
    description: "로컬 해설이 없거나 더 자세한 설명이 필요할 때 사용합니다.",
    dependsOnMaster: true,
  },
];

type AssistToggleCardProps = {
  toggles: AssistToggles;
  onToggle: (key: AssistToggleKey) => void;
};


export function AssistToggleCard({ toggles, onToggle }: AssistToggleCardProps) {
  return (
    <div className="toggle-list">
      {TOGGLE_OPTIONS.map((option) => {
        const isDisabled = option.dependsOnMaster && !toggles.useAssistApi;

        return (
          <label
            key={option.key}
            className={`toggle-row ${isDisabled ? "toggle-row--disabled" : ""}`}
          >
            <div>
              <strong>{option.label}</strong>
              <p className="toggle-row__description">{option.description}</p>
            </div>
            <span className="toggle-row__control">
              <span className={`badge ${toggles[option.key] ? "badge--accent" : "badge--muted"}`}>
                {toggles[option.key] ? "ON" : "OFF"}
              </span>
              <input
                type="checkbox"
                checked={toggles[option.key]}
                disabled={isDisabled}
                onChange={() => onToggle(option.key)}
                aria-label={option.label}
              />
            </span>
          </label>
        );
      })}
    </div>
  );
}
