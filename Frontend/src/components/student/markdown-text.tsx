"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { Check, Copy, Code2 } from "lucide-react";

interface MarkdownTextProps {
  content?: string;
  className?: string;
}

function CodeBlock({ language, code }: { language: string; code: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-4 rounded-md overflow-hidden border border-zinc-800 bg-zinc-950 text-zinc-100 shadow-xl font-mono text-xs text-left">
      <div className="flex items-center justify-between px-4 py-2.5 bg-zinc-900 border-b border-zinc-800 text-zinc-400">
        <div className="flex items-center gap-2 font-bold uppercase tracking-wider text-[11px] text-indigo-400">
          <Code2 className="w-3.5 h-3.5" />
          <span>{language || "code"}</span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-white transition-all text-[11px] font-sans font-semibold cursor-pointer"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400">Đã chép</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Sao chép</span>
            </>
          )}
        </button>
      </div>
      <pre className="p-4 overflow-x-auto leading-relaxed text-zinc-200 selection:bg-indigo-500 selection:text-white">
        <code>{code}</code>
      </pre>
    </div>
  );
}

function autoWrapCode(text: string): string {
  if (!text) return text;
  if (text.includes("```") || text.includes("`")) return text;

  // Pattern 1: "Cho đoạn mã: <code_snippet> <câu_hỏi>?"
  const codeRegex = /(Cho\s+(?:đoạn\s+mã|đoạn\s+code|chương\s+trình|hàm|phương\s+thức|khối\s+mã):?)\s*([\s\S]+?)(?=(?:Hỏi|Giá trị|Kết quả|Đâu là|Sau khi|Khi|Cho|Thì|Bao nhiêu|Biến|Output|\?|$))/i;
  const match = text.match(codeRegex);
  if (match) {
    const label = match[1];
    const potentialCode = match[2].trim();
    const restOfText = text.slice(match.index! + match[0].length).trim();
    
    const isCodeLike = /(?:int|double|float|char|boolean|String|final|public|static|void|class|def|let|const|var|return|if|for|while|struct|import)\b|[=;]/.test(potentialCode);
    if (isCodeLike) {
      return `${label}\n\`\`\`java\n${potentialCode}\n\`\`\`\n${restOfText}`;
    }
  }

  // Pattern 2: Cụm khai báo biến/phép gán mã nguồn nằm giữa văn bản: double d = 9.78; int i = (int) d;
  const inlineCodeRegex = /\b((?:int|double|float|char|boolean|String|final|let|const|var)\s+[a-zA-Z_$][a-zA-Z0-9_$]*\s*=[^;.!?\n]+;(?:\s*(?:int|double|float|char|boolean|String|final|let|const|var)\s+[a-zA-Z_$][a-zA-Z0-9_$]*\s*=[^;.!?\n]+;)*)/gi;

  if (inlineCodeRegex.test(text)) {
    return text.replace(inlineCodeRegex, (m) => `\n\`\`\`java\n${m.trim()}\n\`\`\`\n`);
  }

  return text;
}

export function MarkdownText({ content, className = "" }: MarkdownTextProps) {
  if (!content) return null;

  // Tự động bọc đoạn mã nguồn trong câu hỏi nếu chưa có markdown backtick
  const formattedContent = autoWrapCode(content);

  // Xử lý chuẩn hóa cú pháp LaTeX nếu có dạng \(...\) hoặc \[...\]
  const normalizedContent = formattedContent
    .replace(/\\\[([\s\S]*?)\\\]/g, "$$$$1$$")
    .replace(/\\\(([\s\S]*?)\\\)/g, "$$1$");

  return (
    <div className={`markdown-body space-y-3 leading-relaxed text-zinc-800 dark:text-zinc-200 text-sm text-left ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          h1: ({ children }) => (
            <h1 className="text-xl font-black text-zinc-950 dark:text-white mt-6 mb-3 border-b border-zinc-200 dark:border-zinc-800 pb-2 flex items-center gap-2">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-lg font-black text-indigo-600 dark:text-indigo-400 mt-5 mb-2.5">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-base font-extrabold text-zinc-900 dark:text-zinc-100 mt-4 mb-2">
              {children}
            </h3>
          ),
          p: ({ children }) => <p className="mb-3 leading-relaxed font-medium text-zinc-700 dark:text-zinc-300">{children}</p>,
          strong: ({ children }) => <strong className="font-extrabold text-zinc-950 dark:text-white">{children}</strong>,
          em: ({ children }) => <em className="italic text-indigo-600 dark:text-indigo-400">{children}</em>,
          ul: ({ children }) => <ul className="list-disc pl-5 space-y-1.5 my-3 text-zinc-700 dark:text-zinc-300 font-medium">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal pl-5 space-y-1.5 my-3 text-zinc-700 dark:text-zinc-300 font-medium">{children}</ol>,
          li: ({ children }) => <li className="leading-relaxed">{children}</li>,
          blockquote: ({ children }) => (
            <blockquote className="my-4 border-l-4 border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/20 p-4 rounded-r-xl italic text-zinc-700 dark:text-zinc-300">
              {children}
            </blockquote>
          ),
          table: ({ children }) => (
            <div className="my-4 overflow-x-auto rounded-md border border-zinc-200 dark:border-zinc-800 shadow-sm">
              <table className="w-full text-left border-collapse text-xs">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-zinc-100 dark:bg-zinc-800/80 border-b border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-white font-bold">
              {children}
            </thead>
          ),
          tbody: ({ children }) => <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">{children}</tbody>,
          tr: ({ children }) => <tr className="hover:bg-zinc-50/80 dark:hover:bg-zinc-800/40 transition-colors">{children}</tr>,
          th: ({ children }) => <th className="p-3 font-extrabold uppercase text-[11px] tracking-wider text-indigo-600 dark:text-indigo-400">{children}</th>,
          td: ({ children }) => <td className="p-3 font-medium text-zinc-700 dark:text-zinc-300">{children}</td>,
          code: ({ node, inline, className, children, ...props }: any) => {
            const match = /language-(\w+)/.exec(className || "");
            const codeString = String(children).replace(/\n$/, "");

            if (!inline && (match || codeString.includes("\n"))) {
              return <CodeBlock language={match ? match[1] : ""} code={codeString} />;
            }

            return (
              <code
                className="px-1.5 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 font-mono text-[12px] border border-indigo-100 dark:border-indigo-900/40 font-bold"
                {...props}
              >
                {children}
              </code>
            );
          },
        }}
      >
        {normalizedContent}
      </ReactMarkdown>
    </div>
  );
}

