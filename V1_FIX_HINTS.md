# Gợi ý sửa v2

Rút từ log thật của v1: `starter_v0/runs/v1_B_base_openrouter_20261110T114359725551.json`

- Model: `nvidia/nemotron-3-ultra-550b-a55b:free` (cùng model với v0 của Long để so sánh công bằng)
- Kết quả v1: **18/20 PASS**
- Artifact version: `v1+p7cd5dc4c7059+t5b22a2476d41`

| Chỉ số | v0 (Long) | v1 |
|---|---|---|
| case_accuracy | 0.75 | 0.90 |
| tool_routing_accuracy | 0.95 | 1.0 |
| argument_accuracy | 0.75 | 0.90 |
| multiturn_accuracy | 0.83 | 0.833 |

v1 đã sửa được: R03, R13, M02 (rule `query` ngắn) và R10 (hỏi lại thay vì đoán `sama`).

---

## 2 case FAIL còn lại và cách sửa

### Lỗi 1. R12: gửi/đăng nhưng hỏi bằng `text` thay vì `yes_no`

- **Input:** "Đăng bản tin này lên Telegram giúp mình"
- **Mong đợi:** `clarify(response_type="yes_no")`
- **Model gửi:** `clarify(question="Bạn muốn đăng nội dung gì lên Telegram?...", response_type="text")`
- **Vì sao sai:** prompt v1 có hai rule va nhau. Rule "thiếu thông tin thì `clarify` kiểu `text`" thắng rule "gửi/đăng thì `clarify` kiểu `yes_no`", vì model thấy chưa có nội dung bản tin nên coi là thiếu thông tin.
- **Sửa ở `artifacts/system_prompt.md`:** đặt rule gửi/đăng **ưu tiên cao hơn** rule thiếu thông tin, và nói rõ áp dụng kể cả khi chưa có nội dung.

### Lỗi 2. M05: mất giá trị `limit` giữa các lượt (regression)

- **Hội thoại:** "Lấy 10 tweet mới nhất của Elon Musk" → "Cho mình 3 thôi" → "Vẫn của Elon Musk nhé"
- **Mong đợi:** `timeline(screenname="elonmusk", limit=3)`
- **Model gửi:** `timeline(screenname="elonmusk", limit=5)`
- **Vì sao sai:** câu "Do not add optional arguments unless the user asked" (thêm ở v1) khiến model bỏ giá trị `limit=3` user đã nêu ở lượt 2, rồi quay về mặc định 5. Lượt 3 user không nhắc lại số lượng.
- **Sửa ở `artifacts/system_prompt.md`:** thêm rule giữ lại các giá trị user đã nêu ở lượt trước cho đến khi user đổi.

---

## Nội dung `artifacts/system_prompt.md` cho v2

Chỉ đổi 2 chỗ so với v1: thêm rule giữ giá trị giữa các lượt (mục Arguments) và viết lại mục Sending cho ưu tiên cao hơn.

```markdown
You are a research assistant with tools for tweets, web search, reading URLs, and sending messages.

Routing:
- A specific user's tweets: use the user timeline tool.
- Searching tweets by keyword: use the social search tool.
- News or web information: use the web lookup tool.
- Reading a specific URL: use the fetch tool.
- If the request needs both web and tweets, call both tools in the same turn.

Arguments:
- Keep query short: use only the core topic keyword (for example "AI", "robotics"). Do not add words like "news", "today", "latest" to query, because time and news intent are expressed through the topic and timeframe arguments.
- Do not add optional arguments (such as limit or max_results) unless the user asked for a specific value.
- In a multi-turn conversation, keep values the user already stated in earlier turns (limit, timeframe, handle, topic) until the user changes them. A later message that only changes one thing (for example the account name) must still carry over the earlier limit and timeframe.

Missing information:
- If a required argument (handle, URL, query) is missing, call clarify with response_type=text to ask a short question. Never guess or invent it, and do not call another tool until you have it.

Sending (this rule takes priority over "Missing information"):
- Any request to send, post or publish something (for example "post this to Telegram") must FIRST be answered with clarify using response_type=yes_no, asking the user to confirm. Do this even if the content is not yet provided. Never use response_type=text for a send or post request, and never send before the user confirms.

Out of scope:
- If the request is not about tweets, web search or reading a URL (for example writing code), answer directly or decline. Do not call any tool.
```

Ghi đè bằng PowerShell (chạy trong thư mục `starter_v0`, chạy cả khối từ `@'` đến `Set-Content`) hoặc dán nội dung trong khối trên vào file bằng editor, lưu UTF-8.

---

## Chạy v2

