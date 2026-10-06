# Pseudo-code 01 - `src/lab/agent.py`

**Mục tiêu.** Dựng tác tử (agent) bằng Deep Agents: môi trường thực thi (backend) và hai chế độ (mode): `single` và `subagents`.

**Kiểm tra.** `pytest tests/test_02_agent.py` (chạy ngoại tuyến - offline, không tốn token).

Bốn hằng số `PATHS_NOTE`, `BASE_PROMPT`, `SKILLS_NOTE`, `SUBAGENTS_NOTE` đã được cung cấp sẵn trong `agent.py` và **không sửa**: mọi sinh viên dùng cùng một system prompt thì điều kiện `baseline` mới so sánh được giữa các sinh viên.

---

## Quy ước đường dẫn (đọc trước khi cài đặt)

Tác tử có hai nhóm công cụ truy cập tệp:

| Nhóm | Công cụ | Cách hiểu đường dẫn |
|---|---|---|
| Công cụ tệp | `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` | Đường dẫn ảo (virtual path); gốc của chúng là `root_dir`. Chấp nhận cả `/workspace/x` lẫn `workspace/x`. |
| Shell | `execute` | Lệnh chạy thật trên hệ điều hành, thư mục làm việc là `root_dir`. Thư mục `/workspace` **không tồn tại** ở gốc hệ thống tệp thật; chỉ dạng tương đối `workspace/x` dùng được. |

Do đó mọi đường dẫn trong đề bài và trong `BASE_PROMPT` đều ở dạng **tương đối** (`workspace/...`, `skills/...`), dùng được ở cả hai nhóm công cụ. Test `test_file_tools_and_shell_share_relative_paths` kiểm tra điều này.

---

## Bước 1. `make_backend(sandbox)`

Backend là nơi tác tử đọc, ghi tệp và chạy lệnh shell. Deep Agents cung cấp `LocalShellBackend`.

```text
HÀM make_backend(sandbox):
    env = {
        "PATH": <thư mục chứa python đang chạy, lấy từ sys.executable>
                + ":/usr/local/bin:/usr/bin:/bin",
        "HOME": str(sandbox),
        "PYTHONDONTWRITEBYTECODE": "1",          # không sinh __pycache__ trong workspace
    }
    TRẢ VỀ LocalShellBackend(
        root_dir = sandbox,
        virtual_mode = True,                      # đường dẫn của công cụ tệp là đường dẫn ảo, gốc = sandbox
        inherit_env = False,                      # KHÔNG kế thừa biến môi trường của tiến trình cha
        env = env,
        timeout = 120,                            # giây, giới hạn thời gian mỗi lệnh
    )
```

Hai lỗi thường gặp:

| Cấu hình | Hậu quả |
|---|---|
| `inherit_env=False` và không truyền `env` | Shell của tác tử không có `PATH`, lệnh `python` báo `command not found`. |
| `inherit_env=True` | Shell của tác tử đọc được toàn bộ biến môi trường, gồm khóa API. Đây là lỗi bảo mật. |

---

## Bước 2. `build_agent(sandbox, mode, use_skills, model)`

```text
HÀM build_agent(sandbox, mode="single", use_skills=False, model=None):
    NẾU mode không thuộc {"single", "subagents"}: ném ValueError

    kwargs = {}
    prompt = BASE_PROMPT

    NẾU mode == "subagents":
        # subagent KHÔNG nhận BASE_PROMPT, nên nối PATHS_NOTE vào system_prompt của từng subagent;
        # nếu không, subagent trộn lẫn "/workspace/x" và "workspace/x" và báo "không tìm thấy tệp"
        kwargs["subagents"] = [ {**sub, "system_prompt": sub["system_prompt"] + " " + PATHS_NOTE}
                                 CHO MỖI sub TRONG get_subagents() ]          # file subagents.py
        prompt = prompt + SUBAGENTS_NOTE

    NẾU use_skills:
        kwargs["skills"] = ["/skills/"]                # đường dẫn ảo, tính từ root_dir của backend
        prompt = prompt + SKILLS_NOTE

    TRẢ VỀ create_deep_agent(
        model         = model HOẶC make_model(),         # make_model() có sẵn trong model.py
        system_prompt = prompt,
        backend       = make_backend(sandbox),
        **kwargs,
    )
```

Ghi chú kỹ thuật:

1. `create_deep_agent` luôn thêm công cụ `task` và một subagent mặc định tên `general-purpose`. Vì vậy chế độ `single` vẫn là "tác tử Deep Agents mặc định" (default agent).
2. Chế độ `subagents` chỉ **thêm** các subagent tự định nghĩa. Tác tử chính tự quyết định có giao việc hay không; `SUBAGENTS_NOTE` chỉ khuyến khích. Ghi nhận cả trường hợp subagent không được gọi lần nào (`subagent_calls = 0` trong `run.json`).
3. Với `skills=["/skills/"]`, Deep Agents chỉ đọc phần tiêu đề (frontmatter) của mỗi `SKILL.md` khi khởi động và nạp toàn bộ nội dung khi tác tử cần (progressive disclosure - nạp dần). Skill được dùng hay không phụ thuộc vào `description` và vào `SKILLS_NOTE`.
4. Không dùng tham số `permissions=` để khóa thư mục `skills`. Deep Agents ném `NotImplementedError` khi kết hợp `permissions` với backend có khả năng chạy lệnh. Việc phát hiện sửa skill được thực hiện trong `run_task` bằng cách băm (hash) thư mục `skills`.
5. Tham số `model` cho phép truyền mô hình giả (`ScriptedChatModel`) trong test.

---

## Kiểm tra nhanh bằng tay (tùy chọn, tốn token)

```python
from pathlib import Path
from lab.agent import build_agent
sandbox = Path("/tmp/sb"); (sandbox / "workspace").mkdir(parents=True, exist_ok=True)
agent = build_agent(sandbox)
out = agent.invoke({"messages": [{"role": "user", "content": "Create the file workspace/hello.txt containing hi"}]})
print(out["messages"][-1].content)
```
