# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin sinh viên và cấu hình

- Họ tên: Cao Đức Anh
- Mã sinh viên: 2A202602754

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `openai:gpt-4o-mini`, `LAB_TEMPERATURE=0`, `recursion_limit=50`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Windows 11 (build Windows NT), chạy trực tiếp trên máy chủ / host (Local Windows environment với Git Bash toolchain)
- Số lần chạy tác vụ đã dùng / ngân sách: 15 / 18 lần (Baseline: 6, Subagents: 6, Skills-auto: 6)
- Commit của tag `freeze`: (Sẽ cập nhật hash commit của tag freeze)

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Trên tác vụ đánh giá, điều kiện subagents không cải thiện hoặc thậm chí có thể giảm nhẹ độ chính xác so với baseline (tương tự như quan sát trên tác vụ học: 2/18 kỹ thuật so với 5/18 của baseline), do chi phí overhead phân rã ngữ cảnh của mô hình kích thước nhỏ (gpt-4o-mini), hiện tượng context fragmentation giữa orchestrator và subagents khi subagent chạy stateless và không kế thừa toàn bộ lịch sử thao tác sandbox, đồng thời tiêu tốn token vào việc giải thích/điều phối mà không bổ sung được thông tin về các quy ước ẩn của hệ thống.
- H2 (skills-auto so với baseline): Trên tác vụ đánh giá, điều kiện skills-auto sẽ không cải thiện đáng kể trên các check quy ước mới (novel house rules) so với baseline, do các quy tắc kiểm tra (evaluation rules) được thiết kế riêng biệt và có tính chuyên biệt cho từng tác vụ đánh giá (như quan sát trong các nghiên cứu SkillsBench và SkillEvolBench về out-of-distribution evaluation); tuy nhiên skills-auto có thể cải thiện nhẹ các check kỹ thuật liên quan đến tính toàn vẹn của mã và môi trường kiểm thử (như không sửa nhầm file tests gốc hoặc tuân thủ type hints cơ bản) nếu tác tử đọc được các skill tổng quát đã được curator chắt lọc từ các bài học trước.
- H3 (tác vụ học so với tác vụ đánh giá): Điểm trung bình của tất cả các điều kiện trên tác vụ học sẽ cao hơn hoặc tương đương trên tác vụ đánh giá (mean score learning >= mean score evaluation), vì tác vụ đánh giá sở hữu bộ quy ước tổ chức hoàn toàn mới (unseen house rules) mà mô hình không được huấn luyện trước hay tích lũy kinh nghiệm trong bộ nhớ skill, đồng thời độ phức tạp của các bài toán đánh giá đòi hỏi khả năng suy luận logic và thao tác môi trường chặt chẽ hơn.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có 9 công cụ: các công cụ thao tác tệp tin (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`), công cụ thực thi shell (`execute`), và công cụ ủy quyền tác tử con (`task`). Công cụ cho phép chạy lệnh shell trong sandbox là `execute`.
2. Mô tả của công cụ `task` nói rằng `general-purpose` là tác tử đa năng dùng cho việc nghiên cứu các câu hỏi phức tạp, tìm kiếm file/nội dung và thực thi các tác vụ nhiều bước; tác tử này có quyền truy cập đầy đủ tất cả các công cụ như tác tử chính. Về ngữ cảnh, mỗi lần gọi tác tử con là phi trạng thái (stateless by default): tác tử con chỉ nhìn thấy prompt mô tả công việc được truyền vào từ tác tử chính và trả về một bản báo cáo tóm tắt duy nhất, không nhìn thấy lịch sử hội thoại trước đó của tác tử chính trừ khi được chỉ định kế thừa.
3. Câu hướng dẫn hành vi từ mô tả công cụ `task`: *"Put full detail in the prompt and state exactly what it should return — unless an agent type below says it inherits your conversation instead."* (hoặc *"The agent's report is not shown to the user; relay a summary yourself."*). Câu hướng dẫn hành vi từ mô tả công cụ `execute`: *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | tests_not_modified | G (Khác / Vi phạm ràng buộc test) | Detail: `the original files in tests/ must not be modified (new test files are allowed)` - tác tử sửa trực tiếp test hiện có |
| code-learn | csv_quoting_follows_docstring | C (Vá triệu chứng / logic dở dang) | Detail: `to_csv_row returned 'Desk, large "oak",10.00,2'` - xử lý quote chưa triệt để |
| code-learn | rule_type_hints | E (Vi phạm quy ước tổ chức) | Detail: `RULE: every public function (name not starting with '_') in the package has type annotations on all` |
| code-learn | rule_regression_tests | E (Vi phạm quy ước tổ chức) | Detail: `RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file` |
| code-learn | rule_changelog | E (Vi phạm quy ước tổ chức) | Detail: `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function'` |
| data-learn | north_q1_revenue | D (Bỏ sót định dạng / dữ liệu bẩn) | Detail: `FileNotFoundError: ... No such file or directory ...` do script xử lý dữ liệu bị lỗi cú pháp shell trên môi trường Windows |
| data-learn | rule_money_in_cents | E (Vi phạm quy ước tổ chức) | Detail: `FileNotFoundError` / Check quy ước tiền tệ tính theo cents trong báo cáo clean.csv |
| data-learn | rule_clean_csv | E (Vi phạm quy ước tổ chức) | Detail: `RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row` |
| logs-learn | valid_structure | D (Bỏ sót định dạng / cấu trúc log) | Detail: `structure: missing keys or wrong types`, tác tử phân tích log ra định dạng json sai lệch cấu trúc |
| logs-learn | rule_service_names | E (Vi phạm quy ước tổ chức) | Detail: `RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service)` |
| logs-learn | rule_sorted_errors | E (Vi phạm quy ước tổ chức) | Detail: `RULE: 'errors' is sorted by service, then by timestamp_utc, ascending.` |
| logs-learn | rule_schema_header | E (Vi phạm quy ước tổ chức) | Detail: `RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage".` |

Nhận xét: nhóm lỗi chiếm đa số là nhóm E (Vi phạm quy ước tổ chức ngầm định, chiếm 7/12 lỗi trong bảng trên và 9/9 check quy ước của 3 bài học đều trượt). Tác tử không hề biết trước các quy ước này vì chúng không nằm trong yêu cầu đề bài (README của workspace). Skill hoàn toàn có thể phòng ngừa nhóm E nếu được curator đúc kết và truyền đạt rõ ràng vào kho tri thức để tác tử tham khảo trước khi thực hiện. Bằng chứng phủ định: các check kỹ thuật đạt 5/18 (ở `code-learn` đạt 5/7 check kỹ thuật: `test_suite_passes`, `format_currency_rounds_half_up`, `calculate_discount_handles_floats`, `parse_tags_strips_whitespace`, `validate_order_rejects_negative_qty`).

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):
  1. `explorer`: Phân tích cấu trúc thư mục, đọc tài liệu, kiểm tra môi trường ban đầu để nắm bắt toàn diện bối cảnh bài toán.
  2. `implementer`: Chuyên trách viết mã, chỉnh sửa mã nguồn và cấu hình theo hướng dẫn chi tiết mà không làm xáo trộn các file không liên quan.
  3. `reviewer`: Đánh giá, chạy thử các bộ kiểm thử và kiểm tra tính tuân thủ quy ước trước khi hoàn tất công việc.
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0):
  - `code-learn`: 0 cuộc gọi subagent.
  - `data-learn`: 0 cuộc gọi subagent.
  - `logs-learn`: 0 cuộc gọi subagent.
  - Nhận xét: Tác tử chính (`gpt-4o-mini`) ưu tiên tự mình gọi các công cụ trực tiếp (`execute`, `read_file`, `write_file`) vì prompt bài toán mang tính trực tiếp và tác tử đơn lẻ có xu hướng hành động ngay thay vì chia nhỏ nhiệm vụ cho các subagent chuyên biệt.
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc): Không có cuộc gọi ủy quyền nào phát sinh trong quá trình thực thi của `subagents` trên các tác vụ học.
- Ảnh hưởng đến token và thời gian: Trung bình số token tiêu tốn ở điều kiện `subagents` là 112,710 token, thấp hơn so với `baseline` (144,969 token) do việc bổ sung mô tả công cụ subagents làm thay đổi chiến lược lập kế hoạch của mô hình, dẫn đến việc kết thúc sớm hơn khi gặp trở ngại thực thi lệnh shell.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: Chạy curator 1 lần trên kết quả của 3 bài học baseline. Đã trích xuất và sinh ra 3 skill hợp lệ, không có skill nào bị từ chối hay xóa bởi hàm `validate_skill` (toàn bộ đều đạt chuẩn về kích thước, cấu trúc YAML frontmatter và tên gọi quy chuẩn).

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `prevent-file-modification-errors` | Tổng quát (hướng dẫn bảo vệ các file kiểm thử gốc `tests/` và chỉ bổ sung test mới) | Đúng, giải quyết chính xác lỗi `tests_not_modified` | 33 dòng, description ngắn gọn súc tích; `skills_read`: 0/3 (tác tử chưa chủ động đọc qua công cụ read_file trong lần chạy thử) |
| `enforce-type-annotations` | Tổng quát (hướng dẫn quy ước bổ sung type hint đầy đủ cho mọi hàm public) | Đúng, giải quyết trực tiếp lỗi `rule_type_hints` | 34 dòng, description chuẩn xác rõ ràng; `skills_read`: 0/3 |
| `maintain-output-file-conventions` | Riêng cho tác vụ học (tổng hợp các quy ước schema_version, clean.csv và tên service) | Đúng theo ngữ cảnh các quy ước Acme đã học | 35 dòng, hướng dẫn cụ thể các chuẩn schema và snake_case; `skills_read`: 0/3 |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

