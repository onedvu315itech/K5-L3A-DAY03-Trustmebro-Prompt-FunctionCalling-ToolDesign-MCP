# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: Trustmebro
- Members: [TEAM.md](./../../TEAM.md)
- Provider/model: OpenRouter

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì
Trustmebro là Research Agent được dùng để xem tweet của một tài khoản, tìm bài đăng theo chủ đề, tra cứu web, đọc nội dung URL, hỏi lại người dùng khi thiếu thông tin và gửi tin nhắn sau khi người dùng xác nhận yes/no.

**Link dùng thử:** [trustmebro-prompt.vercel.app](https://trustmebro-prompt.vercel.app/)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin (`text`), xin xác nhận yes/no trước khi gửi/đăng (`yes_no`), hoặc cho chọn từ danh sách (`choice`) | ❌ |
| timeline | lấy các bài đăng gần đây của một tài khoản X cụ thể (handle không có @, có `limit`) | ❌ |
| social_search | tìm bài đăng/thảo luận trên X theo từ khóa (`Latest` hoặc `Top`) | ❌ |
| lookup | tìm thông tin/tin tức trên web, có `topic` (general/news) và `timeframe` (day/week/month/year) | ❌ |
| fetch | đọc và trích nội dung từ một URL người dùng đưa | ❌ |
| format | định dạng các mục nghiên cứu đã thu thập thành digest Markdown (brief, sections, bullets, thread, daily_ai_vn) | ❌ |
| send | gửi văn bản tới Telegram đã cấu hình, chỉ sau khi người dùng xác nhận (`confirmed=true`) | ❌ |
| policy | tìm trong tài liệu chính sách nội bộ của lab (AI, trích dẫn, quyền riêng tư, xuất bản, dùng tool) | ❌ |
| papers | tìm bài báo trên arXiv theo chủ đề | ❌ |
| paper_text | tải và trích văn bản từ một bài arXiv đã biết ID/URL | ❌ |
| extract_urls | tách các link HTTP/HTTPS từ đoạn văn bản, bỏ trùng, không mở hay kiểm tra link | ✅ |
| wiki | lấy tóm tắt Wikipedia cho một khái niệm/người/tổ chức theo tên bài | ✅ |

## A3. Câu hỏi mẫu để thử

1. Dạo này Andrej Karpathy đang đăng gì? Cho mình xem 3 bài gần nhất.
2. Cộng đồng trên X đang tranh cãi gì về robotics? Ưu tiên bài được quan tâm nhiều nhất.
3. Tin công nghệ tuần này có gì đáng chú ý? Gom lại thành bản tin dạng gạch đầu dòng giúp mình.
4. Transformer là gì? Cho mình định nghĩa ngắn rồi tìm vài bài báo arXiv gần đây về chủ đề này.
5. Gửi bản tin vừa rồi lên Telegram nhé.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 | system_prompt.md	 | Bỏ các chỉ dẫn xấu của starter (đoán thay vì hỏi, gửi không cần xác nhận, ép một bước), thêm rule routing, hỏi lại khi thiếu thông tin, yes_no trước khi gửi, out-of-scope, và giữ query ngắn. Kỳ vọng sửa R10, R12 và lỗi nhồi chữ vào query (R03, R13, M02) | case_accuracy 0.75 (15/20) | case_accuracy 0.90 (18/20) </br>R12 còn FAIL, M05 bị regression | runs/v1_B_base_openrouter_20261110T114359725551.json |
| v2 |system_prompt.md, tools.yaml  | Làm rõ cách chọn giữa lookup và social_search, quy ước arguments, xác nhận yes_no trước khi gửi, và giữ/chuẩn hóa thông tin tài khoản qua nhiều lượt. Kỳ vọng sửa R12, M02, M03 và giữ limit ở M05. | case_accuracy=0.90 (18/20) |case_accuracy=0.95 (19/20); routing=0.95, argument=0.95, multiturn=1.0 </br>Còn lỗi R10: thiếu tên tài khoản nhưng agent đoán sama  | runs/v2_B_base_openrouter_20261110T124601179205.json  |
| v3 | system_prompt.md | Bổ sung vào system_prompt.md các rule còn thiếu của v2: hỏi lại khi yêu cầu “mới nhất” chưa rõ nguồn hoặc tài khoản (không tự đoán người), tin tức luôn qua lookup còn kết quả social chỉ là tham khảo chưa xác minh, chỉ xử lý yêu cầu mới nhất, thêm chống prompt injection và định dạng đầu ra có nguồn kèm ngày. Kỳ vọng sửa lỗi R10 còn lại của v2 và giữ các chỉ số khác không giảm. | case_accuracy 0.95 (19/20) | case_accuracy 0.90 (20/20) </br>Còn lỗi M02: Ngoài tool `look_up` còn sử dụng thêm tool `social_search` | runs/v3_B_base_openrouter_20261110T161602027725.json |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI |  |  |  |
| Tool unit tests (`tests/`) | `pytest` output |  |  |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?