```powershell
python run_eval.py --version v2 --provider openrouter --model nvidia/nemotron-3-ultra-550b-a55b:free --system-prompt artifacts/system_prompt.md
```

Kiểm tra dòng `Artifact version`: hash prompt phải khác `p7cd5dc4c7059`, còn `tools_hash` vẫn là `t5b22a2476d41` (v2 chỉ sửa prompt).

### Kỳ vọng

| Case | v1 | v2 kỳ vọng |
|---|---|---|
| R12 | FAIL | PASS |
| M05 | FAIL | PASS |
| Các case còn lại | PASS | giữ nguyên (không regression) |

Tổng: khoảng 20/20, `case_accuracy` 1.0. Model free có nhiễu giữa các lần chạy, nên nếu kết quả lệch 1 case, chạy lại một lần để xác nhận.

### Cần kiểm tra regression

- R05, R07 (limit, search_type): rule giữ giá trị giữa các lượt có thể làm model giữ nhầm giá trị cũ.
- M03, M06 (đổi handle, đổi tool): đảm bảo model vẫn đổi theo ý user mới.
- R08, R14 (out-of-scope): rule Sending mới không được kéo model gọi `clarify` bừa.

---

## Ghi `artifacts/version_log.csv`

Đổi `TenBan` thành tên bạn, điền `metric_after` theo kết quả thật:

```powershell
Add-Content -Encoding utf8 artifacts\version_log.csv "v2,TenBan,system_prompt,v2+<prompt_hash>+t5b22a2476d41,<prompt_hash>,t5b22a2476d41,rule yes_no uu tien cho send va giu gia tri giua cac luot,rule yes_no uu tien se sua R12 va rule carry-over se sua M05,case_acc=0.90,case_acc=<ket qua>,runs/<ten file run v2>.json"
```

Không dùng dấu phẩy trong các ô văn bản để CSV không lệch cột.

---

## Nếu v2 vẫn còn lỗi: v3 sửa `artifacts/tools.yaml`

Nếu R12 vẫn FAIL, nguyên nhân nhiều khả năng nằm ở khai báo tool: `response_type` của `clarify` đang có `default: "text"` và không bắt buộc, nên model bỏ qua hoặc mặc định `text`. Trên máy bạn, đổi này đã đưa R10, R11 từ FAIL lên PASS.

Các thay đổi ở v3 (chỉ đụng `tools.yaml`, không đổi tên tool hay tên tham số):

- `clarify`: bỏ `default` ở `response_type`, đặt `required: [question, response_type]`, mô tả: `text` khi xin thông tin còn thiếu, `yes_no` khi xin xác nhận gửi/đăng.
- `send`: ghi rõ chỉ gọi khi user đã xác nhận và đặt `confirmed=true`; chưa xác nhận thì gọi `clarify` với `yes_no`.
- `lookup`, `social_search`: ghi vào mô tả `query` "chỉ chủ đề cốt lõi, không thêm news/today/latest".
- Các tool còn lại: viết lại `description` theo mẫu làm gì / khi nào dùng / khi nào không dùng.

Sau khi sửa:

```powershell
python -c "import yaml;print(len(yaml.safe_load(open('artifacts/tools.yaml',encoding='utf-8'))['tools']))"
pytest tests/test_tool_contract.py
python run_eval.py --version v3 --provider openrouter --model nvidia/nemotron-3-ultra-550b-a55b:free --system-prompt artifacts/system_prompt.md --tools artifacts/tools.yaml
```

Lệnh đầu phải in `10`, `pytest` phải xanh.

---

## Đề xuất chia version

| Version | Sửa file | Giả thuyết | Case kỳ vọng hết lỗi |
|---|---|---|---|
| v1 | `system_prompt.md` | Bỏ chỉ dẫn xấu, thêm rule hỏi lại, yes_no, out-of-scope, query ngắn | R10, R03, R13, M02 (đã đạt) |
| v2 | `system_prompt.md` | Rule yes_no ưu tiên cho send + giữ giá trị giữa các lượt | R12, M05 |
| v3 | `tools.yaml` | Description rõ ràng + bắt buộc `response_type` ở `clarify` | R12 nếu v2 chưa đủ, và làm prompt bớt phụ thuộc |

## Lưu ý

- Không sửa `data/eval_base.json`.
- Mỗi lần chạy có thay đổi thì đặt tên version mới, không chạy lại cùng một version.
- Chạy mọi lệnh trong thư mục `starter_v0`.
- Chỉ so sánh `metric_before` và `metric_after` trong cùng một model. Ghi rõ model trong báo cáo.
- Model free hay gặp lỗi 429 (giới hạn lượt gọi). Nếu gặp, đợi một lúc rồi chạy lại.