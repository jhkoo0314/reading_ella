export function buildQuestionWithChoicesSpeechText(prompt: string, choices: string[]) {
  const choicesText = choices
    .map((choice, index) => `${String.fromCharCode(65 + index)}. ${choice}.`)
    .join(" ");

  return `Question. ${prompt}. Choices. ${choicesText}`;
}
