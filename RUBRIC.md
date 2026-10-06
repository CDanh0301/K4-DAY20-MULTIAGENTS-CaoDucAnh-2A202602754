# Thang điểm (RUBRIC) - 100 điểm

Điểm tối đa 100, cộng thêm tối đa 5 điểm thưởng (tổng không vượt quá 100). Điểm được tính theo từng hạng mục. Đây là bài cá nhân, chấm cho từng sinh viên. Số "Phần" khớp với `GUIDE.md`.

## Tổng quan

| # | Hạng mục | Điểm | Cách chấm |
|---|---|---|---|
| 1 | Cài đặt harness (mã nguồn) | 30 | Tự động (`pytest`) |
| 2 | Chạy tác vụ học, đường cơ sở và phân loại lỗi (Phần 2) | 14 | Kiểm tra kết quả + đọc báo cáo |
| 3 | Đa tác tử - subagent (Phần 1, 2) | 10 | Kiểm tra kết quả + đọc báo cáo |
| 4 | Self-evolving: skill do curator sinh (Phần 3) | 16 | Kiểm tra kết quả + đọc báo cáo |
| 5 | Bảng so sánh và quy trình đóng băng (Phần 4) | 10 | `lab.compare` + `scripts/verify_freeze.py` |
| 6 | Báo cáo (Phần 0, 5) | 20 | Đọc báo cáo |
| | **Tổng** | **100** | |
| | Thưởng: thử thách mở rộng (Phần 6) | +5 | Đọc phụ lục |

---

## 1. Cài đặt harness - 30 điểm (tự động)

Chạy `pytest` trên mã nguồn của sinh viên. Điểm của mỗi tệp test = điểm tối đa × (số test đạt / tổng số test của tệp).

| Tệp test | Nội dung | Điểm |
|---|---|---|
| `tests/test_02_agent.py` (9 test) | `make_backend` tìm thấy `python` và không lộ khóa API; công cụ tệp và shell dùng chung đường dẫn tương đối; `build_agent` ở hai chế độ; subagent nhận quy ước đường dẫn; nạp skill khi và chỉ khi được yêu cầu; `get_subagents` hợp lệ | 10 |
| `tests/test_03_runner.py` (6 test) | `run_task` ghi bản ghi đầy đủ (gồm `skills_sha256`, `timestamp`); không sửa `tasks/*/workspace`; ghi lỗi thay vì ném ngoại lệ; phát hiện sửa skill; đếm `skills_read` (số skill khác nhau) và `subagent_calls`. Test đếm điều kiện (`test_three_conditions_defined`) đạt sẵn vì `CONDITIONS` được cung cấp. | 12 |
| `tests/test_04_curator.py` (2 test) | `curate_skills` chỉ ghi skill hợp lệ, không đưa tác vụ đánh giá vào prompt, có đưa phản hồi `detail` của tác vụ học, không cho tên chứa `../`; không gọi mô hình khi không có check thất bại | 8 |

`tests/test_01_provided.py` (15 test) kiểm tra mã có sẵn (gồm `validate_skill`, `parse_skill_blocks`, `compare`, `make_model`), không tính điểm nhưng phải đạt.

Điều kiện: sinh viên không được sửa thư mục `tests/`, `tasks/`, `scripts/` hay các tệp có sẵn (`model.py`, `tasks.py`, `grading.py`, `testing.py`, `compare.py`, hằng số prompt, `render_trace`, `main` của runner, `validate_skill`, `parse_skill_blocks`). Giảng viên chạy test trên bản gốc của các tệp này.

---

## 2. Chạy tác vụ học, đường cơ sở và phân loại lỗi - 14 điểm

| Tiêu chí | Điểm | Mức đạt đầy đủ |
|---|---|---|
| 2.1 Đủ kết quả `baseline` | 4 | `results/baseline/` có `run.json` và `trace.md` hợp lệ cho cả 6 tác vụ. Thiếu mỗi tác vụ trừ 1 (tối đa 4). |
| 2.2 Bảng phân loại lỗi | 10 | Xem bảng mức độ dưới đây. |

**Mức độ cho 2.2.** Dựa trên các check thất bại của tác vụ học trong kết quả `baseline` (hoặc lần chạy đầu tiên còn lưu).

