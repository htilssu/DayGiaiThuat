/**
 * Utility functions for content parsing and rendering
 */

export function isMarkdownContent(content: string): boolean {
  // Check for common markdown indicators
  const markdownPatterns = [
    /^#+\s/m,           // Headers
    /\*\*.*\*\*/,       // Bold text
    /\*.*\*/,           // Italic text
    /\[.*\]\(.*\)/,     // Links
    /^\s*-\s/m,         // Unordered lists
    /^\s*\d+\.\s/m,     // Ordered lists
    /```[\s\S]*```/,    // Code blocks
    /`.*`/,             // Inline code
    /^\s*>\s/m,         // Blockquotes
    /^\|.*\|$/m,        // Tables
    /^\s*---\s*$/m,     // Horizontal rules
  ];

  return markdownPatterns.some(pattern => pattern.test(content));
}

export function isHtmlContent(content: string): boolean {
  // Check for HTML tags
  const htmlPattern = /<[^>]*>/;
  return htmlPattern.test(content);
}

export function sanitizeContent(content: string): string {
  // Remove potentially dangerous HTML tags but keep formatting
  const dangerousTags = ['script', 'iframe', 'object', 'embed', 'form', 'input', 'button'];
  let sanitized = content;
  
  dangerousTags.forEach(tag => {
    const regex = new RegExp(`<${tag}[^>]*>.*?</${tag}>`, 'gis');
    sanitized = sanitized.replace(regex, '');
  });
  
  return sanitized;
}

export function formatCodeLanguage(content: string): { code: string; language?: string } {
  // Extract language from code block if present
  const codeBlockMatch = content.match(/```(\w+)?\n([\s\S]*?)```/);
  if (codeBlockMatch) {
    return {
      code: codeBlockMatch[2].trim(),
      language: codeBlockMatch[1]
    };
  }
  
  return { code: content };
}

export function processLessonContent(content: string, type: string): {
  content: string;
  isMarkdown: boolean;
  isHtml: boolean;
  language?: string;
} {
  const sanitized = sanitizeContent(content);
  
  if (type === 'code') {
    const { code, language } = formatCodeLanguage(sanitized);
    return {
      content: code,
      isMarkdown: false,
      isHtml: false,
      language
    };
  }
  
  return {
    content: sanitized,
    isMarkdown: isMarkdownContent(sanitized),
    isHtml: isHtmlContent(sanitized)
  };
}
