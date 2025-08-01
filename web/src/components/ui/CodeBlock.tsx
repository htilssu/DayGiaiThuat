import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow, coy } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useState } from 'react';

interface CodeBlockProps {
  code: string;
  language?: string;
  title?: string;
  showLineNumbers?: boolean;
  className?: string;
}

const SUPPORTED_LANGUAGES = [
  'javascript', 'typescript', 'python', 'java', 'cpp', 'c', 'csharp',
  'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'html',
  'css', 'scss', 'sass', 'sql', 'json', 'xml', 'yaml', 'markdown',
  'bash', 'shell', 'powershell', 'dockerfile', 'nginx', 'apache'
];

function detectLanguage(code: string): string {
  // Simple language detection based on common patterns
  if (code.includes('def ') || code.includes('import ') || code.includes('print(')) return 'python';
  if (code.includes('function ') || code.includes('const ') || code.includes('let ')) return 'javascript';
  if (code.includes('interface ') || code.includes(': string') || code.includes(': number')) return 'typescript';
  if (code.includes('public class ') || code.includes('System.out.println')) return 'java';
  if (code.includes('#include') || code.includes('int main(')) return 'cpp';
  if (code.includes('using namespace') || code.includes('std::')) return 'cpp';
  if (code.includes('<!DOCTYPE') || code.includes('<html>')) return 'html';
  if (code.includes('SELECT ') || code.includes('FROM ') || code.includes('WHERE ')) return 'sql';
  if (code.includes('{') && code.includes('"')) return 'json';
  
  return 'text';
}

export function CodeBlock({ 
  code, 
  language, 
  title, 
  showLineNumbers = true, 
  className = "" 
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false);
  const detectedLanguage = language || detectLanguage(code);
  const finalLanguage = SUPPORTED_LANGUAGES.includes(detectedLanguage) ? detectedLanguage : 'text';

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  return (
    <div className={`bg-gray-900 rounded-lg overflow-hidden shadow-lg ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between bg-gray-800 px-4 py-2 border-b border-gray-700">
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          </div>
          {title && (
            <span className="text-gray-300 text-sm font-medium ml-2">{title}</span>
          )}
          <span className="text-gray-400 text-xs bg-gray-700 px-2 py-1 rounded">
            {finalLanguage}
          </span>
        </div>
        
        <button
          onClick={copyToClipboard}
          className="text-gray-400 hover:text-white transition-colors duration-200 p-1 rounded"
          title="Copy to clipboard"
        >
          {copied ? (
            <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          )}
        </button>
      </div>

      {/* Code Content */}
      <div className="overflow-x-auto">
        <SyntaxHighlighter
          language={finalLanguage}
          style={tomorrow}
          showLineNumbers={showLineNumbers}
          lineNumberStyle={{
            minWidth: '3em',
            paddingRight: '1em',
            textAlign: 'right',
            color: '#6b7280',
            backgroundColor: 'transparent',
            borderRight: '1px solid #374151',
            marginRight: '1em'
          }}
          customStyle={{
            margin: 0,
            padding: '1rem',
            backgroundColor: 'transparent',
            fontSize: '0.875rem',
            lineHeight: '1.5'
          }}
          codeTagProps={{
            style: {
              fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace'
            }
          }}
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}
