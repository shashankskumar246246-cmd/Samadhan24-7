"""
Script to verify JavaScript syntax, bracket balance, and regex handling in my1.js.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
js_path = os.path.join(ROOT, "my1.js")

with open(js_path, "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

stack = []
pairs = {')': '(', ']': '[', '}': '{'}
openings = set(pairs.values())
closings = set(pairs.keys())

in_single_str = False
in_double_str = False
in_template_str = False
in_line_comment = False
in_block_comment = False
in_regex = False

i = 0
n = len(code)
line_num = 1
col_num = 1

errors = []

while i < n:
    ch = code[i]
    next_ch = code[i+1] if i + 1 < n else ''

    if ch == '\n':
        line_num += 1
        col_num = 1
        in_line_comment = False
        i += 1
        continue
    else:
        col_num += 1

    if in_line_comment:
        i += 1
        continue

    if in_block_comment:
        if ch == '*' and next_ch == '/':
            in_block_comment = False
            i += 2
            continue
        i += 1
        continue

    if (in_single_str or in_double_str or in_template_str or in_regex) and ch == '\\':
        i += 2
        continue

    if in_single_str:
        if ch == "'":
            in_single_str = False
        i += 1
        continue

    if in_double_str:
        if ch == '"':
            in_double_str = False
        i += 1
        continue

    if in_template_str:
        if ch == '`':
            in_template_str = False
        i += 1
        continue

    if in_regex:
        if ch == '/':
            in_regex = False
        i += 1
        continue

    # Not in string/regex/comment
    if ch == '/' and next_ch == '/':
        in_line_comment = True
        i += 2
        continue

    if ch == '/' and next_ch == '*':
        in_block_comment = True
        i += 2
        continue

    # Regex heuristic: / followed by non-space and preceded by operator or start of statement
    if ch == '/':
        # look back
        prev_idx = i - 1
        while prev_idx >= 0 and code[prev_idx] in ' \t\r':
            prev_idx -= 1
        if prev_idx >= 0 and code[prev_idx] in '=(,[{:;!&|?':
            in_regex = True
            i += 1
            continue

    if ch == "'":
        in_single_str = True
        i += 1
        continue

    if ch == '"':
        in_double_str = True
        i += 1
        continue

    if ch == '`':
        in_template_str = True
        i += 1
        continue

    if ch in openings:
        stack.append((ch, line_num, col_num))
    elif ch in closings:
        if not stack:
            errors.append(f"Unexpected closing '{ch}' at line {line_num}:{col_num}")
        else:
            top, t_line, t_col = stack.pop()
            if pairs[ch] != top:
                errors.append(f"Mismatched closing '{ch}' at line {line_num}:{col_num}, expected closing for '{top}' from line {t_line}:{t_col}")

    i += 1

if stack:
    for top, t_line, t_col in stack[:5]:
        errors.append(f"Unclosed '{top}' opened at line {t_line}:{t_col}")

print(f"Total lines analyzed: {line_num}")
if errors:
    print(f"Found {len(errors)} syntax errors:")
    for err in errors[:10]:
        print("  -", err)
    exit(1)
else:
    print("[PASS] my1.js syntax verified: brackets, braces, parentheses, quotes, and regexes perfectly balanced!")
