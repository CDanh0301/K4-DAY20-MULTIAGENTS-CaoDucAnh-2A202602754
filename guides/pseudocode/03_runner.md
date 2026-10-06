# Pseudo-code 03 - `src/lab/runner.py`

**Mục tiêu.** Chạy một tác vụ dưới một điều kiện, đo lường, chấm điểm và ghi kết quả có thể tái lập.

**Kiểm tra.** `pytest tests/test_03_runner.py`.
**Chạy thật.** `python -m lab.runner --condition baseline --tasks learn`

Có sẵn, không cần viết: `render_trace` và `main` (trong `runner.py`), `get_task`, `list_tasks`, `prepare_sandbox`, `hash_dir` (trong `tasks.py`) và `grade` (trong `grading.py`).

---

## Bước 1 (việc bạn cài đặt). `run_task(task_id, condition, results_dir, model, recursion_limit)`

```text
HÀM run_task(...):
    cfg  = CONDITIONS[condition]
    task = get_task(task_id)
    skills_dir = ROOT / cfg["skills_dir"]  NẾU cfg["skills_dir"] ngược lại None
    out = Path(results_dir) / condition / task_id ; tạo thư mục
    sandbox = thư mục tạm MỚI (tempfile.mkdtemp), NẰM NGOÀI kho mã nguồn
    record = {"task", "condition", "role": task.role, "error": None, "timestamp": giờ UTC hiện tại, ISO-8601}

    THỬ:
        prepare_sandbox(task, sandbox, skills_dir)            # sao chép workspace (và skills) vào sandbox
        hash_truoc = hash_dir(sandbox/"skills")
        record["skills_sha256"] = hash_truoc                   # để giảng viên đối chiếu với skill đã đóng băng

        agent = build_agent(sandbox, mode=cfg["mode"], use_skills=(skills_dir khác None), model=model)
        usage = UsageMetadataCallbackHandler()                 # từ langchain_core.callbacks; cộng dồn token của MỌI lần gọi LLM, kể cả subagent
        t0 = thời điểm hiện tại

        THỬ:
            result = agent.invoke(
                {"messages": [{"role": "user", "content": task.instruction}]},
                config = {"callbacks": [usage], "recursion_limit": recursion_limit},
            )
            messages = result["messages"] ; final = nội dung message cuối
        NGOẠI LỆ e:
            record["error"] = "<TênLoại>: <thông báo>" ; messages = [] ; final = ""

        record["seconds"] = thời gian chạy (làm tròn 1 chữ số)
        record["tokens"]  = {"input", "output", "total"} cộng từ usage.usage_metadata.values()
                            (mỗi giá trị có khóa input_tokens, output_tokens, total_tokens)

        calls = mọi tool call trong các AIMessage của messages        # AIMessage.tool_calls là danh sách dict {"name", "args", "id"}
        record["tool_calls"]     = số phần tử của calls
        record["subagent_calls"] = số call có name == "task"
        record["skills_read"]    = số TÊN SKILL KHÁC NHAU trong các call có name == "read_file" và file_path chứa "skills/"
                                (tên = thư mục ngay sau "skills/"; đọc lại cùng một skill chỉ tính một lần)
        record["skills_modified"] = (hash_dir(sandbox/"skills") khác hash_truoc)
        record["final_message"]   = final

        g = grade(task, sandbox / "workspace")                 # chấm trên workspace đã bị tác tử sửa
        record cập nhật: score, passed, total, checks
        ghi out/"trace.md" = render_trace(messages)
    CUỐI CÙNG:
        xóa sandbox

    ghi out/"run.json" = record (JSON, indent=2, ensure_ascii=False)
    TRẢ VỀ record
```

Điểm cần chú ý:

1. **Cô lập.** Tác tử chỉ làm việc trong bản sao ở thư mục tạm. Thư mục `tasks/<id>/workspace` trong kho mã nguồn không bao giờ bị sửa (có test kiểm tra).
2. **Không để lỗi làm dừng chương trình.** Lỗi API, hết giới hạn đệ quy (`recursion_limit`) được ghi vào `error`; tác vụ vẫn được chấm trên trạng thái workspace hiện có.
3. **`recursion_limit`** giới hạn số bước của đồ thị tác tử, là cơ chế chính để chặn một lần chạy tiêu tốn token vô hạn.
4. **Định nghĩa các số đếm.** `tool_calls`, `subagent_calls`, `skills_read` chỉ đếm các lần gọi ở **luồng chính**, vì các message bên trong subagent không nằm trong `result["messages"]`. Số token thì tính đủ nhờ `usage`. Mọi sinh viên dùng cùng định nghĩa này nên số liệu so sánh được.
5. **`skills_modified`** là bằng chứng rằng tác tử đã sửa skill trong lúc chạy. Ở các lần chạy chính thức giá trị phải là `False`.
6. **`skills_sha256` và `timestamp`** cho phép giảng viên kiểm tra rằng lần chạy dùng đúng bộ skill đã đóng băng và diễn ra sau thời điểm đóng băng.
7. **Vết (`trace.md`) chỉ gồm luồng chính.** Việc subagent làm bên trong không hiện ra; chỉ thấy lệnh gọi `task` và báo cáo cuối của subagent.
8. **Khi `agent.invoke` ném lỗi** (ví dụ `GraphRecursionError`), `messages` rỗng nên `trace.md` rỗng và `tool_calls` bằng 0 dù tác tử đã chạy nhiều bước. Đây là hạn chế của cách cài đặt tối thiểu. Mở rộng tùy chọn: dùng `agent.stream(..., stream_mode="values")` và giữ trạng thái cuối cùng nhận được để vẫn có vết khi lỗi.

---

## Bước 2 (CÓ SẴN, chỉ để tham khảo). `main(argv)`

```text
HÀM main(argv):
    parser: --condition (bắt buộc, thuộc CONDITIONS), --tasks (nhiều giá trị, mặc định ["all"]),
            --results (mặc định "results"), --recursion-limit (mặc định 60)
    ids = tất cả id NẾU tasks == ["all"]; id có role "learn"/"eval" NẾU tasks == ["learn"] / ["eval"]; NGƯỢC LẠI chính danh sách
    VỚI MỖI id TRONG ids:
        r = run_task(id, condition, results, recursion_limit=...)
        in một dòng: điều kiện, id, passed/total, token, số tool call, giây, lỗi (nếu có)
```
