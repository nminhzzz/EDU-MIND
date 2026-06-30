"use client";
import React from "react";

interface MarkdownTextProps {
  content?: string;
  className?: string;
}

export function MarkdownText({ content, className = "" }: MarkdownTextProps) {
  if (!content) return null;

  // Phân tách văn bản theo các cụm ký tự bọc trong **
  const parts = content.split(/(\*\*[^*]+\*\*)/g);

  return (
    <span className={`whitespace-pre-wrap break-words block ${className}`}>
      {parts.map((part, index) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return (
            <strong key={index} className="font-black text-zinc-950 dark:text-white">
              {part.slice(2, -2)}
            </strong>
          );
        }
        return part;
      })}
    </span>
  );
}
