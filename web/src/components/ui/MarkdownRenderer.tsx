import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { ReactElement } from 'react';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

interface CodeProps {
  node?: any;
  inline?: boolean;
  className?: string;
  children?: React.ReactNode;
}

export function MarkdownRenderer({ content, className = "" }: MarkdownRendererProps) {
  return (
    <div className={`prose prose-slate max-w-none ${className}`}>
      <ReactMarkdown
        components={{
          code: ({ node, inline, className, children, ...props }: CodeProps) => {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';

            return !inline && language ? (
              <SyntaxHighlighter
                style={tomorrow}
                language={language}
                PreTag="div"
                className="rounded-lg overflow-hidden"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className={`${className} bg-gray-100 px-2 py-1 rounded text-sm`} {...props}>
                {children}
              </code>
            );
          },
          h1: ({ children }) => (
            <h1 className="text-3xl font-bold mb-4 text-gray-900">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-2xl font-semibold mb-3 text-gray-800">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-xl font-semibold mb-2 text-gray-800">{children}</h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-lg font-semibold mb-2 text-gray-700">{children}</h4>
          ),
          p: ({ children }) => (
            <p className="text-gray-700 leading-relaxed">{children}</p>
          ),
          ul: ({ children }) => (
            <ul className="list-disc list-inside mb-4 ml-4 space-y-1 text-gray-700">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside mb-4 ml-4 space-y-1 text-gray-700">{children}</ol>
          ),
          li: ({ children }) => (
            <li className="text-gray-700">{children}</li>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-blue-500 pl-4 py-2 mb-4 bg-blue-50 italic text-gray-700">
              {children}
            </blockquote>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold text-gray-900">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="italic text-gray-700">{children}</em>
          ),
          a: ({ href, children }) => (
            <a
              href={href}
              className="text-blue-600 hover:text-blue-800 underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              {children}
            </a>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto mb-4">
              <table className="min-w-full border border-gray-300 rounded-lg overflow-hidden">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-gray-100">{children}</thead>
          ),
          tbody: ({ children }) => (
            <tbody className="divide-y divide-gray-200">{children}</tbody>
          ),
          tr: ({ children }) => (
            <tr>{children}</tr>
          ),
          th: ({ children }) => (
            <th className="px-4 py-2 text-left font-semibold text-gray-900 border-b border-gray-300">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-2 text-gray-700 border-b border-gray-200">
              {children}
            </td>
          ),
          hr: () => (
            <hr className="my-6 border-gray-300" />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
