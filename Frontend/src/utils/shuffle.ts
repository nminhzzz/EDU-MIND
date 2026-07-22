/**
 * Fisher-Yates Shuffle Algorithm for randomizing question and option orders.
 */
export function shuffleArray<T>(array: T[]): T[] {
  if (!array || array.length === 0) return [];
  const result = [...array];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

/**
 * Shuffles quiz questions and options within questions for student test attempts.
 */
export function shuffleQuizForStudent<T extends { options?: any[] }>(questions: T[]): T[] {
  const shuffledQuestions = shuffleArray(questions);
  return shuffledQuestions.map((q) => {
    if (q.options && q.options.length > 0) {
      return {
        ...q,
        options: shuffleArray(q.options),
      };
    }
    return q;
  });
}
