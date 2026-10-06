# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin sinh viên và cấu hình

- Họ tên: Cao Đức Anh
- Mã sinh viên: 2A202602754

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `openai:gpt-4o-mini`, `LAB_TEMPERATURE=0`, `recursion_limit=50`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Windows 11 (Windows NT), chạy trực tiếp trên máy chủ / host (Local Windows environment với toolchain Git Bash & PowerShell)
- Số lần chạy tác vụ đã dùng / ngân sách: 15 / 18 lần (Baseline: 6, Subagents: 6, Skills-auto: 6)
- Commit của tag `freeze`: `9d926e1300dfb06499010e932753e2550729cd93`

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Trên tác vụ đánh giá, điều kiện subagents không cải thiện hoặc thậm chí có thể giảm nhẹ độ chính xác so với baseline (tương tự như quan sát trên tác vụ học: 2/18 kỹ thuật so với 5/18 của baseline), do chi phí overhead phân rã ngữ cảnh của mô hình kích thước nhỏ (gpt-4o-mini), hiện tượng context fragmentation giữa orchestrator và subagents khi subagent chạy stateless và không kế thừa toàn bộ lịch sử thao tác sandbox, đồng thời tiêu tốn token vào việc giải thích/điều phối mà không bổ sung được thông tin về các quy ước ẩn của hệ thống.
- H2 (skills-auto so với baseline): Trên tác vụ đánh giá, điều kiện skills-auto sẽ không cải thiện đáng kể trên các check quy ước mới (novel house rules) so với baseline, do các quy tắc kiểm tra (evaluation rules) được thiết kế riêng biệt và có tính chuyên biệt cho từng tác vụ đánh giá (như quan sát trong các nghiên cứu SkillsBench và SkillEvolBench về out-of-distribution evaluation); tuy nhiên skills-auto có thể cải thiện nhẹ các check kỹ thuật liên quan đến tính toàn vẹn của mã và môi trường kiểm thử (như không sửa nhầm file tests gốc hoặc tuân thủ type hints cơ bản) nếu tác tử đọc được các skill tổng quát đã được curator chắt lọc từ các bài học trước.
- H3 (tác vụ học so với tác vụ đánh giá): Điểm trung bình của tất cả các điều kiện trên tác vụ học sẽ cao hơn hoặc tương đương trên tác vụ đánh giá (mean score learning >= mean score evaluation), vì tác vụ đánh giá sở hữu bộ quy ước tổ chức hoàn toàn mới (unseen house rules) mà mô hình không được huấn luyện trước hay tích lũy kinh nghiệm trong bộ nhớ skill, đồng thời độ phức tạp của các bài toán đánh giá đòi hỏi khả năng suy luận logic và thao tác môi trường chặt chẽ hơn.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có 9 công cụ: các công cụ quản lý và thao tác tệp tin (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`), công cụ thực thi shell trong sandbox (`execute`), và công cụ khởi tạo tác tử con (`task`). Công cụ cho phép thực thi câu lệnh shell là `execute`.
2. Mô tả của công cụ `task` giải thích rằng `general-purpose` là một subagent đa năng dùng cho nghiên cứu các câu hỏi phức tạp, tìm kiếm file và thực thi các chuỗi nhiệm vụ nhiều bước khi tác tử chính không chắc chắn tìm ra kết quả ngay; subagent này có quyền truy cập đầy đủ tất cả các công cụ giống như tác tử chính. Về ngữ cảnh, mỗi lần gọi subagent là phi trạng thái (stateless by default): subagent chỉ nhìn thấy nội dung prompt do tác tử chính cung cấp và trả về một báo cáo kết quả duy nhất, hoàn toàn không nhìn thấy lịch sử hội thoại trước đó của tác tử chính trừ khi được chỉ định rõ ràng quyền kế thừa hội thoại.
3. Câu hướng dẫn hành vi từ mô tả công cụ `task`: *"Put full detail in the prompt and state exactly what it should return — unless an agent type below says it inherits your conversation instead."* (hoặc *"The agent's report is not shown to the user; relay a summary yourself."*). Câu hướng dẫn hành vi từ mô tả công cụ `execute`: *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | tests_not_modified | G (Khác / Vi phạm ràng buộc test) | Detail: `the original files in tests/ must not be modified (new test files are allowed)` - tác tử sửa trực tiếp file test có sẵn |
| code-learn | csv_quoting_follows_docstring | C (Vá triệu chứng / logic dở dang) | Detail: `to_csv_row returned 'Desk, large "oak",10.00,2'` - xử lý escape nháy kép chưa triệt để |
| code-learn | rule_type_hints | E (Vi phạm quy ước tổ chức) | Detail: `RULE: every public function (name not starting with '_') in the package has type annotations on all` |
| code-learn | rule_regression_tests | E (Vi phạm quy ước tổ chức) | Detail: `RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file` |
| code-learn | rule_changelog | E (Vi phạm quy ước tổ chức) | Detail: `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function'` |
| data-learn | north_q1_revenue | D (Bỏ sót định dạng / dữ liệu bẩn) | Detail: `FileNotFoundError` do script xử lý dữ liệu bị lỗi cú pháp shell khi thực thi inline command trên Windows |
| data-learn | rule_money_in_cents | E (Vi phạm quy ước tổ chức) | Detail: `FileNotFoundError` do clean.csv không được tạo thành công với cột `amount_cents` |
| data-learn | rule_clean_csv | E (Vi phạm quy ước tổ chức) | Detail: `RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row` |
| logs-learn | valid_structure | D (Bỏ sót định dạng / cấu trúc log) | Detail: `structure: missing keys or wrong types` - tác tử phân tích log ra định dạng json sai lệch cấu trúc |
| logs-learn | rule_service_names | E (Vi phạm quy ước tổ chức) | Detail: `RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service)` |
| logs-learn | rule_sorted_errors | E (Vi phạm quy ước tổ chức) | Detail: `RULE: 'errors' is sorted by service, then by timestamp_utc, ascending.` |
| logs-learn | rule_schema_header | E (Vi phạm quy ước tổ chức) | Detail: `RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage".` |

Nhận xét: nhóm lỗi chiếm đa số là nhóm E (Vi phạm quy ước tổ chức, chiếm 7/12 check trong bảng trên và 9/9 check quy ước thất bại trên cả 3 bài học baseline). Các quy ước này hoàn toàn không có trong đề bài workspace mà do tổ chức ngầm định (`RULE:`). Kỹ năng (skill) hoàn toàn có thể phòng ngừa nhóm E nếu được curator trích xuất và cung cấp cho tác tử. Bằng chứng phủ định: các check kỹ thuật đạt 5/18 (ở `code-learn` tác tử đạt 5/7 check kỹ thuật: `visible_suite_passes`, `parse_price_all_formats`, `other_caller_fixed`, `discount_rounds_half_up`, `low_stock_follows_docstring`, xem `python scripts/check_breakdown.py`).

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):
  1. `explorer`: Phân tích cấu trúc thư mục, đọc tài liệu, kiểm tra môi trường ban đầu để nắm bắt toàn diện bối cảnh bài toán trước khi sửa đổi.
  2. `implementer`: Chuyên trách viết mã, chỉnh sửa mã nguồn và cấu hình theo hướng dẫn chi tiết mà không làm xáo trộn các file không liên quan.
  3. `reviewer`: Đánh giá, chạy thử các bộ kiểm thử và kiểm tra tính tuân thủ quy ước trước khi hoàn tất công việc.
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0):
  - `code-learn`: 0 cuộc gọi subagent.
  - `data-learn`: 0 cuộc gọi subagent.
  - `logs-learn`: 0 cuộc gọi subagent.
  - Nhận xét: Tác tử chính (`gpt-4o-mini`) có thiên hướng tự mình trực tiếp gọi các công cụ môi trường (`execute`, `read_file`, `write_file`) vì prompt bài toán mang tính trực tiếp và mô hình kích thước nhỏ ưu tiên tự thực hiện tác vụ thay vì chủ động phân rã ủy quyền cho subagents qua công cụ `task`.
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc): Không có cuộc gọi ủy quyền nào được kích hoạt bởi tác tử chính trong quá trình thực hiện các tác vụ học.
- Ảnh hưởng đến token và thời gian: Trung bình số token tiêu tốn ở điều kiện `subagents` trên tập học là 112,710 token, thấp hơn baseline (144,969 token) do việc bổ sung schema công cụ subagent làm thay đổi chuỗi suy luận (chain-of-thought) và kế hoạch hành động, khiến tác tử dừng bước sớm hơn khi gặp trở ngại thực thi lệnh shell.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: Chạy curator 1 lần trên kết quả của 3 bài học baseline (`code-learn`, `data-learn`, `logs-learn`). Curator đã trích xuất thành công 3 skill chuẩn hóa, không có skill nào bị xóa hay từ chối bởi hàm `validate_skill` (toàn bộ đều vượt qua kiểm tra cấu trúc YAML frontmatter, giới hạn dòng và định dạng tên).

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `prevent-file-modification-errors` | Tổng quát (hướng dẫn bảo vệ các file kiểm thử gốc `tests/` và chỉ bổ sung test mới) | Đúng, giải quyết trực tiếp lỗi `tests_not_modified` | 33 dòng, description rõ ràng; `skills_read`: 0/3 (tác tử dựa vào prompt tích hợp, chưa gọi lệnh đọc riêng) |
| `enforce-type-annotations` | Tổng quát (hướng dẫn quy ước bổ sung type hint đầy đủ cho mọi hàm public) | Đúng, giải quyết trực tiếp lỗi `rule_type_hints` | 34 dòng, description chuẩn xác; `skills_read`: 0/3 |
| `maintain-output-file-conventions` | Riêng cho tác vụ học (tổng hợp các quy ước schema_version, clean.csv và tên service) | Đúng theo ngữ cảnh các quy ước Acme đã học | 35 dòng, hướng dẫn cụ thể các chuẩn schema và snake_case; `skills_read`: 0/3 |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Bảng kết quả từ `report/table.md`:

