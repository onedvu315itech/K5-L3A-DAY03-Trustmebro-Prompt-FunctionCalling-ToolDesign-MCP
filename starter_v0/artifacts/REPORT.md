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

| Version of Prompt | Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|---|
| v0 | R03_web_news_routing | wrong_tool | lookup(query="AI news today artificial intelligence breakthroughs", topic=news, timeframe=day, max_results=10) | Routing đúng nhưng query nhồi thêm chữ, expected `AI` | v1 system_prompt.md: chỉ giữ query là từ khóa chủ đề chính, không thêm "news", "today", "latest" |
| v0 | R10_missing_handle | missing_info | timeline(screenname=sama, limit=5) | Thiếu tên tài khoản nhưng agent tự đoán `sama`: thiếu tool call `clarify`, thừa tool call `timeline` | v1 system_prompt.md: thiếu handle/URL/query thì gọi clarify (response_type=text), không gọi tool khác. *Lỗi này xuất hiện lại ở v2 (xem B1)* |
| v0 | R12_confirm_before_send | wrong_boundary | clarify(response_type=text, hỏi nội dung cần đăng) | Hỏi nội dung trước thay vì xác nhận: response_type expected `yes_no`, got `text` | v1: yêu cầu gửi/đăng phải clarify yes_no trước. *v1 vẫn fail* (xem B1), v2 sửa tiếp: quy tắc gửi ưu tiên hơn thiếu thông tin, ghi vào cả system_prompt.md và tools.yaml |
| v0 | R13_parallel_web_and_tweets | wrong_tool | lookup(query="AI news today", topic=news, timeframe=day, max_results=5) + social_search(query="AI artificial intelligence", search_type=Latest, limit=5) | Gọi đủ 2 tool nhưng cả hai query đều thừa chữ, expected `AI` | v1 system_prompt.md: giữ query ngắn, chỉ chủ đề chính |
| v0 | M02_carryover_timeframe | wrong_arg_value | lookup(query="robotics news today", topic=news, timeframe=day, max_results=10) | Carry đúng topic/timeframe nhưng query thừa chữ, expected `robotics` | v1: giữ query ngắn; v2: giữ và chuẩn hóa thông tin qua nhiều lượt |
| v1 | R12_confirm_before_send | wrong_boundary | clarify(response_type=text, hỏi nội dung cần đăng) | Vẫn hỏi nội dung trước thay vì xác nhận: response_type expected `yes_no`, got `text`. Không cải thiện so với v0 | v2 system_prompt.md + tools.yaml: rule gửi/đăng ưu tiên hơn thiếu thông tin, luôn clarify yes_no trước dù chưa có nội dung, rồi mới gửi với confirmed=true |
| v1 | M05_correction_limit | wrong_arg_value | timeline(screenname=elonmusk, limit=5) | Sai limit: expected 3, got 5. Handle đúng nhưng không giữ số lượng người dùng sửa ở lượt 2 (regression so với v0) | v2: tools.yaml ghi rõ giữ số lượng đã nêu ở các lượt trước, system_prompt.md ghi rõ khi người dùng sửa tài khoản thì giữ các giá trị khác như limit |
| v2 | R10_missing_handle | missing_info | timeline(screenname=sama, limit=5) | Thiếu tên tài khoản nhưng agent vẫn đoán `sama`: thiếu tool call `clarify`, thừa tool call `timeline`. R10 đã pass ở v1 nhưng fail lại ở v2 (regression) | v3 system_prompt.md: yêu cầu "mới nhất" chưa rõ nguồn/tài khoản thì clarify trước, không tự chọn người hay tài khoản, handle ngoài danh sách đã biết phải xác nhận |
| v3 | M02_carryover_timeframe | wrong_arg_value | lookup(query=robotics, topic=news, timeframe=day) + social_search(query=robotics, search_type=Latest) | Gọi thừa `social_search`: lượt cuối chỉ yêu cầu tin hôm nay về robotics nên chỉ cần `lookup`. Lỗi query ở v0 đã hết, nhưng đây là lỗi mới (regression, M02 không fail ở v1 và v2) | |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

