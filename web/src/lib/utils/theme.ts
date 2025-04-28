export function setTheme(theme: string) {
  document.documentElement.setAttribute("data-theme", theme);
}

export function getTheme() {
  return document.documentElement.getAttribute("data-theme");
}
