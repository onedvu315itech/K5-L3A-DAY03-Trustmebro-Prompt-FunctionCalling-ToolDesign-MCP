# Gợi ý sửa sau v2

Rút từ log thật: `starter_v0/runs/v2_B_base_openrouter_20261110T123851923769.json`

- **Model:** `openai/gpt-4o-mini` qua OpenRouter
- **Kết quả:** **18/20 PASS**
- **Artifact version:** `v2+pa6675e5d2ac8+t3cfd8543bbae`

| Chỉ số | v2 |
|---|---:|
| case_accuracy | 0.90 |
| tool_routing_accuracy | 1.00 |
| argument_accuracy | 0.90 |
| multiturn_accuracy | 0.8333 |

> Lưu ý: các log v0/v1 trong ghi chú trước dùng model khác. Không nên kết luận điểm tăng hay giảm giữa các version chỉ từ những số liệu này; hãy so sánh các lần chạy cùng model.

## Hai case FAIL còn lại và cách sửa

### Lỗi 1. R12: hỏi xác nhận gửi nhưng dùng `text` thay vì `yes_no`

- **Mong đợi:** `clarify(response_type="yes_no")`
- **Model gửi:** `clarify(response_type="text")`
- **Vì sao sai:** model chọn đúng tool `clarify` nhưng hỏi nội dung bản tin trước, thay vì xác nhận hành động đăng.
- **Hướng sửa:** trong `artifacts/system_prompt.md`, đặt quy tắc xác nhận gửi/đăng trước quy tắc hỏi thông tin thiếu. Nói rõ phải hỏi `yes_no` trước, kể cả khi chưa có nội dung; không hỏi nội dung trước. Trong `artifacts/tools.yaml`, mô tả `clarify` phải nhấn mạnh cùng thứ tự này.

### Lỗi 2. M03: dùng handle `andrejkarpathy` thay vì `karpathy`

- **Mong đợi:** `timeline(screenname="karpathy", limit=3)`
- **Model gửi:** `timeline(screenname="andrejkarpathy", limit=3)`
- **Vì sao sai:** model chọn đúng tool và giữ đúng `limit=3`, nhưng handle không khớp quy ước của eval.
- **Hướng sửa:** trong prompt/tool description, nói rõ khi người dùng sửa tên tài khoản thì thay tài khoản cũ bằng tài khoản mới, giữ các arguments khác đã nêu, và dùng handle chuẩn không có `@`. Nếu nhóm dùng quy ước `Andrej Karpathy → karpathy`, ghi rõ ánh xạ này.

## Đã đạt trong v2

M02, lỗi trước đó về chọn `social_search` thay vì `lookup`, đã đạt ở run mới. Các case còn lại cũng đạt. Khi sửa M03, kiểm tra để quy tắc sửa tên tài khoản không làm mất `limit=3`.

## Chạy version tiếp theo

Sau khi lưu thay đổi, chạy bằng cùng model:

```powershell
python run_eval.py --version v3 --provider openrouter --model openai/gpt-4o-mini --suite base --eval-cases data/eval_base.json --system-prompt artifacts/system_prompt.md --tools artifacts/tools.yaml
```

**Kỳ vọng:** R12 và M03 đạt, đồng thời M02 và M05 vẫn đạt. Đây là mục tiêu cần kiểm tra; chỉ run mới mới xác nhận được điểm.
