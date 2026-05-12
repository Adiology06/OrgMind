from langchain_groq import ChatGroq
from state.schema import AgentState, new_state
from dotenv import load_dotenv
from datetime import datetime
import os, json

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # stronger model for code
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1,
)


def fix_code(code: str, filename: str, language: str) -> dict:
    print(f"\n💻 IT Agent — Code Fixer: {filename}")
    print("─" * 55)
    print(f"  Language : {language}")
    print(f"  Lines    : {len(code.splitlines())}")

    prompt = f"""
You are an expert {language} developer and debugger.
Analyze this code from file '{filename}' and fix ALL bugs, errors, and issues.

CODE:
```{language}
{code}
```

Reply in this EXACT JSON format only, no markdown outside JSON:
{{
  "has_errors": true,
  "errors_found": [
    {{"line": 5, "error": "description", "severity": "high/medium/low"}}
  ],
  "fixed_code": "complete corrected code here",
  "changes_made": ["change 1", "change 2"],
  "explanation": "2 sentence summary of what was wrong",
  "best_practices": ["tip 1", "tip 2"]
}}
"""
    response = llm.invoke(prompt)
    raw      = response.content.strip()

    # extract JSON
    import re
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    try:
        result = json.loads(match.group()) if match else {}
    except:
        result = {
            "has_errors":    True,
            "errors_found":  [],
            "fixed_code":    code,
            "changes_made":  ["Could not parse — raw response returned"],
            "explanation":   raw[:200],
            "best_practices":[]
        }

    print(f"  Errors found : {len(result.get('errors_found', []))}")
    for err in result.get('errors_found', []):
        flag = "🔴" if err.get('severity') == 'high' else "🟡"
        print(f"  {flag} Line {err.get('line','?'):3} | {err.get('error','')[:60]}")

    print(f"\n  Changes made:")
    for c in result.get('changes_made', []):
        print(f"     ✅ {c}")

    print(f"\n  💡 {result.get('explanation','')[:100]}")

    return {
        "filename":       filename,
        "language":       language,
        "original_lines": len(code.splitlines()),
        "has_errors":     result.get("has_errors", False),
        "errors_found":   result.get("errors_found", []),
        "fixed_code":     result.get("fixed_code", code),
        "changes_made":   result.get("changes_made", []),
        "explanation":    result.get("explanation", ""),
        "best_practices": result.get("best_practices", []),
        "timestamp":      datetime.now().isoformat(),
    }


def review_code(code: str, filename: str, language: str) -> dict:
    print(f"\n🔍 IT Agent — Code Review: {filename}")
    print("─" * 55)

    prompt = f"""
Do a professional code review of this {language} code:

```{language}
{code}
```

Reply in JSON only:
{{
  "quality_score": 75,
  "security_issues": ["issue1"],
  "performance_issues": ["issue1"],
  "maintainability": "good/fair/poor",
  "suggestions": ["suggestion1", "suggestion2"],
  "summary": "2 sentence review"
}}
"""
    response = llm.invoke(prompt)
    raw      = response.content.strip()
    import re
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    try:
        result = json.loads(match.group()) if match else {}
    except:
        result = {"quality_score": 0, "summary": raw[:200]}

    print(f"  Quality Score : {result.get('quality_score', 0)}/100")
    print(f"  Maintainability: {result.get('maintainability','')}")
    print(f"  Security Issues: {len(result.get('security_issues',[]))}")
    print(f"  Summary: {result.get('summary','')[:80]}")

    return result


def run_it_coder(action: str, **kwargs) -> AgentState:
    state = new_state(task=f"ITCoder:{action}", agent="it_dev", priority="medium")

    if action == "fix":
        result = fix_code(
            code=kwargs.get("code", ""),
            filename=kwargs.get("filename", "code.py"),
            language=kwargs.get("language", "python"),
        )
    elif action == "review":
        result = review_code(
            code=kwargs.get("code", ""),
            filename=kwargs.get("filename", "code.py"),
            language=kwargs.get("language", "python"),
        )
    else:
        result = {"error": f"Unknown action: {action}"}

    state["result"]     = result
    state["updated_at"] = datetime.now().isoformat()
    return state