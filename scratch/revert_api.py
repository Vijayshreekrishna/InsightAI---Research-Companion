import os

file_path = r'c:\Users\vijay\Downloads\vsk\I-AI\utils\api.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Update call_api
for i, line in enumerate(lines):
    if 'path == "/format-paper":' in line:
        lines[i+1] = '        return generate_formatted_paper(payload.get("title", ""), payload.get("text", ""))\n'
        # Remove subsequent lines until else
        j = i + 2
        while j < len(lines) and 'else:' not in lines[j]:
            lines.pop(j)
        break

# Update generate_formatted_paper
start_index = -1
for i, line in enumerate(lines):
    if 'def generate_formatted_paper' in line:
        start_index = i
        break

if start_index != -1:
    new_func = [
        'def generate_formatted_paper(title: str, text: str) -> dict:\n',
        '    """Structure raw research text into high-quality academic sections with strict constraints."""\n',
        '    provider = get_llm_provider()\n',
        '    prompt = f"""\n',
        '    You are a mechanical academic organizer. Your ONLY task is to take the provided raw research text and sort it into the correct academic sections.\n',
        '    \n',
        '    CONSTRAINTS:\n',
        '    1. Title: {title}\n',
        '\n',
        '    CRITICAL QUALITY INSTRUCTIONS:\n',
        '    - **NO RE-WRITING**: This is the absolute priority. Do NOT rephrase, do NOT improve grammar, and do NOT change a single word of the SOURCE RESEARCH TEXT.\n',
        '    - **Literal Sorting**: Take the sentences exactly as they are and place them into the appropriate section: Abstract, Keywords, Introduction, Literature Review, Methodology, Results, Conclusion, Future Scope, References.\n',
        '    - **No Hallucinations**: Do NOT generate any background info or analysis that is not in the source text.\n',
        '    - **No Placeholders**: Do NOT use "{{...}}" or "[Insert here]". \n',
        '    \n',
        '    Return your answer as a valid JSON object with these exact keys:\n',
        '    "title", "abstract", "keywords", "introduction", "lit_review", "methodology", "results", "conclusion", "future_scope", "references"\n',
        '\n',
        '    SOURCE RESEARCH TEXT:\n',
        '    {_truncate(text, 15000)}\n',
        '    """\n',
        '    response_text = provider.generate_content(prompt)\n',
        '    return _extract_json(response_text)\n'
    ]
    lines[start_index:] = new_func
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Successfully reverted api.py")
else:
    print("Could not find function")
