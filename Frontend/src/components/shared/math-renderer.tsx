"use client";

import React, { useEffect, useState } from "react";

interface MathRendererProps {
  content: string;
  className?: string;
}

declare global {
  interface Window {
    katex?: {
      renderToString: (
        text: string,
        options?: { displayMode?: boolean; throwOnError?: boolean }
      ) => string;
    };
  }
}

export function MathRenderer({ content, className = "" }: MathRendererProps) {
  const [isKatexLoaded, setIsKatexLoaded] = useState<boolean>(
    typeof window !== "undefined" && !!window.katex
  );

  useEffect(() => {
    if (typeof window === "undefined") return;

    if (window.katex) {
      setIsKatexLoaded(true);
      return;
    }

    // Load KaTeX CSS if not present
    if (!document.getElementById("katex-css")) {
      const link = document.createElement("link");
      link.id = "katex-css";
      link.rel = "stylesheet";
      link.href =
        "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css";
      document.head.appendChild(link);
    }

    // Load KaTeX JS if not present
    if (!document.getElementById("katex-js")) {
      const script = document.createElement("script");
      script.id = "katex-js";
      script.src =
        "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js";
      script.onload = () => setIsKatexLoaded(true);
      document.head.appendChild(script);
    } else {
      const checkInterval = setInterval(() => {
        if (window.katex) {
          setIsKatexLoaded(true);
          clearInterval(checkInterval);
        }
      }, 100);
      return () => clearInterval(checkInterval);
    }
  }, []);

  if (!content) return null;

  // Split content by $$ ... $$ (block) and $ ... $ (inline)
  const renderFormattedText = () => {
    if (!isKatexLoaded || !window.katex) {
      return <span className={className}>{content}</span>;
    }

    try {
      // Regex for block $$...$$ and inline $...$
      const parts: React.ReactNode[] = [];
      const regex = /(\$\$[\s\S]*?\$\$|\$[\s\S]*?\$)/g;
      let lastIndex = 0;
      let match: RegExpExecArray | null;

      while ((match = regex.exec(content)) !== null) {
        // Text before math
        if (match.index > lastIndex) {
          parts.push(content.substring(lastIndex, match.index));
        }

        const mathExpr = match[0];
        const isBlock = mathExpr.startsWith("$$") && mathExpr.endsWith("$$");
        const rawLatex = isBlock
          ? mathExpr.slice(2, -2).trim()
          : mathExpr.slice(1, -1).trim();

        try {
          const html = window.katex.renderToString(rawLatex, {
            displayMode: isBlock,
            throwOnError: false,
          });

          parts.push(
            <span
              key={match.index}
              dangerouslySetInnerHTML={{ __html: html }}
              className={isBlock ? "block my-2 text-center" : "inline-block px-0.5"}
            />
          );
        } catch (e) {
          parts.push(mathExpr);
        }

        lastIndex = regex.lastIndex;
      }

      if (lastIndex < content.length) {
        parts.push(content.substring(lastIndex));
      }

      return <span className={className}>{parts}</span>;
    } catch (err) {
      return <span className={className}>{content}</span>;
    }
  };

  return renderFormattedText();
}
