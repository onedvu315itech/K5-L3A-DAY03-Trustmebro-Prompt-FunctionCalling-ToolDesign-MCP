# Gợi ý sửa sau v0

Rút từ log thật: `starter_v0/runs/v0_B_base_openrouter_20261110T111752296069.json`

- Model: `nvidia/nemotron-3-ultra-550b-a55b:free` (miễn phí trên OpenRouter, gọi tool được)
- Kết quả v0: **15/20 PASS**

| Chỉ số | Giá trị |
|---|---|
| case_accuracy | 0.75 |
| tool_routing_accuracy | 0.95 |
| argument_accuracy | 0.75 |
| multiturn_accuracy | 0.83 |

Lệnh chạy (thêm `--model` vì model mặc định của starter là bản trả phí):
```bash
python run_eval.py --provider openrouter --model nvidia/nemotron-3-ultra-550b-a55b:free --version v1 --suite base --eval-cases data/eval_base.json
```

---

## 5 case FAIL và cách sửa

### Lỗi 1. Nhồi thêm chữ vào `query` (3 case: R03, R13, M02)
- **Mong đợi:** `query="AI"`
- **Model gửi:** `query="AI news today artificial intelligence breakthroughs"`
- **Vì sao sai:** "tin tức" và "hôm nay" đã có tham số riêng là `topic=news` và `timeframe=day`, không cần nhét vào `query`.
- **Sửa ở** `artifacts/tools.yaml`, phần `description` của param `query` trong `lookup` và `social_search`:
  > Chỉ ghi chủ đề cốt lõi (vd `AI`, `robotics`). KHÔNG thêm "news", "today", "latest", từ đồng nghĩa: những thứ đó đã có `topic` / `timeframe` / `search_type`.

### Lỗi 2. Đoán thay vì hỏi lại (R10)
- **Mong đợi:** gọi `clarify` để hỏi xem là tài khoản nào.
- **Model gửi:** `timeline(screenname="sama")`, tức tự đoán là Sam Altman.
- **Vì sao sai:** prompt v0 dặn thẳng: "pick a well-known account like Sam Altman".
- **Sửa ở** `artifacts/system_prompt.md`:
  - Xoá các câu bảo "đừng hỏi lại", "đoán đại", "pick Sam Altman", "assume a likely URL".
  - Thêm câu: **Thiếu tài khoản / URL / thông tin bắt buộc → gọi `clarify`, không đoán.**

### Lỗi 3. Gửi Telegram mà không xin xác nhận yes/no (R12)
- **Mong đợi:** `clarify(response_type="yes_no")`
- **Model gửi:** `clarify(response_type="text")`
- **Sửa ở:**
  - `system_prompt.md`: xoá câu "just go ahead and do it". Thêm: **Trước khi `send`, luôn gọi `clarify` với `response_type="yes_no"` để xác nhận.**
  - `tools.yaml`, phần `send`: ghi rõ "Chỉ gọi khi user đã trả lời yes; truyền `confirmed=true`."

---

## Đề xuất chia version (mỗi version một giả thuyết)

| Version | Sửa file | Giả thuyết | Case kỳ vọng hết lỗi |
|---|---|---|---|
| v1 | `system_prompt.md` | Bỏ chỉ dẫn xấu + thêm luật hỏi lại / xác nhận thì hết đoán bừa | R10, R12 |
| v2 | `tools.yaml` | Mô tả rõ `query` chỉ chứa chủ đề thì hết nhồi chữ | R03, R13, M02 |
| v3 | prompt / yaml | Sửa các lỗi còn sót hoặc lỗi mới phát sinh ở v2 | (đọc log v2) |

Sau mỗi version:
1. Chạy eval với `--version vN`.
2. Ghi một dòng vào `artifacts/version_log.csv`.
3. Chạy `pytest tests/test_tool_contract.py`.

---

## Lưu ý
- **Chưa có `RAPIDAPI_KEY`:** `timeline` và `social_search` chạy ra lỗi "Missing key". Eval **vẫn chấm đúng** vì chỉ chấm tên tool và args, nhưng chat hay demo sẽ không có dữ liệu tweet. Nên lấy key trước khi demo.
- **Model free hay bị 429** (giới hạn lượt gọi). Nếu gặp, đợi một lúc rồi chạy lại, hoặc thử model free khác (`google/gemma-4-31b-it:free`).
- **Không sửa** `data/eval_base.json`.
