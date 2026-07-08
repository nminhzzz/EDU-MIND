"use client";

import React from "react";
import { AnimatePresence } from "framer-motion";
import { GoalsWizardState } from "@/features/student/hooks/use-goals-wizard";
import { GoalsCheckingStep } from "./goals-checking-step";
import { GoalsCreateStep } from "./goals-create-step";
import { GoalsDraftStep } from "./goals-draft-step";
import { GoalsListStep } from "./goals-list-step";
import { GoalsScheduleStep } from "./goals-schedule-step";
import { GoalsSuccessStep } from "./goals-success-step";

interface GoalsWizardProps {
  wizard: GoalsWizardState;
}

export function GoalsWizard({ wizard }: GoalsWizardProps) {
  const {
    step,
    setStep,
    subjects,
    loading,
    goals,
    goalsLoading,
    studyHours,
    setStudyHours,
    preferredTime,
    setPreferredTime,
    schedule,
    selectedSubjectId,
    setSelectedSubjectId,
    targetScore,
    setTargetScore,
    deadline,
    setDeadline,
    userMessage,
    setUserMessage,
    draft,
    chatMessage,
    setChatMessage,
    chatLoading,
    handleSaveSchedule,
    handleCreateDraft,
    handleSendMessageToAI,
    handleConfirmRoadmap,
    handleDeleteGoal,
    toggleTimeSlot,
    handleHourChange,
    handleCancelDraft,
  } = wizard;

  return (
    <div className="max-w-6xl mx-auto py-6 px-4 sm:px-6 text-left">
      <AnimatePresence mode="wait">
        {step === "checking" && <GoalsCheckingStep />}

        {step === "list_goals" && (
          <GoalsListStep
            goals={goals}
            subjects={subjects}
            goalsLoading={goalsLoading}
            onCreateClick={() => setStep("create_goal")}
            onDeleteGoal={handleDeleteGoal}
          />
        )}

        {step === "setup_schedule" && (
          <GoalsScheduleStep
            studyHours={studyHours}
            preferredTime={preferredTime}
            schedule={schedule}
            loading={loading}
            onStudyHoursChange={setStudyHours}
            onPreferredTimeChange={setPreferredTime}
            onToggleTimeSlot={toggleTimeSlot}
            onHourChange={handleHourChange}
            onSubmit={handleSaveSchedule}
          />
        )}

        {step === "create_goal" && (
          <GoalsCreateStep
            subjects={subjects}
            selectedSubjectId={selectedSubjectId}
            targetScore={targetScore}
            deadline={deadline}
            userMessage={userMessage}
            loading={loading}
            onSubjectChange={setSelectedSubjectId}
            onTargetScoreChange={setTargetScore}
            onDeadlineChange={setDeadline}
            onUserMessageChange={setUserMessage}
            onScheduleEditClick={() => setStep("setup_schedule")}
            onSubmit={handleCreateDraft}
          />
        )}

        {step === "roadmap_draft" && draft && (
          <GoalsDraftStep
            draft={draft}
            subjects={subjects}
            selectedSubjectId={selectedSubjectId}
            targetScore={targetScore}
            deadline={deadline}
            chatMessage={chatMessage}
            chatLoading={chatLoading}
            loading={loading}
            onChatMessageChange={setChatMessage}
            onSendMessage={handleSendMessageToAI}
            onConfirm={handleConfirmRoadmap}
            onCancelDraft={handleCancelDraft}
          />
        )}

        {step === "success" && <GoalsSuccessStep />}
      </AnimatePresence>
    </div>
  );
}