| Điểm | Mô tả |
|---|---|
| 9 - 10 | Phân loại ít nhất 4 check thất bại; mỗi dòng có bằng chứng cụ thể (tên tác vụ, tên check, trích `detail` hoặc vết); chỉ ra nhóm lỗi chiếm đa số và nguyên nhân chung. Nếu mọi lỗi thuộc cùng một nhóm (thường là nhóm E), sinh viên phải nêu bằng chứng phủ định cho các nhóm còn lại, ví dụ số check kỹ thuật đạt/tổng từ `scripts/check_breakdown.py`. |
| 6 - 8 | Phân loại đúng nhưng bằng chứng chung chung hoặc thiếu trích dẫn. |
| 3 - 5 | Liệt kê lỗi nhưng chưa phân nhóm, hoặc phân nhóm sai so với `detail` và vết. |
| 0 - 2 | Thiếu hoặc không dựa trên dữ liệu thực tế. |

Lỗi do hạ tầng (API lỗi, hết thời gian) không được tính là lỗi của tác tử và không dùng làm bằng chứng.

---

## 3. Đa tác tử (subagent) - 10 điểm

| Tiêu chí | Điểm | Mức đạt đầy đủ |
|---|---|---|
| 3.1 Thiết kế subagent | 3 | Ít nhất 2 subagent có vai trò khác nhau; `description` nêu rõ khi nào gọi; `system_prompt` có phạm vi rõ ràng. |
| 3.2 Đủ kết quả `subagents` | 3 | `results/subagents/` đủ 6 tác vụ hợp lệ. |
| 3.3 Nhận xét từ số liệu và vết | 4 | Báo cáo mục 5 dựa vào `subagent_calls` và `trace.md`: có giao việc không, subagent nào, thông tin truyền đi đủ hay thiếu, ảnh hưởng đến token. Nếu subagent không được gọi lần nào, giải thích hợp lý vẫn đạt điểm tối đa. |

---

## 4. Self-evolving: skill do curator sinh - 16 điểm

| Tiêu chí | Điểm | Mức đạt đầy đủ |
|---|---|---|
| 4.1 Curator hoạt động | 5 | `skills/auto/` có ít nhất 1 skill hợp lệ do `python -m lab.curator` sinh ra, không bị sửa tay. |
| 4.2 Đánh giá skill sinh ra | 5 | Báo cáo mục 6 trả lời đủ 3 câu hỏi cho từng skill (tổng quát, đúng hay sai, độ dài và `description`) bằng nhận xét dựa trên nội dung thật; nếu xóa skill hoặc chạy lại curator thì ghi lý do. |
| 4.3 Kết quả chính thức | 3 | `results/skills-auto/` đủ 6 tác vụ; `python scripts/verify_freeze.py` không báo lỗi. |
| 4.4 Giải thích việc dùng skill | 3 | Báo cáo dùng `skills_read` và `trace.md` để giải thích vì sao skill được đọc hoặc không, được làm theo toàn bộ hay một phần. |

---

## 5. Bảng so sánh và quy trình đóng băng - 10 điểm

| Tiêu chí | Điểm | Mức đạt đầy đủ |
|---|---|---|
| 5.1 Bảng so sánh | 5 | `report/table.md` do `lab.compare` sinh ra, khớp với các `run.json` (giảng viên chạy lại `python -m lab.compare` để đối chiếu); đủ 3 cột, 6 hàng tác vụ, các hàng tổng hợp. |
| 5.2 Quy trình đóng băng | 5 | `python scripts/verify_freeze.py` báo OK (có commit `hypotheses` với H1 đến H3 đã điền, đứng trước tag `freeze`; `skills/` không đổi từ tag; mọi lần chạy `skills-auto` dùng đúng skill đã đóng băng và bắt đầu sau thời điểm tag). |

---

## 6. Báo cáo - 20 điểm