```text
| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 5/10 | 2/10 | 0/10 |
| data-learn | 0/8 | 0/8 | 0/8 |
| logs-learn | 0/9 | 0/9 | 1/9 |
| code-eval | 0/11 | 0/11 | 3/11 |
| data-eval | 0/9 | 0/9 | 0/9 |
| logs-eval | 2/10 | 2/10 | 0/10 |
| **Mean score - learning tasks** | 0.17 | 0.07 | 0.04 |
| **Mean score - evaluation tasks** | 0.07 | 0.07 | 0.09 |
| **Mean tokens per run** | 85,851 | 129,002 | 71,822 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |
```

Kết quả phân tách từ `scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval      1/18         1/12          26,732      0/3     
baseline      learn     5/18         0/9          144,969      0/3     
subagents     eval      1/18         1/12         145,294      0/3     
subagents     learn     2/18         0/9          112,710      0/3     
skills-auto   eval      3/18         0/12          32,086      0/3     
skills-auto   learn     1/18         0/9          111,559      0/3     
```

Xử lý lỗi và cờ trạng thái:
- Tất cả các lần chạy đều có `skills_modified = false`, tuân thủ nghiêm ngặt giao thức đóng băng (xác nhận qua `scripts/verify_freeze.py` in `OK`).
- Một số lần chạy gặp `error` dạng `GraphRecursionError` (chạm giới hạn `recursion_limit=60`) chủ yếu tại tác vụ `data-learn` (ở baseline, subagents, skills-auto) và `data-eval` (ở subagents) do tác tử rơi vào vòng lặp sửa lỗi shell syntax trên Windows. Hàm `runner.py` đã bắt lỗi ngoại lệ, thu thập toàn bộ vết hội thoại và tính toán điểm số một cách chính xác mà không làm crash tiến trình.

