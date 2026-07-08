import { classroomApi } from "@/services/classroom";

export const classroomService = {
  listMine: classroomApi.listMine,
  join: classroomApi.join,
  getDetail: classroomApi.getDetail,
};

export default classroomService;
