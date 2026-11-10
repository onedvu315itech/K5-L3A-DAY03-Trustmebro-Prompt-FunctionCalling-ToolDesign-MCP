# Gợi ý sửa sau v3

Rút từ log thật: `starter_v0/runs/<tên file log v3>.json`

- **Model:** `openai/gpt-4o-mini` qua OpenRouter
- **Kết quả:** **<số case đạt>/<tổng số case> PASS** (còn đúng 1 case FAIL, xem bên dưới)
- **Artifact version:** `<điền từ log>`

| Chỉ số | v3 |
|---|---:|
| case_accuracy | <điền từ log> |
| tool_routing_accuracy | <điền từ log> |
| argument_accuracy | <điền từ log> |
| multiturn_accuracy | <điền từ log> |

> Lưu ý: chỉ so sánh điểm giữa các lần chạy cùng model và cùng bộ case. Không kết luận tăng hay giảm từ log của model khác.

## Case FAIL còn lại và cách sửa

### Lỗi 1. `<CASE_ID>` (multiturn_carryover): gọi thừa `social_search` khi đã đúng `lookup`

- **Tình huống:** 3 lượt: "Tin AI hôm nay có gì?" → "Còn về robotics thì sao?" → "Chỉ tìm robotics thôi, vẫn là tin hôm nay".
- **Mong đợi:** `lookup(query="robotics", topic="news", timeframe="day")` và không có tool nào khác.
- **Model gửi:** `lookup(query="robotics", topic="news", timeframe="day")` và thêm `social_search(query="robotics", search_type="Latest")`.
- **Loại lỗi:** `wrong_arg_value`, `extra_tool_call`.
- **Vì sao sai:** `lookup` và các arguments đã đúng (query, topic, timeframe đều carry over tốt). Lỗi chỉ là tool thừa, vì hai dòng trong prompt kéo model về phía `social_search`:
  1. Quy tắc "Social or real-time information: use social_search" khiến "tin hôm nay" bị hiểu là thông tin real-time.
  2. Chưa có quy tắc nói rõ từ chỉ thời gian chỉ đặt `timeframe` và không đổi nguồn, cũng như chưa cấm gọi thêm một nguồn thứ hai để đối chiếu.

### Hướng sửa

**1. `artifacts/system_prompt.md`, mục TOOLS AND ROUTING: bỏ phần "real-time" của social.**

Thay dòng "Social or real-time information: use social_search ..." bằng:
```
- Social information: use social_search. This covers what people are saying (opinions, public reaction, discussions, trending topics). Time words such as "today", "now", "hôm nay", "mới nhất" never make a request social. If the user names a specific account, use timeline instead.
```

**2. Cùng mục: mỗi chủ đề tin tức chỉ dùng một nguồn.**

Thêm vào cuối dòng bắt đầu bằng "News means original, legally published information":
```
 Time words ("today", "hôm nay", "this week") only set timeframe; they never change the source. Once a request is news, call lookup and nothing else. Do not add social_search as a second opinion, a cross-check, or a fallback.
```

**3. Mục CONVERSATION CONTEXT AND SOURCE SWITCHING: tin nhắn thu hẹp không thêm nguồn.**

Thêm hai dòng:
```
- If the latest message narrows the request ("chỉ tìm robotics thôi", "only robotics"), make exactly one call, for that topic, with the source from the conversation. A narrowing message never adds a source.
- "Vẫn là" / "still" / "same as before" means keep the earlier source and timeframe. Do not re-decide the source.
```

**4. Mục ARGUMENTS: carry-over `timeframe`.**

Thay dòng về optional arguments bằng:
```
- Set optional arguments (limit, max_results, timeframe) only when the user gave a value, in the latest message or an earlier turn, and use exactly that value. "Hôm nay" or "today" means timeframe=day. A value from an earlier turn carries over until the user changes it. Never invent defaults.
```

**5. `artifacts/tools.yaml`: siết mô tả `social_search` để chặn tin tức.**

Thay `description` bằng:
```
Search X posts by keyword. Use only for what people are saying: opinions, reactions, discussions, trends. Never use it to find, confirm, or fill in news, announcements, or articles (in Vietnamese: tin, tin tức, tin mới nhất), even news shared on X; use lookup for all news. Reactions to a news event are allowed, but the news itself must come from lookup. Do not use it for posts from one named account (use timeline). The word latest alone is not a reason to use this tool. Results are unverified posts, not news. Keep query to the core topic and do not add words such as news, today, or latest.
```

**6. (Khuyến nghị) Chặn trong code.** Mô hình nhỏ như `gpt-4o-mini` đôi khi bỏ qua quy tắc trong prompt. Thêm kiểm tra phía ứng dụng: từ chối `social_search` trong cùng lượt đã gọi `lookup` với `topic=news`.

## Đã đạt trong v3

Các case còn lại đều đạt, gồm hai lỗi của v2 là R12 (xác nhận gửi dùng `yes_no`) và M03 (handle `karpathy`). Khi sửa lỗi trên, kiểm tra để các thay đổi không làm hỏng:
- case chuyển nguồn (ví dụ "Bỏ Twitter, chuyển sang tìm tin tức trên web") vẫn chỉ gọi `lookup`;
- case phản ứng của mọi người về một tin vẫn được dùng `social_search` (chỉ phần phản ứng);
- case sửa tên tài khoản vẫn giữ `limit`.

## Chạy version tiếp theo

Sau khi lưu thay đổi, chạy bằng cùng model:

```powershell
python run_eval.py --version v4 --provider openrouter --model openai/gpt-4o-mini --suite base --eval-cases data/eval_base.json --system-prompt artifacts/system_prompt.md --tools artifacts/tools.yaml
```

**Kỳ vọng:** case multiturn_carryover đạt, đồng thời các case đã đạt ở v3 vẫn đạt. Đây là mục tiêu cần kiểm tra; chỉ run mới xác nhận được điểm.