| Tiêu chí | Điểm | Mức đạt đầy đủ |
|---|---|---|
| 6.1 Giả thuyết | 4 | Dự đoán cụ thể, có lý do, có căn cứ từ tài liệu tham khảo; được commit trước tag `freeze`. |
| 6.2 Phân tích kết quả | 8 | Xem bảng mức độ dưới đây. Báo cáo cả điểm tác vụ học ở Phần 3.4 và sau đóng băng của cùng bộ skill, dùng chênh lệch làm ước lượng nhiễu. |
| 6.3 Hạn chế và tính hợp lệ | 4 | Nêu và giải thích ít nhất 3 hạn chế (số tác vụ nhỏ, một lần chạy, nhiễu, tác vụ do giảng viên thiết kế, quá khớp, mô hình duy nhất) và ảnh hưởng của từng hạn chế đến kết luận. |
| 6.4 Trình bày và tái lập | 4 | Báo cáo đủ các mục của mẫu, kể cả mục 3 (câu hỏi làm quen Phần 0.3); ghi rõ mô hình, tham số, lệnh chạy, commit; ngôn ngữ kỹ thuật chính xác; có thể tái lập từ README. |

**Mức độ cho 6.2.**

| Điểm | Mô tả |
|---|---|
| 7 - 8 | So sánh điều kiện bằng số liệu, tách tác vụ học và tác vụ đánh giá và tách check kỹ thuật với check quy ước (`rule_`); giải thích cơ chế bằng vết và `skills_read`; phân tích chi phí token; nhận xét về quá khớp hoặc rò rỉ; kết luận khớp với số liệu và không khẳng định quá mức. Kết quả âm hoặc không khác biệt vẫn đạt mức này nếu được phân tích tốt. |
| 5 - 6 | Số liệu đúng và có so sánh, nhưng giải thích cơ chế còn chung chung hoặc thiếu phân tích chi phí. |
| 3 - 4 | Mô tả kết quả nhưng ít diễn giải; kết luận chưa gắn với số liệu. |
| 0 - 2 | Không có phân tích, hoặc kết luận mâu thuẫn với số liệu. |

---

## Thưởng: thử thách mở rộng - tối đa +5

Một hướng trong Phần 6 của `GUIDE.md`, thực hiện đầy đủ và có số liệu. Tiêu chí:

| Tiêu chí | Điểm |
|---|---|
| Thiết kế thí nghiệm rõ ràng, tách biệt khỏi kết quả chính (thư mục kết quả riêng) | +1 |
| Có số liệu so sánh với kết quả chính | +1 |
| Phân tích cơ chế dựa trên vết | +1 |
| Nêu hạn chế và đề xuất bước tiếp theo | +1 |
| Chất lượng mã và khả năng tái lập | +1 |

Điểm thưởng chỉ được tính khi các hạng mục 1 đến 6 đã hoàn thành.

## Trừ điểm

| Vi phạm | Trừ |
|---|---|
| Để lộ khóa API trong kho mã nguồn, vết hoặc báo cáo | -10 |
| Sao chép nội dung tác vụ đánh giá hoặc đáp án vào skill, hoặc sửa tay nội dung `skills/auto/` | -10 |
| Sửa `tests/`, `tasks/`, `check.py` hoặc các tệp có sẵn | -10 |
| `verify_freeze.py` báo skill đổi sau tag nhưng báo cáo kết quả như thể không đổi | -10 |
| Kết quả hoặc số liệu trong báo cáo không khớp `results/` | -5 đến -10 |
| Nộp trễ | Theo quy định của lớp |

Việc mở tệp `check.py` hay `run.json` của tác vụ đánh giá trước khi đóng băng không thể kiểm chứng tự động; giảng viên chỉ trừ điểm khi có bằng chứng (ví dụ skill chứa nội dung chỉ có trong tác vụ đánh giá, hoặc lịch sử git).

Nếu có nghi vấn sao chép giữa các sinh viên, giảng viên đối chiếu `results/`, `skills/` và báo cáo; bài có nội dung trùng bất thường nhận 0 điểm hạng mục liên quan.

## Quy trình chấm gợi ý cho giảng viên

```bash
git clone <kho-của-sinh-viên> && cd <kho>
# Chép lại thư mục tests/, tasks/, scripts/ và các tệp có sẵn trong src/lab/ từ kho gốc của giảng viên, rồi:
pip install -e .
pytest                                  # hạng mục 1
python scripts/verify_freeze.py         # hạng mục 4.3, 5.2
python -m lab.compare                   # hạng mục 5.1 (so với report/table.md)
python scripts/check_breakdown.py       # hỗ trợ đối chiếu mục 6.2 (kỹ thuật so với quy ước)
```
