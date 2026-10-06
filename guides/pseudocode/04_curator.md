# Pseudo-code 04 - `src/lab/curator.py`

**Mục tiêu.** Tự động viết skill từ các lần chạy thất bại của **tác vụ học** (learning task). Đây là bước "tiến hóa" (evolution) ở tầng ngữ cảnh (context layer): tác tử không đổi trọng số, chỉ đổi tri thức thủ tục (procedural knowledge) mà nó được cung cấp.

**Kiểm tra.** `pytest tests/test_04_curator.py` (và `tests/test_01_provided.py` cho phần có sẵn).

Bạn chỉ cài đặt `curate_skills`; `validate_skill` và `parse_skill_blocks` đã có sẵn trong `curator.py` vì đây là phần dễ sai và liên quan bảo mật. Hãy đọc chúng để hiểu vì sao tên skill được kiểm tra.
**Chạy thật.** `python -m lab.curator` (sau khi đã chạy điều kiện `baseline` trên tác vụ học).

---

## Bước 1 (CÓ SẴN, chỉ để tham khảo). `validate_skill(text, expected_name=None)`

```text
HÀM validate_skill(text, expected_name) -> danh sách chuỗi mô tả vấn đề:
    problems = []
    tách text thành frontmatter (giữa hai dòng '---') và body   (regex DOTALL)
    NẾU không tách được: TRẢ VỀ ["missing YAML frontmatter"]
    name = giá trị của dòng "name:" ;  description = giá trị của dòng "description:"
    NẾU name thiếu, hoặc không khớp ^[a-z0-9]+(-[a-z0-9]+)*$, hoặc dài hơn 64: thêm "invalid name"
    NGƯỢC LẠI NẾU expected_name khác None và name != expected_name: thêm "name differs from the block name"
    NẾU description thiếu hoặc dài hơn 1024: thêm "missing or too long description"
    NẾU body có hơn 80 dòng: thêm "body longer than 80 lines"
    VỚI MỖI marker TRONG eval_markers():            # hàm có sẵn, tính lúc chạy từ tasks/*-eval/
        NẾU marker xuất hiện trong text (không phân biệt hoa thường): thêm "mentions evaluation material: <marker>"
    TRẢ VỀ problems
```

Quy tắc `name` khớp biểu thức chính quy an toàn và bằng tên khối là **biện pháp bảo mật**: tên khối do mô hình sinh ra được dùng để tạo đường dẫn tệp, nên một tên như `../evil` không được phép lọt qua.

## Bước 2 (CÓ SẴN, chỉ để tham khảo). `parse_skill_blocks(reply)`

Mô hình đôi khi quên dòng `=== END ===`. Biểu thức chính quy "tham lam ít" kết thúc ở `=== END ===` sẽ nuốt nhiều skill vào một khối. Kết thúc khối cần ở **điểm nào đến trước** trong ba điểm: `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản.

```text
HÀM parse_skill_blocks(reply):
    mẫu = re.compile( r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M )
    TRẢ VỀ [(tên, nội dung đã strip) cho mỗi khớp của mẫu trong reply]
```

## Bước 3 (việc bạn cài đặt). `curate_skills(...)`

```text
HÀM curate_skills(results_dir, source_condition, out_dir, model, max_skills):
    out_dir mặc định = ROOT / "skills" / "auto"

    runs = []
    VỚI MỖI tệp results_dir/source_condition/*/run.json:
        r = đọc JSON
        BỎ QUA NẾU r["role"] != "learn"             # tuyệt đối không dùng dữ liệu tác vụ đánh giá
        trace = đọc trace.md cùng thư mục (nếu có), chỉ lấy ~6000 ký tự CUỐI
        failed = (tên, detail) của các check có passed == False   # detail = nhận xét của bot đánh giá (quy tắc bị vi phạm)
        runs.thêm({task, failed, trace})

    NẾU không có run nào có failed khác rỗng:
        in cảnh báo "không có check thất bại ở tác vụ học"; TRẢ VỀ []     # không gọi mô hình

    prompt = PROMPT_MẪU điền: max_skills và, với mỗi run, danh sách check thất bại (tên và detail) + vết
    reply  = model.invoke(prompt).content                     # model mặc định: make_model()

    written = []
    VỚI MỖI (name, text) TRONG parse_skill_blocks(reply):
        NẾU đã đủ max_skills, HOẶC validate_skill(text, expected_name=name) còn vấn đề: BỎ QUA
        ghi out_dir/name/"SKILL.md"
        written.thêm(đường dẫn)
    TRẢ VỀ written
```

Trường `detail` của check thất bại ở **tác vụ học** là nhận xét của bot đánh giá: nó phát biểu quy tắc bị vi phạm (ví dụ "RULE: ...") hoặc nêu giá trị mô hình đã xuất ra; nó **không chứa đáp án**. Đây chính là phản hồi (feedback) để rút ra skill. Trường `detail` của **tác vụ đánh giá** luôn rỗng và curator không bao giờ đọc tác vụ đánh giá.

## Mẫu prompt gợi ý cho curator

```text
Bạn viết SKILL cho một tác tử lập trình và phân tích dữ liệu.
Dưới đây là các check thất bại (tên và nhận xét của bot đánh giá) và vết của các lần chạy.
Hãy tìm các lỗi QUY TRÌNH chung (không phải đáp án cụ thể) và viết tối đa {max_skills} skill ngắn
giúp tránh các lỗi đó trên tác vụ MỚI cùng loại.

Quy tắc:
- Skill phải tổng quát: không nêu id tác vụ, không nêu tên tệp riêng của một tác vụ, không nêu đáp án hay con số.
- Mỗi skill có frontmatter YAML gồm `name` (chữ thường, gạch ngang) và `description` (một câu: DÙNG KHI NÀO),
  sau đó tối đa 40 dòng chỉ dẫn mệnh lệnh (danh sách kiểm tra - checklist - hoạt động tốt).
- Định dạng đầu ra, đúng từng ký tự:
=== SKILL: <name> ===
---
name: <name>
description: <khi nào dùng>
---
<nội dung>
=== END ===

{các lần chạy}
```

Prompt mẫu viết bằng tiếng Anh vì mô hình và các tác vụ dùng tiếng Anh; có thể viết tiếng Việt nếu bạn muốn thử so sánh.

## Lưu ý khoa học

- Nghiên cứu **SkillsBench** ghi nhận skill do con người biên soạn (khác với skill do mô hình tự sinh như ở lab này) tăng tỉ lệ đạt trung bình khoảng 16 điểm phần trăm, còn skill do mô hình tự sinh trung bình không có lợi. Nghiên cứu **SkillEvolBench** ghi nhận lợi ích trên tác vụ học thường không chuyển sang tác vụ mới (quá khớp - overfitting). Hãy đưa các điều này vào giả thuyết ở báo cáo và kiểm chứng bằng số liệu của bạn.
- Skill ngắn, tập trung (2 đến 3 mô-đun) thường hiệu quả hơn tài liệu dài.
- Curator có tính ngẫu nhiên: cùng đầu vào có thể cho skill khác nhau, và một skill hợp lệ về định dạng vẫn có thể **sai hoặc có hại**. Luôn đọc từng skill do curator sinh ra (GUIDE Phần 3.3). Skill có hại phải bị xóa hoặc curator phải chạy lại; ghi lý do vào báo cáo. Không sửa tay nội dung skill trong `skills/auto/`.
