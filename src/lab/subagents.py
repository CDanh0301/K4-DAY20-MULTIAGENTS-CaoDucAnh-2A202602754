"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": "Use to inspect the workspace, read files, analyze directory structure, review specifications or inspect logs before modifying files. Returns findings; does not modify files.",
            "system_prompt": (
                "You are an investigative subagent. Your role is to carefully read workspace files, "
                "read task instructions, examine code, logs, and data formats, and report precise facts. "
                "Never modify or delete any files. Report your findings clearly and concisely."
            ),
        },
        {
            "name": "implementer",
            "description": "Use to execute code modifications, run tests, fix errors, clean datasets, or parse logs in the workspace according to plan. Reports execution results.",
            "system_prompt": (
                "You are an implementation subagent. Your role is to make precise edits to workspace files, "
                "run Python scripts or test suites using the shell, verify fixes, and report exact changes made."
            ),
        },
        {
            "name": "reviewer",
            "description": "Use to independently review modified files, run test suites or verification scripts, check edge cases, and verify against task specifications and guidelines. Does not modify files.",
            "system_prompt": (
                "You are a quality assurance and verification subagent. Your role is to independently review "
                "workspace changes, execute validation tests, check for missing edge cases or formatting errors, "
                "and ensure all specifications are met. Never modify files."
            ),
        },
    ]