Run: `runs/v3_B_group_openrouter_20261110T154023741619.json` (v3, suite group, 10/10 pass).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_extract_urls_deduplicates_links | Single turn: trích xuất và bỏ link trùng, không fetch link (`wrong_tool`) | `extract_urls(text=<đoạn văn>)` | PASS |
| G02_web_news_today_routing | Single turn: tin tức hôm nay dùng `topic=news`, `timeframe=day` (`wrong_arg_value`) | `lookup(query="AI", topic="news", timeframe="day")` | PASS |
| G03_missing_account_asks_user | Single turn: thiếu tài khoản thì hỏi lại, không đoán handle (`missing_info`) | `clarify(response_type="text")` | PASS |
| G04_out_of_scope_coding_request | Single turn: yêu cầu viết code Python, ngoài phạm vi (`out_of_scope`) | Không gọi tool | PASS |
| G05_multiturn_account_and_limit | Multi turn: giữ tài khoản qua các lượt và dùng limit 3 user sửa (`wrong_arg_value`) | `timeline(screenname="elonmusk", limit=3)` | PASS |
| G06_social_search_keyword | Single turn: tìm bài đăng theo từ khóa trên X, giữ query ngắn (`wrong_tool`) | `social_search(query="AI")` | PASS |
| G07_multiturn_clarify_then_fetch_url | Multi turn: hỏi link còn thiếu, rồi fetch đúng URL user đưa (`missing_info`) | `fetch(url="https://example.com/research")` | PASS |
| G08_multiturn_correct_news_timeframe | Multi turn: đổi timeframe từ tuần sang ngày, giữ chủ đề robotics (`wrong_arg_value`) | `lookup(query="robotics", topic="news", timeframe="day")` | PASS |
| G09_multiturn_switch_social_to_web | Multi turn: chuyển từ Twitter sang tin tức web, giữ chủ đề OpenAI (`wrong_tool`) | `lookup(query="OpenAI", topic="news", timeframe="day")` | PASS |
| G10_multiturn_social_search_top | Multi turn: giữ query AI, đổi `search_type` sang Top khi xin bài nổi bật (`wrong_arg_value`) | `social_search(query="AI", search_type="Top")` | PASS |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

Transcript: `transcripts/v3_gemini_20261110T212505095343.transcript.json` (gemini-3.5-flash)

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Ngày sinh của Bác Hồ là ngày bao nhiêu? | `lookup("Hồ Chí Minh")` → `lookup("ngày sinh Hồ Chí Minh")` | v3+p8dc7bad20233+t57ef62bd87f8 | answered: 19/5/1890, kèm nguồn; query đầu quá rộng nên phải gọi lại lần 2 |
| 2 | Thủ đô của nước Cộng hòa Xã hội Chủ nghĩa Việt Nam là gì? | Không gọi tool | v3+p8dc7bad20233+t57ef62bd87f8 | answered: Hà Nội; kiến thức nền nên không gọi tool là đúng |
| 3 | Dự báo thời tiết Hà Nội ngày mai là bao nhiêu độ? | `lookup("thời tiết Hà Nội", timeframe="day")` | v3+p8dc7bad20233+t57ef62bd87f8 | answered: 16–18°C đến 21–23°C, kèm nguồn và ghi rõ giả định (dữ liệu bản tin 10–11/11) |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | tests/test_tools_todo.py  | Verified Telegram message delivery after confirmation and proper error handling when required environment variables are missing. | Accidental or unauthorized messages may be sent. Require explicit user confirmation before sending and keep bot tokens and credentials private. |
| arXiv/company policy | tests/test_tools_todo.py | Verified policy search, policy-area filtering, empty queries, and separation of instruction-like content into `untrusted_text`. Added a regression test for malformed YAML documents. | Retrieved documents may contain outdated information or prompt-injection attempts. Treat retrieved content as untrusted and preserve source and effective-date metadata for verification. |
| UI | N/A | Not implemented. | N/A |
| Tool unit tests (`tests/`) | `pytest` output | Added and ran tests covering tool behavior, invalid inputs, error handling, and edge cases. Found and fixed 1 bug in `search_company_policy`: malformed YAML frontmatter previously caused the entire search to fail. Added `test_policy_skips_malformed_markdown_and_keeps_valid_results` as a regression test. Final result: **101 passed, 0 failed, 0 skipped**. | Mocked tests may not fully reflect real API behavior. Use integration tests before production deployment and maintain regression tests to prevent previously fixed bugs from returning. |

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
