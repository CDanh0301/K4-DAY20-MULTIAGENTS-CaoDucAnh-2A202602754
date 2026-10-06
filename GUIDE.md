# Hướng dẫn thực hiện (GUIDE)

Tài liệu này mô tả từng bước của lab theo thứ tự thời gian. Đọc `README.md` trước (đặc biệt mục 2 về thiết kế thí nghiệm). Mỗi phần có **đầu ra** (checkpoint) để tự kiểm tra trước khi sang phần tiếp theo.

Đây là **bài cá nhân**: bạn tự làm toàn bộ các phần, tự chạy thí nghiệm bằng khóa API của mình và nộp báo cáo riêng.

Quy ước: lệnh chạy trong thư mục gốc của kho (cùng cấp với `README.md`) với môi trường ảo đã kích hoạt. Số "Phần" dưới đây là số dùng thống nhất trong mã nguồn, test, thang điểm và báo cáo.

---

## Quy tắc làm bài

**Phản hồi (feedback) và `detail`.** Mỗi tác vụ ngoài các check kỹ thuật còn có các check **quy ước tổ chức** (tên bắt đầu bằng `rule_`) mà đề bài không nêu. Ở **tác vụ học**, check thất bại có trường `detail` trong `run.json` phát biểu quy tắc bị vi phạm (không chứa đáp án); curator dùng phản hồi này để viết skill. Ở **tác vụ đánh giá**, `detail` luôn rỗng, và có thêm một quy ước mới không học được từ tác vụ học.

**Quy tắc xem dữ liệu (liêm chính học thuật).**

1. Chỉ được mở `run.json` và `trace.md` của **tác vụ học** để rút kinh nghiệm. Không mở `run.json`, `trace.md` của tác vụ đánh giá và thư mục `tasks/*-eval/`.
2. Không mở tệp `check.py` của bất kỳ tác vụ nào (chứa đáp án kỳ vọng).
3. Không chép đáp án vào skill và không sửa tay nội dung `skills/auto/`. Tên do **quy ước của Acme** yêu cầu (tệp đầu ra như `clean.csv`, `tests/test_regressions.py`, khóa JSON như `meta`) được phép xuất hiện trong skill vì chúng chính là quy tắc; tên có sẵn trong workspace của tác vụ và mọi định danh của tác vụ đánh giá thì không (curator từ chối).
4. Chỉ chạy `baseline` và `subagents` trên tác vụ học trước khi viết giả thuyết (Phần 4.0), để giả thuyết không biết trước điểm của tác vụ đánh giá.
5. Sau khi chốt skill, tạo tag `freeze` và không sửa `skills/auto/` nữa (Phần 4.1).

**An toàn.** Tác tử chạy lệnh shell thật trên máy bạn. Môi trường cách ly (sandbox) trong lab là thư mục tạm, chưa phải cách ly ở mức hệ điều hành; nên chạy trong Docker (`Dockerfile`). Không đưa khóa API vào mã nguồn, `trace.md` hay báo cáo; không commit `.env`. `trace.md` đã thay đường dẫn thư mục người dùng bằng `~`, vẫn nên đọc lại trước khi nộp.

**Ngân sách token.** Chi phí do bạn tự chịu theo gói API của mình. Gợi ý tối đa 30 lần chạy tác vụ: `baseline` 6, `subagents` 6, kiểm tra skill trên tác vụ học 3 đến 6, chạy cuối `skills-auto` sau đóng băng 6, còn lại để chạy lại khi lỗi. Mỗi lần chạy thường dùng khoảng 15 nghìn đến 150 nghìn token. Dùng `pytest` và mô hình giả để kiểm tra mã trước khi chạy mô hình thật.

**Sao lưu kết quả.** Chạy lại cùng một điều kiện ghi đè `results/<điều kiện>/`. Nếu cần giữ bằng chứng cũ, đổi tên thư mục trước khi chạy lại (ví dụ `mv results/skills-auto results/skills-auto-dev`). `lab.compare` chỉ đọc ba thư mục điều kiện đúng tên (`baseline`, `subagents`, `skills-auto`) nên thư mục có hậu tố không lẫn vào bảng.

---

## Phần 0. Cài đặt và làm quen

### 0.1. Cài đặt

Làm theo `README.md` mục 4 (tạo môi trường ảo, `pip install -e .`, tạo `.env`, tạo `report/REPORT.md` từ mẫu).

