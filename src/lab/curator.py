"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import re
from pathlib import Path

from .tasks import eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


import json
import logging
from .model import make_model
from .tasks import ROOT

logger = logging.getLogger(__name__)

CURATOR_PROMPT_TEMPLATE = """You write reusable Agent Skills for a software engineering and data analysis agent.
Below are the failed checks (check names and evaluator review comments/rules) and execution traces from previous learning task runs.
Identify common procedural errors and organizational rules (NOT specific answers or hardcoded constants), and write up to {max_skills} concise skills that help prevent these errors on NEW tasks of the same kind.

Rules:
- Generalize: Do not mention task IDs, specific input file names belonging to one task, or specific numbers/answers.
- Mentioning standard Acme organization conventions required by the house rules (e.g. output file conventions like clean.csv, tests/test_regressions.py, metadata key 'meta', etc.) is allowed and encouraged when they represent general rules.
- Each skill must have YAML frontmatter with `name` (lowercase letters, digits, and hyphens only, max 64 chars) and `description` (one sentence: when to use this skill, max 1024 chars), followed by an imperative checklist of at most 40 lines.
- Format each skill exactly as follows:
=== SKILL: <name> ===
---
name: <name>
description: <when to use this skill>
---
# <Title>

1. <Step 1>
2. <Step 2>
=== END ===

Failed runs feedback:
{runs_feedback}
"""


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file.

    Các bước: nạp run.json + trace.md -> (nếu không có check nào thất bại: in cảnh báo và trả về [] mà KHÔNG gọi LLM)
    -> dựng prompt -> model.invoke(prompt) -> parse_skill_blocks -> validate_skill(text, expected_name=name)
    -> ghi `<out_dir>/<name>/SKILL.md`. Mặc định `out_dir` = <gốc lab>/skills/auto (dùng `ROOT` từ lab.tasks).
    Giữ tối đa `max_skills` skill hợp lệ; skill không hợp lệ bị bỏ qua.
    Prompt chứa, với mỗi check thất bại, TÊN và trường `detail` (lời nhận xét của bot đánh giá: phát biểu quy tắc bị vi phạm)
    cùng phần cuối của vết (trace). Với tác vụ học, `detail` chỉ phát biểu quy tắc, không chứa đáp án.
    Tuyệt đối KHÔNG đưa dữ liệu của tác vụ đánh giá (role == "eval") vào prompt.
    model mặc định: make_model() (lab.model).
    Trả về: danh sách đường dẫn SKILL.md đã ghi.
    """
    if out_dir is None:
        out_path = ROOT / "skills" / "auto"
    else:
        out_path = Path(out_dir)

    source_path = Path(results_dir) / source_condition
    runs_with_failures = []

    if source_path.exists():
        for run_file in sorted(source_path.glob("*/run.json")):
            try:
                data = json.loads(run_file.read_text(encoding="utf-8"))
            except Exception:
                continue

            if data.get("role") != "learn":
                continue

            failed_checks = []
            for c in data.get("checks", []):
                if not c.get("passed", False):
                    failed_checks.append((c.get("name", ""), c.get("detail", "")))

            if not failed_checks:
                continue

            trace_file = run_file.parent / "trace.md"
            trace_tail = ""
            if trace_file.exists():
                trace_content = trace_file.read_text(encoding="utf-8")
                trace_tail = trace_content[-6000:]

            runs_with_failures.append({
                "task": data.get("task", run_file.parent.name),
                "failed": failed_checks,
                "trace": trace_tail,
            })

    if not runs_with_failures:
        print("Warning: No failed checks found in learning task runs. Skipping skill curation.")
        return []

    feedback_parts = []
    for r in runs_with_failures:
        feedback_parts.append(f"Task: {r['task']}")
        feedback_parts.append("Failed checks:")
        for name, detail in r["failed"]:
            feedback_parts.append(f"  - Check: {name}")
            if detail:
                feedback_parts.append(f"    Evaluator feedback: {detail}")
        if r["trace"]:
            feedback_parts.append("Trace snippet:")
            feedback_parts.append(r["trace"])
        feedback_parts.append("-" * 30)

    prompt = CURATOR_PROMPT_TEMPLATE.format(
        max_skills=max_skills,
        runs_feedback="\n".join(feedback_parts),
    )

    llm = model or make_model()
    reply = llm.invoke(prompt).content

    blocks = parse_skill_blocks(reply)
    written = []

    for name, text in blocks:
        if len(written) >= max_skills:
            break
        problems = validate_skill(text, expected_name=name)
        if problems:
            logger.warning("Rejecting skill '%s': %s", name, problems)
            continue

        skill_dir = out_path / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        file_path = skill_dir / "SKILL.md"
        file_path.write_text(text.strip() + "\n", encoding="utf-8")
        written.append(file_path)

    return written


if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)
