"use client";

import React from "react";
import { MarkdownText } from "@/components/student/markdown-text";

interface MathRendererProps {
  content: string;
  className?: string;
}

export function MathRenderer({ content, className = "" }: MathRendererProps) {
  if (!content) return null;
  return <MarkdownText content={content} className={className} />;
}