### 0.2. Kiểm tra môi trường

```bash
pytest tests/test_01_provided.py
```

Đầu ra: `15 passed`. Bộ test này xác nhận 6 tác vụ tồn tại, tác vụ chưa sửa không đạt điểm tối đa, và các mô-đun có sẵn (gồm `validate_skill`, `parse_skill_blocks`, `compare`, `make_model`) hoạt động.

Kiểm tra cấu hình mô hình bằng khóa của bạn (tốn một lượng token rất nhỏ). Nếu chưa đặt `LAB_MODEL`, chương trình báo cần đặt biến nào:

```bash
python -c "from lab.model import make_model; print(make_model().invoke('Reply with OK').content)"
```

### 0.3. Xem tác tử Deep Agents mặc định

```bash
python scripts/tour.py
```

Lệnh này dùng mô hình giả nên **không tốn token**. Nó in danh sách công cụ (tool) mà mô hình nhìn thấy (công cụ tệp: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`; shell: `execute`; subagent: `task`), mô tả đầy đủ của công cụ `task` và `execute`.

Trả lời ngắn các câu hỏi sau vào mục 3 của `report/REPORT.md`:

1. Tác tử mặc định có những công cụ nào? Công cụ nào cho phép chạy lệnh?
2. Mô tả của công cụ `task` nói gì về subagent `general-purpose`? Subagent đó nhìn thấy ngữ cảnh nào của tác tử chính?
3. System prompt mặc định của Deep Agents rỗng. Trích một câu hướng dẫn hành vi từ mô tả của công cụ `task` và một câu từ mô tả của công cụ `execute`.

---

## Phần 1. Hoàn thiện harness với Deep Agents

Cài đặt theo thứ tự dưới đây. Mỗi tệp có pseudo-code trong `guides/pseudocode/`. Chạy test sau mỗi tệp. Test chạy ngoại tuyến, không tốn token.

| Bước | Tệp cần cài đặt | Pseudo-code | Lệnh kiểm tra |
|---|---|---|---|
| 1.1 | `src/lab/subagents.py` | `02_subagents.md` | `pytest tests/test_02_agent.py -k subagents` |
| 1.2 | `src/lab/agent.py` (`make_backend`, `build_agent`) | `01_agent.md` | `pytest tests/test_02_agent.py` |
| 1.3 | `src/lab/runner.py` (`run_task`) | `03_runner.md` | `pytest tests/test_03_runner.py` |

Thứ tự 1.1 trước 1.2 vì `build_agent` gọi `get_subagents`.

Các hằng số `PATHS_NOTE`, `BASE_PROMPT`, `SKILLS_NOTE`, `SUBAGENTS_NOTE` trong `agent.py` đã có sẵn và không sửa; `render_trace` và `main` trong `runner.py` cũng có sẵn. Mỗi tệp chỉ còn các hàm đánh dấu TODO.

Đầu ra: `test_02` và `test_03` đạt toàn bộ.

Chạy thử một tác vụ thật để xác nhận toàn bộ chuỗi hoạt động. Lần chạy này chính là lần chạy `baseline` của `data-learn`, tính vào ngân sách và không cần chạy lại ở Phần 2:

```bash
python -m lab.runner --condition baseline --tasks data-learn
```

Dòng kết quả có dạng (giá trị cụ thể sẽ khác):

```text
baseline      data-learn  score=5/8 tokens=45114 calls=7 12.2s
```

Kiểm tra: `results/baseline/data-learn/run.json` và `trace.md` tồn tại; `tokens.total` lớn hơn 0; trường `checks` liệt kê các check, và check thất bại có `detail`.

Nếu gặp lỗi, xem mục "Xử lý sự cố" ở cuối tài liệu.

---

## Phần 2. Cho tác tử chạy tác vụ học, đo đạc và phân tích lỗi

### 2.1. Chạy đường cơ sở và điều kiện subagents trên tác vụ học

```bash
python -m lab.runner --condition baseline --tasks code-learn logs-learn   # data-learn đã chạy ở Phần 1
python -m lab.runner --condition subagents --tasks learn
```

Chỉ chạy tác vụ học ở giai đoạn này. Tác vụ đánh giá được chạy ở Phần 4, sau khi bạn đã viết giả thuyết.

### 2.2. Phân loại lỗi (error taxonomy)

Mở `run.json` (khóa `checks`, mỗi check có `name`, `passed`, `detail`) và `trace.md` của ba tác vụ học (`code-learn`, `data-learn`, `logs-learn`). Với mỗi check thất bại, xác định nhóm lỗi:

| Nhóm | Dấu hiệu |
|---|---|
| A. Bỏ qua đặc tả | Tác tử không đọc README, docstring hoặc phần định dạng trong đề trước khi làm. |
| B. Không kiểm chứng | Tác tử kết thúc mà không chạy lại test hoặc không đối chiếu kết quả với yêu cầu. |
| C. Vá triệu chứng | Sửa nơi báo lỗi thay vì nguyên nhân gốc. |
| D. Bỏ sót dữ liệu bẩn hoặc định dạng | Không kiểm tra giá trị đặc biệt, trùng lặp, định dạng không đồng nhất, múi giờ trước khi tính. |
| E. Vi phạm quy ước tổ chức | Check có tên bắt đầu bằng `rule_`; `detail` bắt đầu bằng `RULE:`. Quy ước này không có trong đề. |
| F. Báo cáo hoàn thành sai sự thật | Câu trả lời cuối nói đã tạo hoặc sửa một tệp mà thực tế không có. |
| G. Khác | Mô tả ngắn. |

Ghi kết quả vào mục 4 của báo cáo. Mỗi nhóm lỗi nêu **bằng chứng**: tên tác vụ, tên check, trích ngắn từ `detail` hoặc vết. Nhận xét: nhóm lỗi nào chiếm đa số, và một skill có thể phòng ngừa nhóm đó không?

Kỳ vọng: với mô hình mạnh, phần lớn lỗi thuộc nhóm E, còn các check kỹ thuật (nhóm A đến D) thường đạt. Đó cũng là một phát hiện: ghi số check kỹ thuật đạt/tổng làm **bằng chứng phủ định** cho các nhóm A đến D (xem `python scripts/check_breakdown.py`).

### 2.3. Quan sát điều kiện `subagents`

Đọc `trace.md` và `run.json` của điều kiện `subagents` (mục 5 của báo cáo):

1. Trường `subagent_calls`: tác tử chính có giao việc cho subagent không? Subagent nào được gọi, bao nhiêu lần?
2. Nếu có giao việc: lời giao việc có đủ quy tắc của đề không? Báo cáo của subagent có được kiểm tra trước khi dùng không?
3. Nếu `subagent_calls` bằng 0: đây là kết quả hợp lệ. Ghi lại và giải thích vì sao tác tử chính chọn không giao việc.
4. So sánh `tokens.total` với `baseline`.

Lưu ý: `trace.md` chỉ chứa luồng chính; việc subagent làm bên trong không hiện ra.

Đầu ra: `results/baseline/` và `results/subagents/` có đủ 3 tác vụ học; bảng phân loại lỗi.

---

## Phần 3. Self-evolving: curator tự viết skill

Đọc `guides/pseudocode/04_curator.md` và `guides/pseudocode/05_skill_quality.md`.

### 3.1. Cài đặt

Cài đặt hàm `curate_skills` trong `src/lab/curator.py` (`validate_skill` và `parse_skill_blocks` đã có sẵn) và kiểm tra:

```bash
pytest tests/test_04_curator.py
```

### 3.2. Chạy curator

```bash
python -m lab.curator
```

Lệnh này đọc các lần chạy `baseline` của tác vụ học (phản hồi `detail` và vết), gọi mô hình một lần và ghi skill hợp lệ vào `skills/auto/`. Nếu in cảnh báo "không có check thất bại", kiểm tra lại kết quả `baseline`.

### 3.3. Đánh giá skill sinh ra

Với mỗi skill trong `skills/auto/`, trả lời vào mục 6 của báo cáo (dùng các tiêu chí ở `05_skill_quality.md`):

1. Skill có tổng quát hay chỉ lặp lại chi tiết của tác vụ học?
2. Skill có đúng không? Có hướng dẫn nào sai hoặc gây hại không? (Curator có tính ngẫu nhiên; một skill hợp lệ về định dạng vẫn có thể sai.)
3. Skill dài bao nhiêu dòng? Có thừa không? `description` có nêu đúng tình huống kích hoạt không?

Bạn được phép xóa skill kém chất lượng hoặc có hại, và chạy lại curator tối đa 2 lần. Ghi lý do mỗi lần xóa hoặc chạy lại. Không được sửa tay nội dung skill trong `skills/auto/`: đây là thí nghiệm về tác tử tự tiến hóa, nên giữ nguyên đầu ra của curator.

### 3.4. Kiểm tra skill có được dùng không (chỉ trên tác vụ học)

```bash
python -m lab.runner --condition skills-auto --tasks learn
```

Đọc `run.json`: `skills_read` là số skill khác nhau mà tác tử đã đọc; bằng 0 nghĩa là chưa dùng skill nào. Đọc skill chưa đủ: đối chiếu `trace.md` xem tác tử có làm theo từng quy tắc không, và so với `baseline` của cùng tác vụ.

Đầu ra: `skills/auto/` có ít nhất một skill hợp lệ; `test_04` đạt; có kết quả `skills-auto` trên tác vụ học.

---

## Phần 4. Giả thuyết, đóng băng và đo lại trên tác vụ đánh giá

### 4.0. Viết giả thuyết (trước khi thấy bất kỳ điểm nào của tác vụ đánh giá)

Điền mục 2 của `report/REPORT.md` (H1 đến H3): dự đoán điều kiện nào đạt điểm cao nhất trên tác vụ đánh giá và vì sao, kèm căn cứ. Commit ngay:

```bash
git add -A && git commit -m "hypotheses"
```

### 4.1. Đóng băng

Chốt skill. Từ đây không được sửa `skills/auto/`.

```bash
git add -A && git commit --allow-empty -m "freeze skills" && git tag freeze
```

`--allow-empty` để lệnh không thất bại khi không còn thay đổi chưa commit.

### 4.2. Chạy chính thức

Chạy các tác vụ đánh giá cho hai điều kiện chưa có dữ liệu, rồi chạy lại **cả tác vụ học và tác vụ đánh giá** với skill đã đóng băng:

```bash
python -m lab.runner --condition baseline --tasks eval
python -m lab.runner --condition subagents --tasks eval
python -m lab.runner --condition skills-auto --tasks all
```

Kiểm tra bằng công cụ có sẵn:

```bash
python scripts/verify_freeze.py
```

Kết quả phải là `OK`: có commit `hypotheses` (đã điền H1 đến H3) trước tag, skill không đổi từ lúc `freeze`, mọi lần chạy `skills-auto` dùng đúng skill đã đóng băng và `skills_modified` là `false`. Nếu một lần chạy bị báo lỗi, chạy lại lần đó và ghi chú trong báo cáo.

Lưu ý khi đọc kết quả: lần chạy `skills-auto --tasks all` ghi đè kết quả kiểm tra ở Phần 3.4 của tác vụ học (cùng thư mục). Điểm tác vụ học sau đóng băng và điểm ở Phần 3.4 của **cùng bộ skill** có thể khác nhau chỉ do nhiễu; đừng đọc mọi chênh lệch ở cột tác vụ học như là "hiệu quả học". Hãy sao lưu kết quả Phần 3.4 trước khi chạy lại (`mv results/skills-auto results/skills-auto-dev`) để báo cáo cả hai con số.

### 4.3. Tạo bảng so sánh

```bash
python -m lab.compare > report/table.md
```

Đầu ra: `report/table.md` có đủ 3 cột điều kiện, 6 hàng tác vụ và các hàng tổng hợp (điểm trung bình, token trung bình, số lần chạy có đọc skill).

### 4.4. Thống kê hỗ trợ báo cáo

```bash
python scripts/check_breakdown.py
```

In, cho từng điều kiện và vai trò, số check kỹ thuật và số check quy ước đạt, token trung bình và số lần chạy có đọc skill. Dùng số liệu này cho mục 4, 7 và 8 của báo cáo.

---

## Phần 5. Báo cáo

Hoàn thiện `report/REPORT.md` (đã sao chép từ mẫu ở Phần 0). Trong buổi học, viết bản nháp các mục 1 đến 7. Sau buổi học, hoàn thiện mục 8 đến 10. Các yêu cầu bắt buộc:

1. **Giả thuyết đã commit trước tag `freeze`** (mục 2, Phần 4.0).
2. Bảng so sánh dán từ `report/table.md` (mục 7).
3. Phân tích có số liệu, trả lời các câu hỏi trong mục 8 của mẫu. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.
4. Hạn chế của thí nghiệm (số tác vụ nhỏ, một lần chạy, nhiễu) ở mục 9.

---

## Phần 6. Thử thách mở rộng (tùy chọn, tối đa +5 điểm)

Chọn **một** hướng, thực hiện và ghi kết quả vào phụ lục báo cáo:

| Hướng | Mô tả |
|---|---|
| 6a. Tiến hóa tại thời điểm chạy (hot-path) | Cho phép tác tử ghi skill vào `skills/` trong lúc làm tác vụ (ý tưởng của Live-SWE-agent). So sánh với skill đóng băng; theo dõi `skills_modified`. |
| 6b. Vòng tiến hóa thứ hai | Chạy curator lần 2 trên vết của `skills-auto`, hợp nhất skill, đo lại. Quan sát skill phình to (skill bloat) hoặc suy giảm. |
| 6c. Tấn công curator (red team) | Tìm cách khiến curator hoặc tác tử "gian lận" (ví dụ nhắc tên tác vụ đánh giá bằng cách viết lại). Đề xuất biện pháp chặn. |
| 6d. Subagent có skill | Thêm khóa `"skills": ["/skills/"]` cho subagent và so sánh với `subagents` thường. |
| 6e. Lặp để đo nhiễu | Chạy lại mỗi điều kiện trên tác vụ đánh giá ít nhất 2 lần nữa (kết quả ghi vào thư mục `--results` khác), báo cáo trung bình và khoảng dao động. |

---

## Xử lý sự cố

| Triệu chứng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Vết cho thấy `python: command not found` trong lệnh của tác tử | `make_backend` không đặt `PATH` | Xem `01_agent.md`, bước 1. |
| Vết cho thấy `No such file or directory: '/workspace/...'` | Tác tử dùng đường dẫn tuyệt đối `/workspace` trong shell; chỉ dạng tương đối `workspace/...` dùng được ở shell | Dùng nguyên `BASE_PROMPT` có sẵn, không sửa; xem `01_agent.md`, mục "Quy ước đường dẫn". |
| `NotImplementedError: FilesystemMiddleware does not yet support permissions ...` | Dùng tham số `permissions=` cùng backend có shell | Bỏ `permissions`; phát hiện sửa skill bằng băm thư mục. |
| `RuntimeError: No model configured` | Chưa đặt `LAB_MODEL` trong `.env` | Làm theo `README.md` mục 4 (Cấu hình mô hình). |
| `AuthenticationError` hoặc 401 | Khóa API sai, sai biến khóa của nhà cung cấp, hoặc chưa nạp `.env` | Kiểm tra `.env` (đúng tên biến khóa của nhà cung cấp), chạy lại lệnh kiểm tra ở mục 0.2. |
| 404 hoặc "model not found" | Sai `LAB_MODEL` hoặc `LAB_BASE_URL` | Đối chiếu tên model và URL với tài liệu của nhà cung cấp. |
| 429 (vượt giới hạn tốc độ) | Vượt giới hạn của gói API | Chạy tuần tự, chờ và chạy lại; không chạy song song. |
| Một lần chạy kéo dài hoặc tốn nhiều token | Tác tử lặp vô hạn | Giảm `--recursion-limit` (ví dụ 40). Ghi vào `error` của `run.json` và giải thích trong báo cáo. |
| Tác tử không gọi công cụ, chỉ trả lời văn bản | Mô hình không hỗ trợ gọi công cụ ổn định | Đổi sang mô hình hỗ trợ tool calling (xem `README.md` mục 4). |
| `skills_read` bằng 0 dù có skill | `description` của skill quá hẹp hoặc không nêu tình huống kích hoạt | Chạy lại curator (tối đa 2 lần) và đánh giá `description` theo `05_skill_quality.md`. |
| Curator không ghi skill nào | Không có check thất bại ở tác vụ học, hoặc mọi skill bị `validate_skill` từ chối | Đọc thông báo in ra; kiểm tra kết quả `baseline`; xem `validate_skill` báo vấn đề gì. |
| `git commit` báo "nothing to commit" rồi không tạo tag | Dùng `&&` mà không có thay đổi | Dùng `git commit --allow-empty` như ở Phần 4.1. |
| `test_01` báo tác vụ đạt điểm tối đa | Đã vô tình sửa `tasks/*/workspace` | `git checkout -- tasks/`. |
| Thư mục `results/` có kết quả cũ | Chạy lại cùng điều kiện ghi đè kết quả cũ | Đổi tên thư mục cũ trước khi chạy lại (xem mục "Quy tắc làm bài" ở đầu tài liệu). |
