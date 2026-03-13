export type Level = "GT" | "S" | "MGT";
export type Skill = "main_idea" | "detail" | "inference" | "vocab_in_context";
export type TranslationScope = "passage" | "question_full";
export type ExplanationDetailLevel = "short" | "deep";
export type TtsScope = "passage" | "question_prompt" | "question_choices";

export type PublicPassage = {
  title: string;
  text: string;
  word_count: number;
};

export type PublicQuestion = {
  id: string;
  skill: Skill;
  prompt: string;
  choices: string[];
};

export type TranslationAssist = {
  lang: string;
  passage_available: boolean;
  question_prompt_ids: string[];
  question_choice_ids: string[];
};

export type ExplanationAssist = {
  local_rationale_available: boolean;
  api_available: boolean;
  available_depths: string[];
};

export type TtsAssist = {
  browser_available: boolean;
  api_available: boolean;
};

export type AssistInfo = {
  translation: TranslationAssist;
  explanation: ExplanationAssist;
  tts: TtsAssist;
};

export type PackLoadResponse = {
  pack_id: string;
  topic: string;
  passage: PublicPassage;
  questions: PublicQuestion[];
  assist: AssistInfo;
};

export type SubmitAnswerItem = {
  question_id: string;
  chosen_index: number;
};

export type SubmitRequest = {
  pack_id: string;
  started_at: string;
  answers: SubmitAnswerItem[];
};

export type SubmitAnswerResult = {
  question_id: string;
  chosen_index: number;
  is_correct: boolean;
};

export type SkillScore = {
  correct: number;
  total: number;
};

export type ScoreSummary = {
  raw: number;
  total: number;
  by_skill: Record<string, SkillScore>;
};

export type SubmitResponse = {
  attempt_id: string;
  pack_id: string;
  started_at: string;
  finished_at: string;
  answers: SubmitAnswerResult[];
  score: ScoreSummary;
  wrong_question_ids: string[];
};

export type ReviewQuestionItem = {
  attempt_id: string;
  pack_id: string;
  level: string;
  topic: string;
  passage_title: string;
  question_id: string;
  question_number: number;
  skill: Skill;
  prompt: string;
  choices: string[];
  chosen_index: number;
  correct_index: number;
  chosen_text: string;
  correct_text: string;
  finished_at: string;
  created_at?: string | null;
  status?: string | null;
  reason?: string | null;
};

export type AttemptResultResponse = {
  attempt_id: string;
  pack_id: string;
  level: string;
  topic: string;
  passage_title: string;
  started_at: string;
  finished_at: string;
  score: ScoreSummary;
  wrong_questions: ReviewQuestionItem[];
};

export type ReviewListResponse = {
  items: ReviewQuestionItem[];
};

export type TranslationRequest = {
  pack_id: string;
  target_lang?: string;
  scope: TranslationScope;
  question_id?: string;
  allow_external_api?: boolean;
};

export type TranslationResponse = {
  source: "local_overlay" | "api_live";
  provider_used?: string | null;
  model_used?: string | null;
  pack_id: string;
  target_lang: string;
  scope: TranslationScope;
  question_id?: string | null;
  translated_title?: string | null;
  translated_text?: string | null;
  translated_prompt?: string | null;
  translated_choices?: string[] | null;
};

export type ExplanationRequest = {
  pack_id: string;
  question_id: string;
  chosen_index: number;
  target_lang?: string;
  detail_level: ExplanationDetailLevel;
  allow_external_api?: boolean;
};

export type ExplanationResponse = {
  source: "local_rationale" | "api_live";
  provider_used?: string | null;
  model_used?: string | null;
  pack_id: string;
  question_id: string;
  target_lang: string;
  detail_level: ExplanationDetailLevel;
  explanation: string;
};

export type TtsRequest = {
  pack_id: string;
  scope: TtsScope;
  question_id?: string;
  allow_external_api?: boolean;
};

export type TtsResponse = {
  source: "browser_tts" | "api_live";
  provider_used?: string | null;
  voice_used?: string | null;
  pack_id: string;
  scope: TtsScope;
  question_id?: string | null;
  playback_mode: "browser" | "external";
  voice_locale: string;
  text: string;
  audio_url?: string | null;
};

export type ApiErrorResponse = {
  detail?: string;
};
