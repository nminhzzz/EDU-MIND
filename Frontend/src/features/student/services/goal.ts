import { goalApi } from "@/services/goal";

export const goalService = {
  getPreferences: goalApi.getPreferences,
  updatePreferences: goalApi.updatePreferences,
  getGoals: goalApi.getGoals,
  deleteGoal: goalApi.deleteGoal,
  createDraft: goalApi.createDraft,
  confirmDraft: goalApi.confirmDraft,
};

export default goalService;
