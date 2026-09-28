# Demo Day 12 (3-5 phút)

## Chuẩn Bị

Mở https://day12-agent-production-3776.up.railway.app/ hoặc http://localhost:8000/.
Local cần Docker Desktop và `docker compose up --build -d --wait`.
Cloud nhập khóa từ `DEPLOY_API_KEY` trong `.env`; local dùng `AGENT_API_KEY`.
Không chiếu nội dung `.env` lên màn hình. UI không lưu key sau khi reload.
Đây là Mock LLM, không phải một chatbot LLM thật; chi phí được giả lập.

## Kịch Bản

1. Cho thấy FastAPI và Redis đều Online. Giải thích FastAPI xử lý request,
   Redis lưu lịch sử và các bộ đếm; Docker đóng gói, Railway chạy trên cloud.
2. Nhấn **Phiên mới**, gửi "Docker là gì?", rồi "Redis làm gì?".
   Chỉ ra lịch sử trước lượt đầu là 0, lượt sau là 2; token và chi phí có số liệu.
3. Nhấn **Kiểm tra không có khóa · 401**: request bị chặn trước khi gọi mock LLM.
4. Nhấn **Gửi 15 yêu cầu · Rate limit**: mặc định 10 lần 200, 5 lần 429.
   Bài kiểm tra dùng một user riêng nên không khóa phiên chat đang trình diễn.
5. Mở **API Docs** và tab GitHub Actions, chỉ ra test/build/deploy xanh.
   Deploy chỉ chạy sau test và build thành công, từ push vào main.

**Phiên mới** đổi User ID để bắt đầu hội thoại khác; không xóa dữ liệu Redis cũ.
UI hiển thị hội thoại vừa gửi trong tab; lịch sử phía server nằm trong Redis.
Nếu reload UI, các tin nhắn hiển thị được làm mới, không phải Redis mất dữ liệu.
Nếu gặp sự cố mạng lúc thuyết trình, dùng Docker local đã kiểm tra.

## Minh Chứng

`screenshots/demo-ui.png`: chat 2 lượt và kiểm tra rate limit qua UI thật.
`screenshots/cicd.png`: pipeline thành công.
