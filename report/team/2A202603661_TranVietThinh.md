# Báo cáo cá nhân — HoVaTen-MSSV

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Trần Việt Thịnh  
- MSSV: 2A202603661 
- Email: 26ai.thinhtv@vinuni.edu.vn

## 2. Phần việc phụ trách

Phụ trách tối ưu agent ở v1, ghi log vào version viết unit test cho tool mới, tìm ra bug có sẵn và sửa với bằng chứng

## 3. Đóng góp cụ thể

phụ trách version v1. Sau khi đối chiếu từng chỉ dẫn trong system_prompt.md của starter với từng case lỗi, mình xác định gốc rễ là các chỉ dẫn xấu cố ý (không hỏi lại mà đoán, gửi ngay không cần xác nhận, ép một bước), rồi viết lại prompt với rule routing, hỏi lại khi thiếu thông tin, xác nhận trước khi gửi, out-of-scope và gọi song song. Viết unit test cho tool rồi giữ pytest xanh, phát hiện ra tool có sẵn, ghi lại bug, đã sửa và test lại thành công

## 4. Bằng chứng

- File/commit/PR: https://github.com/onedvu315itech/K5-L3A-DAY03-Trustmebro-Prompt-FunctionCalling-ToolDesign-MCP/commit/19824fd1bb83c18aa2b3e2dc0f3426ec7b910e2f
 https://github.com/onedvu315itech/K5-L3A-DAY03-Trustmebro-Prompt-FunctionCalling-ToolDesign-MCP/commit/add49575c6837ca40dca382110051c187c29df84
 https://github.com/onedvu315itech/K5-L3A-DAY03-Trustmebro-Prompt-FunctionCalling-ToolDesign-MCP/commit/c9b8338ab0ddf08bb1bc75b62d0fd6d678d1049b#diff-774a51ad5da984d76607b29375b1ab9add8a9af0a007324f5494915594796901
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: Dùng Claude để sửa bug, sau đó đọc lại kết quả đó, tự test và nhận được pytest xanh

## 5. Tự đánh giá
Làm theo vòng lặp có bằng chứng: chạy, đọc log chi tiết, tìm nguyên nhân, sửa, chạy lại. Hầu hết kết luận đều dựa vào file run chứ không đoán.
Mỗi version đều ghi hypothesis và metric trước/sau, kiểm tra regression sau mỗi lần sửa.
Phát hiện và ghi nhận lỗi của chính mình (M05 do rule optional args), không chỉ báo số liệu đẹp.