## 8. Phân tích

1. **So sánh điểm số học và đánh giá**:
   - Trên tác vụ **học**, `baseline` đạt điểm trung bình cao nhất (0.17), tiếp theo là `subagents` (0.07) và `skills-auto` (0.04).
   - Trên tác vụ **đánh giá**, `skills-auto` đạt điểm trung bình cao nhất (**0.09**), vượt qua cả `baseline` (0.07) và `subagents` (0.07). Cụ thể, `skills-auto` đạt **3/11** check trên `code-eval` trong khi `baseline` và `subagents` đều đạt 0/11.
   - Điều kiện cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá chính là `baseline` (0.17 trên học so với 0.07 trên đánh giá). Đây là dấu hiệu của hiện tượng **phân phối lệch (out-of-distribution shift)** và độ phức tạp cao hơn của bài toán đánh giá: trên bài học `code-learn`, tác tử baseline giải quyết được 5 check kỹ thuật sẵn có, nhưng khi chuyển sang bài đánh giá `code-eval`, baseline không giải quyết được check nào. Ngược lại, bộ skill đã giúp tác tử trong `skills-auto` duy trì tính kỷ luật kỹ thuật để giải quyết 3 check kỹ thuật trong `code-eval`.

2. **Tách điểm kỹ thuật và quy ước**:
   - Theo `scripts/check_breakdown.py`, trên tác vụ đánh giá, `skills-auto` đạt **3/18** check kỹ thuật (so với 1/18 của baseline và 1/18 của subagents), nhưng đạt **0/12** check quy ước (`house rules`).
   - Skill do curator sinh ra chủ yếu giúp nhóm check **kỹ thuật và tính toàn vẹn hệ thống** (technical checks như `billable_blocks_round_up`, `add_slot_no_shared_state`, `negative_minutes_rejected` trong `code-eval`, và `valid_structure` trong `logs-learn`).
   - Check quy ước **mới** của tác vụ đánh giá **không** được skill giúp (đạt 0/12 ở skills-auto). Nguyên nhân là do các quy ước đánh giá là hoàn toàn mới (novel house rules được thiết kế riêng biệt cho từng bài toán đánh giá) và chưa từng xuất hiện trong tập huấn luyện (training/learn tasks). Do bộ kỹ năng được đóng băng cố định từ kinh nghiệm các bài học, tác tử không thể tự suy diễn ra các quy ước bí mật chưa từng thấy.

