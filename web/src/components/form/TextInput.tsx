import React, { useState } from "react";

interface TextInputProps {
  id: string;
  name: string;
  label: string;
  type?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  error?: string;
  autoComplete?: string;
  required?: boolean;
  placeholder?: string;
  showPasswordToggle?: boolean;
}

const TextInput: React.FC<TextInputProps> = ({
  id,
  name,
  label,
  type = "text",
  value,
  onChange,
  error,
  autoComplete,
  required = false,
  placeholder = " ",
  showPasswordToggle = false,
}) => {
  const [showPassword, setShowPassword] = useState(false);

  const inputType = type === "password" && showPassword ? "text" : type;

  return (
    <div className="relative">
      <input
        id={id}
        name={name}
        type={inputType}
        value={value}
        onChange={onChange}
        required={required}
        autoComplete={autoComplete}
        className={`peer appearance-none block w-full px-3 pt-5 pb-2 border ${
          error
            ? "border-red-500 dark:border-red-400"
            : "border-gray-300 dark:border-gray-600"
        } rounded-md focus:outline-none focus:ring-2 ${
          error ? "focus:ring-red-500" : "focus:ring-indigo-500"
        } focus:border-transparent text-gray-900 dark:text-gray-100 bg-transparent transition-all duration-200`}
        placeholder={placeholder}
      />
      <label
        htmlFor={id}
        className={`absolute top-2 left-3 text-gray-500 dark:text-gray-400 text-xs transition-all duration-200 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-500 peer-placeholder-shown:dark:text-gray-400 peer-placeholder-shown:top-3.5 peer-focus:top-2 peer-focus:text-xs ${
          error
            ? "text-red-500 dark:text-red-400 peer-focus:text-red-500 peer-focus:dark:text-red-400"
            : "peer-focus:text-indigo-600 peer-focus:dark:text-indigo-400"
        }`}
      >
        {label}
      </label>

      {showPasswordToggle && type === "password" && (
        <button
          type="button"
          className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
          onClick={() => setShowPassword(!showPassword)}
          tabIndex={-1}
        >
          {showPassword ? (
            <svg
              className="h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
              />
            </svg>
          ) : (
            <svg
              className="h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
              />
            </svg>
          )}
        </button>
      )}

      {error && (
        <p className="mt-1 text-sm text-red-500 dark:text-red-400">{error}</p>
      )}
    </div>
  );
};

export default TextInput;
