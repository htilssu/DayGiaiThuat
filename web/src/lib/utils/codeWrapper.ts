// Utility to wrap user code with a harness that reads stdin and calls the user's function

function detectFunctionName(code: string, language: string): string | null {
  // Try common patterns. Fallback to "solve" or "yourFunction" handled by caller
  if (language === "javascript" || language === "typescript") {
    const fnDecl = code.match(/function\s+([A-Za-z_$][\w$]*)\s*\(/);
    if (fnDecl) return fnDecl[1];
    const arrowFn = code.match(
      /(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*\(/
    );
    if (arrowFn) return arrowFn[1];
    const methodExport = code.match(
      /export\s+function\s+([A-Za-z_$][\w$]*)\s*\(/
    );
    if (methodExport) return methodExport[1];
    return null;
  }
  if (language === "python") {
    const pyFn = code.match(/def\s+([A-Za-z_][\w]*)\s*\(/);
    if (pyFn) return pyFn[1];
    return null;
  }
  return null;
}

function buildJsHarness(fnName: string): string {
  return `
const fs = require('fs');
const raw = fs.readFileSync(0, 'utf-8').trim();
let parsed;
try { parsed = JSON.parse(raw); } catch { parsed = raw; }

function __coerceInput(rawValue) {
  if (typeof rawValue !== 'string') return rawValue;
  const s = rawValue.trim();
  if (!s) return s;
  if ((s.startsWith('[') && s.endsWith(']')) || (s.startsWith('{') && s.endsWith('}'))) {
    try { return JSON.parse(s); } catch {}
  }
  const tokens = s.split(/[\s,]+/).filter(Boolean).map(tok => {
    if (/^-?\d+$/.test(tok)) return Number(tok);
    if (/^-?\d*\.\d+$/.test(tok)) return Number(tok);
    if ((tok.startsWith('[') && tok.endsWith(']')) || (tok.startsWith('{') && tok.endsWith('}'))) {
      try { return JSON.parse(tok); } catch { return tok; }
    }
    return tok;
  });
  if (tokens.length > 1) return tokens;
  return s;
}

const input = __coerceInput(parsed);

let __result;
try {
  if (Array.isArray(input)) {
    try { __result = ${fnName}(...input); }
    catch { __result = ${fnName}(input); }
  } else {
    __result = ${fnName}(input);
  }
} catch (e) {
  console.error(e && e.message ? e.message : String(e));
  process.exit(1);
}

if (typeof __result === 'object') {
  console.log(JSON.stringify(__result));
} else {
  console.log(String(__result));
}
`;
}

function buildPyHarness(fnName: string): string {
  return `
import sys, json
_raw = sys.stdin.read().strip()
def _coerce_input(s):
    if not isinstance(s, str):
        return s
    t = s.strip()
    if not t:
        return t
    if (t.startswith('[') and t.endswith(']')) or (t.startswith('{') and t.endswith('}')):
        try:
            return json.loads(t)
        except Exception:
            pass
    parts = [p for p in t.replace(',', ' ').split() if p]
    vals = []
    for p in parts:
        try:
            if '.' in p:
                vals.append(float(p))
            else:
                vals.append(int(p))
            continue
        except Exception:
            pass
        try:
            vals.append(json.loads(p))
            continue
        except Exception:
            pass
        vals.append(p)
    if len(vals) > 1:
        return vals
    return t

try:
    _parsed_json = json.loads(_raw)
except Exception:
    _parsed_json = _raw
_input = _coerce_input(_parsed_json)

def __call_solve(_p):
    try:
        if isinstance(_p, list):
            try:
                _res = ${fnName}(*_p)
            except TypeError:
                _res = ${fnName}(_p)
        else:
            _res = ${fnName}(_p)
        if isinstance(_res, (dict, list)):
            print(json.dumps(_res))
        else:
            print(_res)
    except Exception as e:
        print(str(e))
        raise

__call_solve(_input)
`;
}

export function wrapUserCode(code: string, language: string): string {
  const lang = (language || "").toLowerCase();
  const detected = detectFunctionName(code, lang);
  const fallbackName = code.includes("yourFunction") ? "yourFunction" : "solve";
  const fnName = detected || fallbackName;

  if (lang === "javascript" || lang === "typescript") {
    return `${code}\n\n${buildJsHarness(fnName)}`;
  }
  if (lang === "python") {
    return `${code}\n\n${buildPyHarness(fnName)}`;
  }
  // For other languages, return as-is (user must handle I/O)
  return code;
}
