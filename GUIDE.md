# Hướng dẫn thực hiện Lab: Research Agent (v0 → v1 → v2 → v3)

Mọi lệnh chạy trong thư mục `starter_v0/`. Chi tiết đề bài xem [README.md](README.md) và [TOOL-SETUP.md](TOOL-SETUP.md).

## Khái niệm cần nắm

Agent gồm 3 phần:

| Phần | File | Vai trò |
|---|---|---|
| Luật hành xử | `artifacts/system_prompt.md` | Dặn model cách quyết định |
| Khai báo tool | `artifacts/tools.yaml` | Model đọc để biết có tool gì, khi nào dùng, args ra sao |
| Code tool | `tools/<tên>/tool.py` | Chạy thật (gọi API, ...) |

Eval chấm **chọn đúng tool + đúng args** dựa trên log thật, không chấm văn phong câu trả lời.

Một tool có mặt ở 4 nơi, **tên phải khớp nhau**:

1. `tools/<tên>/tool.py`: code
2. `tools/<tên>/TOOL.md`: metadata (frontmatter)
3. `tools/__init__.py`: đăng ký trong `TOOL_FUNCTIONS`
4. `artifacts/tools.yaml`: khai báo cho model

---

## Phần 1. Dựng v0

### 1.1 Setup
```bash
cd starter_v0
python -m venv .venv
.venv\Scripts\activate          # Windows (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env            # nếu chưa có .env
```
Điền `.env` (tuyệt đối **không commit** `.env`):
```
OPENROUTER_API_KEY=...
TAVILY_API_KEY=...        # lookup
FIRECRAWL_API_KEY=...     # fetch
RAPIDAPI_KEY=...          # timeline, social_search
RAPIDAPI_TWITTER_HOST=twitter-api45.p.rapidapi.com
```
Kiểm tra provider:
```bash
python scripts/preflight_provider.py --provider openrouter
```

### 1.2 Tool đầu tiên: `lookup`
1. Lấy `TAVILY_API_KEY` (xem TOOL-SETUP.md mục 2).
2. Chạy thử:
   ```bash
   python -c "from tools import TOOL_FUNCTIONS as T; print(T['lookup']('AI', max_results=1)['items'][0]['title'])"
   ```
3. Kiểm tra `lookup` đã được khai báo trong `artifacts/tools.yaml` và đăng ký trong `tools/__init__.py`.

### 1.3 Mở rộng đủ tool core
Lần lượt thêm key và chạy thử từng tool (lệnh test ở TOOL-SETUP.md):

| Tool | Làm gì | Key cần |
|---|---|---|
| `clarify` | Hỏi lại user | không |
| `timeline` | Bài đăng gần đây của 1 tài khoản | `RAPIDAPI_KEY` |
| `social_search` | Tìm bài đăng theo từ khoá | `RAPIDAPI_KEY` |
| `lookup` | Tìm web (general/news) | `TAVILY_API_KEY` |
| `fetch` | Đọc nội dung 1 URL | `FIRECRAWL_API_KEY` |
| `format` | Đóng gói thành markdown digest | không |

v0 giữ nguyên prompt và khai báo mặc định của starter. Prompt v0 **cố tình viết xấu** (đoán thay vì hỏi, gửi không cần xác nhận, ép một bước) để có lỗi mà phân tích.

### 1.4 Kiểm tra test nền
```bash
pytest
```
Contract test và example test phải xanh, test TODO đang `skipped` là bình thường.

### 1.5 Chạy baseline v0
```bash
python run_eval.py --provider openrouter --model nvidia/nemotron-3-ultra-550b-a55b:free --version v0 --suite base --eval-cases data/eval_base.json
```
Model mặc định của starter (`openai/gpt-4o-mini`) là bản trả phí. Nhóm dùng model free ở trên, nên **mọi version phải dùng cùng `--model`** để so sánh được.
Kết quả lưu ở `runs/v0_B_base_openrouter_<timestamp>.json` (xem mục "Run JSON sinh ra ở đâu" bên dưới).

### 1.6 Phân tích lỗi v0
Mở file run JSON vừa sinh và xem:
- `summary`: `case_accuracy`, `tool_routing_accuracy`, `argument_accuracy`, `multiturn_accuracy`
- `results[*].result.failures`, `results[*].result.observed_mismatch`
- Tool call thực tế và kết quả tool trong `results[*]`

Gán mỗi case FAIL một loại lỗi: `wrong_tool`, `wrong_arg_value`, `wrong_boundary`, `unnecessary_tool`, `out_of_scope`, `missing_info`.

Tuỳ chọn, xuất bảng phẳng để đếm lỗi:
```bash
python scripts/parse_runs.py runs/ --output analysis/base_runs.csv
```

