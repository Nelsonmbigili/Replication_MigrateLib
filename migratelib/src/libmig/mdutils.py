def extract_code_lines(all_lines: list[str]) -> list[str]:
    """Get code block from markdown."""
    code_lines = []
    in_code = False
    for line in all_lines:
        if line.startswith("```"):
            in_code = not in_code
            continue

        if in_code:
            code_lines += [line]

    if not code_lines:
        code_lines = all_lines

    return code_lines


def extract_code(completion: str):
    completion_lines = completion.splitlines(keepends=True)
    code_lines = extract_code_lines(completion_lines)
    code_segment = "".join(code_lines)
    return code_segment
