"use client";

import { useCallback, useEffect, useRef, useState } from "react";


export function useBrowserTts() {
  const [playingKey, setPlayingKey] = useState<string | null>(null);
  const speechRef = useRef<SpeechSynthesisUtterance | null>(null);

  const stopSpeech = useCallback(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }

    speechRef.current = null;
    setPlayingKey(null);
  }, []);

  const speakText = useCallback((key: string, text: string) => {
    if (typeof window === "undefined") {
      return;
    }

    if (!("speechSynthesis" in window)) {
      alert("이 브라우저에서는 읽기 기능을 사용할 수 없습니다.");
      return;
    }

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 0.95;
    utterance.onend = () => {
      speechRef.current = null;
      setPlayingKey((currentKey) => (currentKey === key ? null : currentKey));
    };
    utterance.onerror = () => {
      speechRef.current = null;
      setPlayingKey((currentKey) => (currentKey === key ? null : currentKey));
    };

    speechRef.current = utterance;
    setPlayingKey(key);
    window.speechSynthesis.speak(utterance);
  }, []);

  useEffect(() => {
    return () => {
      stopSpeech();
    };
  }, [stopSpeech]);

  return {
    playingKey,
    speakText,
    stopSpeech,
  };
}
