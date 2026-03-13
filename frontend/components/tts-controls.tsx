type TtsControlsProps = {
  playLabel: string;
  stopLabel?: string;
  isPlaying: boolean;
  disabled?: boolean;
  onPlay: () => void;
  onStop: () => void;
};


export function TtsControls({
  playLabel,
  stopLabel = "정지",
  isPlaying,
  disabled = false,
  onPlay,
  onStop,
}: TtsControlsProps) {
  return (
    <div className="inline-button-row">
      <button className="inline-button" type="button" disabled={disabled} onClick={onPlay}>
        {isPlaying ? `${playLabel} 재생 중` : playLabel}
      </button>
      <button className="inline-button inline-button--muted" type="button" disabled={!isPlaying} onClick={onStop}>
        {stopLabel}
      </button>
    </div>
  );
}
