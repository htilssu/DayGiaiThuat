import React from "react";
import Monaco, { OnChange, Monaco as MonacoType } from "@monaco-editor/react";

interface MonacoEditorProps {
  value: string;
  language?: string;
  theme?: string;
  onChange?: (value: string) => void;
  height?: string | number;
  options?: Record<string, any>;
}

const MonacoEditor: React.FC<MonacoEditorProps> = ({
  value,
  language = "javascript",
  theme = "vs",
  onChange,
  height = 384, // 24rem (h-96)
  options = {},
}) => {
  return (
    <Monaco
      value={value}
      language={language}
      theme={theme}
      height={height}
      options={{
        fontSize: 16,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        wordWrap: "on",
        ...options,
      }}
      onChange={(val) => onChange?.(val ?? "")}
    />
  );
};

export default MonacoEditor;
