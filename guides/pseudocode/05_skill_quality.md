# Hướng dẫn 05 - Chất lượng của một skill (để đánh giá skill do curator sinh)

Tài liệu này không phải pseudo-code. Nó giải thích cấu trúc `SKILL.md` và các tiêu chí để đánh giá skill do curator sinh ra ở Phần 3.3. Curator tự viết skill, bạn không sửa tay; bạn chỉ đánh giá và quyết định giữ, xóa hoặc chạy lại curator.

## 1. Skill là gì

Skill là một thư mục chứa tệp `SKILL.md` (theo chuẩn Agent Skills) mô tả một **quy trình hoặc quy ước** mà tác tử nên làm theo. Deep Agents nạp skill theo cơ chế nạp dần (progressive disclosure):

1. Khi khởi động, tác tử chỉ thấy `name` và `description` của mọi skill.
2. Khi tác vụ phù hợp, tác tử tự đọc toàn bộ `SKILL.md`.

Hệ quả: `description` quyết định tác tử **có dùng** skill hay không. Phần thân (body) quyết định tác tử **làm gì** khi dùng.

## 2. Cấu trúc

```text
skills/auto/
  <ten-skill>/
    SKILL.md
```

```markdown
---
name: ten-skill
description: Một câu nêu DÙNG KHI NÀO (tình huống kích hoạt).
---

# Tiêu đề ngắn

1. Bước 1 (mệnh lệnh, kiểm chứng được).
2. Bước 2.
3. Điều kiện hoàn thành: ...
```

Ràng buộc kỹ thuật (do `validate_skill` kiểm tra): `name` chỉ gồm chữ thường, số và dấu gạch ngang, tối đa 64 ký tự, trùng tên khối; `description` có và tối đa 1024 ký tự; phần thân tối đa 80 dòng; không chứa định danh của tác vụ đánh giá.

## 3. Tiêu chí đánh giá một skill

| Tiêu chí | Câu hỏi kiểm tra | Dấu hiệu tốt | Dấu hiệu xấu |
|---|---|---|---|
| Tổng quát | Skill giúp được tác vụ **mới** cùng loại không? | Nêu quy trình hoặc quy ước theo loại lỗi | Lặp lại chi tiết riêng của một tác vụ (tên tệp, hàm, cột, con số) |
| Đúng | Làm theo skill có cho kết quả đúng không? | Khớp với phản hồi `detail` của bot đánh giá | Mâu thuẫn với `detail`, đề bài hoặc hướng dẫn gây hại (ví dụ cách đếm sai) |
| Ngắn | Có thừa không? | Tối đa khoảng 40 dòng, 2 đến 3 ý chính | Tài liệu dài, trùng lặp |
| Mệnh lệnh | Tác tử làm theo từng bước được không? | Danh sách đánh số, mỗi quy tắc một dòng, có danh sách tự kiểm tra | Đoạn văn mô tả chung chung |
| `description` | Tác tử có chọn đọc skill ở tác vụ mới không? | Bắt đầu bằng "Use when ..." và nêu loại tác vụ rộng | Quá hẹp hoặc chỉ nêu một tác vụ cụ thể |
| Không rò rỉ | Có đáp án hay định danh của tác vụ đánh giá không? | Không có | Có tên hoặc con số cụ thể |

Tên do **quy ước Acme** yêu cầu (tệp đầu ra như `clean.csv`, `tests/test_regressions.py`, khóa JSON như `meta`, tiêu đề) được phép vì chúng là chính quy tắc. Tên tệp dữ liệu, hàm, cột có sẵn trong workspace của tác vụ thì không.

## 4. Ví dụ (miền khác: viết thông điệp commit)

Không tốt:

```markdown
---
name: commit
description: Commit
---
Luôn viết "fix bug in utils.py line 42".
```

Tốt:

```markdown
---
name: write-commit-message
description: Dùng khi chuẩn bị tạo một commit git để thông điệp commit rõ ràng và nhất quán.
---

# Viết thông điệp commit

1. Chạy `git diff --staged` và đọc toàn bộ thay đổi trước khi viết.
2. Dòng đầu tối đa 72 ký tự, ở thể mệnh lệnh ("Add ...", "Fix ..."), nêu NỘI DUNG thay đổi.
3. Nếu thay đổi cần giải thích lý do, thêm một dòng trống và đoạn mô tả TẠI SAO.
4. Không gộp nhiều thay đổi không liên quan vào một commit.
```

## 5. Skill chỉ có tác dụng khi tác tử đọc và làm theo

Thực nghiệm cho thấy hai kiểu thất bại:

1. **Không đọc.** `skills_read` bằng 0: `description` quá hẹp hoặc không nêu tình huống kích hoạt.
2. **Đọc nhưng chỉ làm một phần.** Skill dài thường chỉ được áp dụng vài quy tắc, và khi đề bài nói khác (ví dụ "number" so với "số nguyên cent") tác tử có xu hướng làm theo đề.

Khi đánh giá skill, đối chiếu `skills_read` và `trace.md`: skill có được đọc không, tác tử có làm theo từng quy tắc không. Ghi nhận xét này vào mục 6 và mục 8 của báo cáo.