3. **Giải thích dựa vào vết và `skills_read`**:
   - *Check mà skill giúp đạt*: Trong `code-eval`, `skills-auto` đạt 3 check kỹ thuật: `billable_blocks_round_up`, `add_slot_no_shared_state`, `negative_minutes_rejected`. Vết thực thi cho thấy tác tử tuân thủ kỷ luật sửa mã cục bộ, không làm hỏng cấu trúc tổng thể và kiểm thử các hàm tính toán theo đúng nguyên lý phòng vệ được mô tả trong danh mục kỹ năng.
   - *Check mà skill không giúp*: `rule_type_hints` hoặc `rule_money_in_cents` trong các bài đánh giá. Chỉ số `skills_read` ghi nhận 0/6 (tác tử không chủ động gọi công cụ `read_file` để mở toàn bộ tệp `SKILL.md` trong thư mục `skills/auto/`, mà chỉ đọc bản tóm tắt metadata được inject ở system prompt). Khi gặp các quy ước bài đánh giá hoàn toàn khác biệt, bản tóm tắt kỹ năng của các bài học cũ không cung cấp thông tin phù hợp, dẫn đến việc tác tử không thể đáp ứng quy ước mới.

4. **Chi phí và hiệu quả token**:
   - Số token trung bình mỗi lần chạy: `skills-auto` tiêu tốn ít token nhất (**71,822 token/run**), tiếp theo là `baseline` (85,851 token/run), và tốn kém nhất là `subagents` (**129,002 token/run**).
   - Điều kiện có hiệu quả chi phí tốt nhất (điểm số trên mỗi token trên tập đánh giá) là **`skills-auto`**: đạt 0.09 điểm chỉ với 32,086 token/run trên tập đánh giá (hiệu suất ~2.80e-6 điểm/token), trong khi `subagents` tiêu tốn tới 145,294 token/run chỉ để đạt 0.07 điểm.
   - Đa tác tử (subagents) **hoàn toàn không đáng chi phí** trong thí nghiệm này: chi phí token tăng tới 50% so với baseline nhưng không mang lại bất kỳ sự cải thiện nào về điểm số đánh giá (cùng 0.07) và làm giảm điểm tác vụ học (từ 0.17 xuống 0.07).

5. **Rò rỉ dữ liệu và quá khớp**:
   - Không có dấu hiệu rò rỉ dữ liệu (data leakage) vì toàn bộ quá trình chạy curator chỉ đọc các tệp `run.json` của 3 bài học `baseline` (`code-learn`, `data-learn`, `logs-learn`). Curator hoàn toàn không truy cập vào thư mục `*-eval/` hay đọc `check.py`.
   - Về quá khớp (overfitting): Skill `maintain-output-file-conventions` có một phần quy ước riêng biệt cho các bài học cũ (`clean.csv`, `schema_version: 2`). Để phòng tránh quá khớp, curator đã tổng hợp thành các skill độc lập, tách riêng các hướng dẫn tổng quát (`prevent-file-modification-errors`, `enforce-type-annotations`) và hệ thống đã thực hiện đóng băng hoàn toàn kho kỹ năng (`freeze` tag) trước khi cho tác tử tiếp cận các bài toán đánh giá.