### 1.7 Ghi v0 vào version log
Thêm một dòng vào `artifacts/version_log.csv` (cột: `version,author,changed_artifact,artifact_version,prompt_hash,tools_hash,reason,hypothesis,metric_before,metric_after,run_file`). `artifact_version`, hash và đường dẫn run lấy từ output của lệnh chạy. Ví dụ định dạng: `samples/version_log.example.csv`.

---

## Phần 2. Từ v0 lên v1 (và v2, v3)

Mỗi version lặp lại cùng một chu trình, **chỉ đổi một giả thuyết mỗi lần**.

### 2.1 Chu trình
1. **Đọc log** của version trước, gom các case FAIL theo loại lỗi.
2. **Đặt một giả thuyết** cho nguyên nhân phổ biến nhất. Ví dụ: "Model đoán thay vì hỏi lại vì prompt bảo nó đoán."
3. **Sửa một thứ** trong đúng 2 file:

   | File | Có thể sửa |
   |---|---|
   | `artifacts/system_prompt.md` | Bỏ chỉ dẫn xấu; thêm rule routing (khi nào `timeline` / `social_search` / `lookup` / `fetch` / `clarify`) |
   | `artifacts/tools.yaml` | Viết lại `description` (làm gì, khi nào dùng, khi nào không dùng); nêu rõ quy ước args: handle không có `@`, `topic=news` cho tin tức, `timeframe`, `search_type=Top\|Latest`; `send` chỉ gửi khi `confirmed=true` |

   **Không sửa** nội dung case trong `data/eval_base.json`.
4. **Chạy lại** với version mới:
   ```bash
   python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
   ```
5. **So metric** trước/sau. Không cải thiện thì đổi giả thuyết, nhưng vẫn ghi lại kết quả.
6. **Ghi một dòng** vào `artifacts/version_log.csv`.
7. **Kiểm tra đồng bộ**:
   ```bash
   pytest tests/test_tool_contract.py
   ```

### 2.2 Gợi ý giả thuyết theo thứ tự
- **v1**: Bỏ các chỉ dẫn xấu trong prompt (đoán, gửi không xác nhận, ép một bước) và thêm rule dùng `clarify`.
- **v2**: Viết lại description các tool cùng quy ước args (handle, topic, timeframe, search_type).
- **v3**: Xử lý các case biên còn lại (ví dụ `send` cần xác nhận, câu ngoài phạm vi, không cần tool).

Đây chỉ là gợi ý, giả thuyết thật phải dựa trên lỗi trong log của nhóm.

---

## Phần 3. Các bước tiếp theo sau v3

1. **Tool mới** (≥ 1): tạo `tools/<tên>/tool.py` + `TOOL.md`, đăng ký trong `tools/__init__.py` và `tools.yaml`.
2. **Unit test** cho tool mới (≥ 3 test) trong `tests/test_tools_todo.py`. Mẫu ở `tests/test_tools_examples.py`; HTTP phải mock bằng `fake_http`. Mục tiêu `pytest`: 0 failed, 0 skipped.
3. **Eval của nhóm**: thêm 10 case (5 single turn, 5 multi turn) vào `data/eval_group.json`, rồi chạy:
   ```bash
   python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
   ```
4. **Chat live** (≥ 3 lượt): `python chat.py --provider openrouter --version v3`. Transcript lưu ở `transcripts/*.transcript.json`.
5. **UI** Streamlit hoặc Vercel; chia sẻ nhanh bằng `cloudflared tunnel --url http://localhost:8501`.
6. **Report**: `artifacts/REPORT.md` (Phần A trước 16:30, Phần B để nộp).

---

## Run JSON sinh ra ở đâu

Thư mục `runs/` **không có sẵn** trong repo. Nó được tạo tự động khi chạy `run_eval.py`:

- Thư mục mặc định `runs/` (tham số `--runs-dir`), tạo bằng `mkdir` tại `run_eval.py:326`.
- Tên file ghép từ `version`, `phase`, `suite`, `provider` và timestamp (`run_eval.py:330-336`), ví dụ `v0_B_base_openrouter_20261110T153000123456.json`.
- File được ghi tại `run_eval.py:354-355`.

Mỗi lần chạy sinh một file mới, không ghi đè. Ví dụ phân tích mẫu: `samples/run-analysis.csv`.

## Nộp bài

Commit: `artifacts/*`, `data/eval_group.json`, `tests/`, `runs/*.json`, `analysis/*.csv`, `transcripts/*.transcript.json` và code đã thêm hoặc sửa.
**Không commit** `.env` hoặc API key.
