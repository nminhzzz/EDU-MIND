import { studyPlanApi } from "@/services/study-plan";

export const studyPlanService = {
  getPlans: studyPlanApi.getPlans,
  getPlan: studyPlanApi.getPlan,
  updatePlanStatus: studyPlanApi.updatePlanStatus,
};

export default studyPlanService;