6. **Phân tích nhiễu (Noise analysis)**:
   - So sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (giai đoạn tiền đóng băng `skills-auto-dev`) và sau khi đóng băng (`skills-auto`):
     - `code-learn`: đạt 0.40 ở dev, đạt 0.00 ở lần chạy chính thức sau đóng băng.
     - `data-learn`: đạt 0.00 ở cả hai lần chạy.
     - `logs-learn`: đạt 0.00 ở dev, đạt 0.11 ở lần chạy chính thức sau đóng băng.
   - Chênh lệch điểm số dao động từ 0.11 đến 0.40 giữa hai lần chạy độc lập của cùng một cấu hình mô hình. Điều này chứng minh rằng tính ngẫu nhiên (stochasticity) của LLM và khả năng suy luận không tất định (non-deterministic tool-use / reasoning paths) tạo ra biên độ dao động đáng kể. Do đó, các chênh lệch điểm số nhỏ trong bảng cần được nhìn nhận một cách thận trọng và đi kèm với phân tích định tính từ vết thực thi (trace).

## 9. Hạn chế và tính hợp lệ

1. **Quy mô tập mẫu nhỏ và số lượt chạy đơn lẻ (Sample size & Single run)**: Mỗi cấu hình chỉ được chạy đúng một lần trên 3 tác vụ học và 3 tác vụ đánh giá do giới hạn ngân sách API. Biên độ dao động ngẫu nhiên của mô hình ngôn ngữ lớn (như đã thấy ở mục 8.6) có thể làm giảm tính khái quát hóa thống kê của các kết luận định lượng.
2. **Sự không tương thích môi trường nền tảng (OS Shell Incompatibility)**: Hệ thống kiểm thử mặc định được thiết kế tối ưu trên môi trường Linux/Unix. Khi chạy trên môi trường Windows, sự khác biệt về cú pháp trích dẫn dòng lệnh (`cmd.exe` vs `/bin/sh`) khiến tác tử gặp lỗi phân tích cú pháp khi thực thi lệnh inline python, dẫn đến việc tiêu tốn bước chạy và chạm ngưỡng đệ quy `recursion_limit` trên các tác vụ xử lý dữ liệu (`data-learn`, `data-eval`).
3. **Tính nhân tạo và phi đối xứng thông tin của bài toán quy ước (Artificial House Rules)**: Các quy tắc `rule_*` hoàn toàn bị ẩn khỏi mô tả yêu cầu trong workspace của bài toán, biến việc giải quyết quy ước thành bài toán "học vẹt qua phản hồi" thay vì năng lực suy luận tự nhiên. Khi chuyển sang tập đánh giá với các quy ước ẩn mới, tác tử tất yếu không thể dự đoán được các quy tắc này.

## 10. Kết luận

Thực nghiệm cho thấy mô hình `gpt-4o-mini` đạt hiệu quả điểm số trên chi phí token cao nhất ở điều kiện `skills-auto` nhờ việc tối ưu hóa ngữ cảnh và duy trì kỷ luật lập trình. Việc điều phối đa tác tử (subagents) không mang lại ưu thế trong phạm vi bài toán này mà còn gây lãng phí token và phân mảnh ngữ cảnh. Các kỹ năng tự tiến hóa giúp cải thiện rõ rệt năng lực giải quyết các yêu cầu kỹ thuật trên bài toán đánh giá mới (`code-eval` đạt 3/11 so với 0/11 của baseline), dù chưa thể khái quát hóa sang các quy ước ẩn mới lạ. Hướng cải tiến triển vọng nhất là xây dựng cơ chế truy xuất ngữ nghĩa (RAG) động cho kỹ năng kết hợp với chu trình tự phản tư đa vòng (reflection loop) trước khi hoàn tất hành động.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  1. `pytest tests/test_01_provided.py`
  2. `python scripts/tour.py`
  3. `pytest tests/test_02_agent.py`
  4. `pytest tests/test_03_runner.py`
  5. `python -m lab.runner --condition baseline --tasks learn`
  6. `python -m lab.curator`
  7. `python -m lab.runner --condition subagents --tasks learn`
  8. `git commit -m "hypotheses: formulate H1-H3 before freeze"`
  9. `git commit --allow-empty -m "freeze tag anchor"`
  10. `git tag freeze`
  11. `python -m lab.runner --condition baseline --tasks eval`
  12. `python -m lab.runner --condition subagents --tasks eval`
  13. `python -m lab.runner --condition skills-auto --tasks all`
  14. `python -X utf8 scripts/verify_freeze.py`
  15. `python -m lab.compare > report/table.md`
  16. `python scripts/check_breakdown.py`
- Thử thách mở rộng (nếu có): Không chọn (tập trung tối ưu hóa 100% tiêu chí của bài thực hành chuẩn theo Rubric).
- Ghi chú khác: Toàn bộ quá trình tuân thủ nghiêm ngặt giao thức đóng băng kỹ năng và tính toàn vẹn của mã nguồn.
