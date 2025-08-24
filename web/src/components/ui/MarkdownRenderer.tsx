import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { tomorrow } from "react-syntax-highlighter/dist/esm/styles/prism";
import { ReactElement } from "react";
import "@/styles/markdown-table.css";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

interface CodeProps {
  node?: unknown;
  inline?: boolean;
  className?: string;
  children?: React.ReactNode;
}

export function MarkdownRenderer({
  content,
  className = "",
}: MarkdownRendererProps) {
  return (
    <div className={`prose prose-slate max-w-none ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code: ({
            node,
            inline,
            className,
            children,
            ...props
          }: CodeProps) => {
            const match = /language-(\w+)/.exec(className || "");
            const language = match ? match[1] : "";

            return !inline && language ? (
              <SyntaxHighlighter
                style={tomorrow}
                language={language}
                PreTag="div"
                className="rounded-lg overflow-hidden"
                {...props}>
                {String(children).replace(/\n$/, "")}
              </SyntaxHighlighter>
            ) : (
              <code
                className={`${className} bg-foreground/10 px-2 py-1 rounded text-sm text-foreground`}
                {...props}>
                {children}
              </code>
            );
          },
          h1: ({ children }) => (
            <h1 className="text-3xl font-bold mb-4 text-foreground">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-2xl font-semibold mb-3 text-foreground">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-xl font-semibold mb-2 text-foreground">
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-lg font-semibold mb-2 text-foreground">
              {children}
            </h4>
          ),
          p: ({ children }) => (
            <p className="text-foreground/80 leading-relaxed">{children}</p>
          ),
          ul: ({ children }) => (
            <ul className="list-disc list-inside mb-4 ml-4 space-y-1 text-foreground/80">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside mb-4 ml-4 space-y-1 text-foreground/80">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="text-foreground/80">{children}</li>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-primary pl-4 py-2 mb-4 bg-primary/10 italic text-foreground/80">
              {children}
            </blockquote>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold text-foreground">
              {children}
            </strong>
          ),
          em: ({ children }) => (
            <em className="italic text-foreground/80">{children}</em>
          ),
          a: ({ href, children }) => (
            <a
              href={href}
              className="text-primary hover:text-primary/80 underline"
              target="_blank"
              rel="noopener noreferrer">
              {children}
            </a>
          ),
          table: ({ children }) => (
            <div className="markdown-table-wrapper overflow-x-auto mb-6">
              <table className="markdown-table">{children}</table>
            </div>
          ),
          thead: ({ children }) => <thead>{children}</thead>,
          tbody: ({ children }) => <tbody>{children}</tbody>,
          tr: ({ children, ...props }) => <tr {...props}>{children}</tr>,
          th: ({ children, style, ...props }) => {
            // Handle text alignment from markdown table syntax
            const textAlign = style?.textAlign || "left";
            const alignmentClass =
              textAlign === "center"
                ? "table-cell-center"
                : textAlign === "right"
                ? "table-cell-right"
                : "table-cell-left";

            return (
              <th className={alignmentClass} style={style} {...props}>
                {children}
              </th>
            );
          },
          td: ({ children, style, ...props }) => {
            // Handle text alignment from markdown table syntax
            const textAlign = style?.textAlign || "left";
            const alignmentClass =
              textAlign === "center"
                ? "table-cell-center"
                : textAlign === "right"
                ? "table-cell-right"
                : "table-cell-left";

            return (
              <td className={alignmentClass} style={style} {...props}>
                {children}
              </td>
            );
          },
          hr: () => <hr className="my-6 border-foreground/20" />,
        }}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
