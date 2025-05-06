export function setTheme(theme: string) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
}

export function getTheme() {
  if (typeof document == "undefined") return "light";
  return document.documentElement.getAttribute("data-theme");
}