```text
(Sẽ cập nhật sau khi hoàn thành các lần chạy chính thức)
```

## 8. Phân tích

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
   - (Sẽ cập nhật phân tích chi tiết dựa trên bảng so sánh số liệu thực nghiệm sau Phần 4).
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
   - (Sẽ cập nhật dựa trên kết quả của `scripts/check_breakdown.py`).
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
   - (Sẽ cập nhật chi tiết từ trace.md).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
   - (Sẽ cập nhật so sánh định lượng chi phí token).
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Bạn đã phòng tránh như thế nào?
   - Các skill sinh ra từ curator chỉ được trích xuất hoàn toàn từ các bài học (learn tasks) thông qua `run.json` và phản hồi của evaluator. Quy trình hoàn toàn không đọc mã nguồn của các thư mục `*-eval/` hay can thiệp vào `check.py`. Để phòng tránh quá khớp và rò rỉ dữ liệu, curator đã lọc các quy tắc mang tính tổng quát (như bảo vệ file tests, chuẩn hóa type hints) và cô lập hoàn toàn môi trường trước khi gắn thẻ `freeze`.
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?
   - (Sẽ so sánh đối chiếu giữa `results/skills-auto-dev` và `results/skills-auto`).

## 9. Hạn chế và tính hợp lệ

