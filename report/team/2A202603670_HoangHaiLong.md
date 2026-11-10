# Báo cáo cá nhân — HoangHaiLong-2A202603670

## 1. Thông tin thành viên

- Họ tên: Hoàng Hải Long (HoangHaiLong)
- MSSV: 2A202603670
- Email: hoanghailong291@gmail.com

## 2. Phần việc phụ trách

Tôi phụ trách chạy baseline v0, thực hiện chat live với Gemini, và viết B3 (Team Eval Cases) và B4 (Live Chat Evidence) trong `REPORT.md`.

## 3. Đóng góp cụ thể

- **Baseline v0:** chạy base eval 20 case (OpenRouter, nemotron). Kết quả 15/20 đạt, `case_accuracy` 0.75, 5 case lỗi: R03, R10, R12, R13, M02. Ghi dòng v0 vào `version_log.csv`.
- **Chat live:** chạy `chat.py --provider gemini --version v3` (`gemini-3.5-flash`). Có 3 transcript, Tool đã gọi: `lookup`.
- **B4:** viết bảng 3 turn của transcript `v3_gemini_20261110T212505095343.transcript.json`.
- **B3:** viết bảng 10 case G01–G10, kết quả 10/10 đạt (run OpenRouter).

## 4. Bằng chứng

- File/commit/PR:
  - `starter_v0/runs/v0_B_base_openrouter_20261110T111752296069.json` (commit `9b3fc6c`)
  - `starter_v0/transcripts/v3_gemini_20261110T212505095343.transcript.json`
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: dùng Claude Code hỗ trợ. Tự kiểm tra bằng cách đọc lại transcript và file run.

## 5. Tự đánh giá

Hạn chế: chat live mới thử `lookup`, các phần khác chưa thử hết.