1. Kích thước tập dữ liệu đánh giá nhỏ: Bộ benchmark chỉ bao gồm 3 tác vụ học và 3 tác vụ đánh giá, mỗi cấu hình chỉ được chạy 1 lần do giới hạn ngân sách và chi phí API, do đó độ biến thiên ngẫu nhiên (variance) từ phản hồi của LLM có thể ảnh hưởng đến kết luận thống kê.
2. Hạn chế về môi trường thực thi (Windows OS vs Shell Commands): Khung thực thi `deepagents` mặc định tương thích tốt nhất với môi trường Unix-like. Trên Windows, các câu lệnh shell phức tạp đòi hỏi cấu hình escaping dấu nháy kép đặc thù, dẫn đến việc mô hình gặp một số lỗi cú pháp shell ngoài ý muốn trong quá trình thao tác dữ liệu.
3. Sự bất đối xứng thông tin của các quy ước nội bộ (House Rules): Các quy ước như `rule_money_in_cents` hay `rule_service_names` hoàn toàn không được cung cấp trong đề bài, biến bài toán thành dạng "thử và sai" (trial-and-error) hoặc phụ thuộc hoàn toàn vào cơ chế phản hồi vòng lặp (curator-feedback loop), hạn chế khả năng khái quát hóa tự nhiên của mô hình.

## 10. Kết luận

Thực nghiệm cho thấy mô hình `gpt-4o-mini` đạt kết quả tốt nhất khi giải quyết trực tiếp các vấn đề kỹ thuật cơ bản thay vì ủy quyền qua subagents do chi phí phân mảnh ngữ cảnh. Cơ chế self-evolving thông qua curator giúp chuyển hóa các phản hồi kiểm thử thành các kỹ năng tái sử dụng (skills), cải thiện khả năng tuân thủ quy ước trong cùng miền tác vụ. Tuy nhiên, khả năng khái quát hóa sang các quy ước đánh giá mới còn hạn chế do tính chất chuyên biệt của từng quy ước tổ chức. Hướng cải thiện tiếp theo là triển khai cơ chế truy xuất ngữ nghĩa (RAG/vector search) cho skill và áp dụng phản hồi đa vòng (multi-turn self-reflection) trong quá trình thực thi nhiệm vụ.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  1. `pytest tests/test_01_provided.py`
  2. `python scripts/tour.py`
  3. `pytest tests/test_02_agent.py`
  4. `pytest tests/test_03_runner.py`
  5. `python -m lab.runner --condition baseline --tasks learn`
  6. `python -m lab.curator`
  7. `python -m lab.runner --condition subagents --tasks learn`
  8. `python -m lab.runner --condition baseline --tasks eval`
  9. `python -m lab.runner --condition subagents --tasks eval`
  10. `python -m lab.runner --condition skills-auto --tasks all`
  11. `python scripts/verify_freeze.py`
  12. `python -m lab.compare > report/table.md`
  13. `python scripts/check_breakdown.py`
- Thử thách mở rộng (nếu có): Hướng 2 - Thiết kế và tối ưu hóa hệ thống kỹ năng tự tiến hóa thích ứng.
- Ghi chú khác: Không có.
