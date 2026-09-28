# Phiếu Phản Ánh — K4 Level 3A, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Nội dung dưới đây là bản nháp dựa trên kiểm chứng thực tế và giải thích kỹ thuật.
> Học viên cần đọc, kiểm tra và diễn đạt lại bằng lời của mình trước khi nộp.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Hà Mạnh Tuấn. Mã học viên: 2A202602982.

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

Nếu quên đặt AGENT_API_KEY trên Railway, ứng dụng phải dừng khởi động thay vì
phục vụ bằng một khóa mặc định dễ đoán. Test thiếu khóa đã xác nhận Settings
ném ValidationError. Lifespan gọi get_settings() để kiểm tra cấu hình lúc startup.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

Log thu được từ container agent ngày 2026-09-28:

```json
{"user_id":"reflection-log","tokens_in":3,"tokens_out":41,"cost_usd":2.505e-05,"event":"ask_completed","level":"info","timestamp":"2026-09-28T08:45:41.376998+00:00"}
```

Có thể lọc các request theo user_id và cộng cost_usd theo tháng; cũng có thể
thống kê token và số sự kiện ask_completed theo thời gian. Một dòng thông báo
chung không có các trường để đối chiếu tự động như vậy.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | Chưa có số đo thực tế |
| Multi-stage | 309 MB, đo bằng docker images day12-agent:cp2-test |

Giải thích: phần dung lượng chênh lệch đó là những gì?

Đã build và đo image multi-stage, nhưng chưa build bản đầu dùng python:3.11
đầy đủ, nên chưa thể báo chênh lệch MB thực tế. Không lấy số ước lượng làm số đo.
Về nguyên lý, base slim loại bớt nhiều package hệ điều hành so với base đầy đủ;
multi-stage chỉ mang venv và source cần thiết sang runtime. Multi-stage không
tự động làm image nhỏ hơn nếu builder không có công cụ hoặc artifact dư.
Đây là thí nghiệm còn cần bổ sung trước khi nộp bản phản ánh hoàn chỉnh.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

Trong lần build lại sau timeout tải dependency, log Docker hiện CACHED cho
WORKDIR, tạo venv và COPY requirements.txt. Với sửa source Python, layer
COPY app và các layer runtime phía sau bị mất cache; phần cài dependency của
builder vẫn có thể dùng lại vì requirements.txt không đổi. Nếu COPY toàn bộ
source trước pip install thì đổi code sẽ làm pip install chạy lại.
Chưa thực hiện riêng thí nghiệm sửa đúng một ký tự rồi đo thời gian build.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

Lỗ hổng cho phép chạy lệnh tùy ý trước hết cho kẻ tấn công quyền của process
trong container. Nếu process là root, kẻ tấn công có thể sửa nhiều file hơn và
lợi dụng bind mount nhạy cảm hoặc lỗ hổng container runtime/kernel để gây hại
trên host. Root trong container không tự động đồng nghĩa root trên host.
USER appuser giảm quyền ở bước thực thi lệnh trong container, nhưng không thay
thế việc cập nhật hệ thống và giới hạn mount. Lệnh id thật trả uid=999(appuser).

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

Có thể gửi 20 request: 10 request ở giây 59 của phút trước và 10 request ở
giây 00 của phút sau. Bộ đếm reset theo phút cho qua cả hai nhóm. Sliding
window nhìn lại 60 giây nên nhóm thứ hai vẫn bị tính cùng nhóm thứ nhất;
Redis ZSET lưu timestamp và member UUID để không gộp request trùng thời điểm.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

Rate limit giới hạn tần suất trong 60 giây, cost guard giới hạn tổng tiền
trong tháng. Người dùng mới gửi một request nhưng đã hết ngân sách tháng sẽ
qua rate limit và bị cost guard chặn 402. Người dùng còn ngân sách nhưng gửi
request thứ 11 trong cửa sổ 60 giây bị rate limit chặn 429. Kiểm tra cloud thật
với user mới cho kết quả 10 lần 200 rồi 5 lần 429; chi phí LLM trong lab là mock.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

Nếu liveness cũng phụ thuộc Redis, Redis mất kết nối làm cả ba probe thất bại;
sau ngưỡng retry, orchestrator có thể restart cả ba container. Redis vẫn lỗi
thì container mới tiếp tục thất bại, tạo vòng restart và làm gián đoạn request.
Tách /health giúp báo process còn sống; /ready trả 503 để báo không sẵn sàng.
Việc ngừng gửi traffic phụ thuộc platform có sử dụng readiness hay không;
Docker HEALTHCHECK tự nó không restart container và Railway ở lab cấu hình
/health cho kiểm tra deployment, không phải một Kubernetes readiness probe.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

Kiểm tra trên local và cloud với cùng user cho history_length lần lượt 0 và 2.
Test CP4 kiểm tra các store dùng chung Redis nhìn thấy cùng lịch sử. Redis lưu
dữ liệu ngoài process nên đổi replica vẫn đọc được lịch sử; dict riêng trong
mỗi replica sẽ tạo ba lịch sử riêng, con số phụ thuộc request vào replica nào.
Chưa chạy ba replica thật: Compose hiện map cố định 8000:8000 nên lệnh scale
trong câu hỏi sẽ xung đột cổng. Cần override ports hoặc đặt reverse proxy trước
khi thực hiện thí nghiệm này; không coi test store là bằng chứng đã scale thật.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

Lần deploy Railway thất bại với thông báo:

```text
dockerfile invalid: flag '--mount=type=cache,target=/root/.cache/pip' is missing an id argument at Line 31
```

Build logs chỉ ra dòng pip install có cache mount. Thêm id=day12-pip vẫn bị
từ chối do thiếu cacheKey prefix của Railway. Bản cuối bỏ cache mount và dùng
pip install --no-cache-dir --timeout 120 --retries 5. Railway build thành công,
service Online; /health và /ready trả 200, request thiếu khóa trả 401.
Redis reference cũng được sửa từ DATABASE_URL sang biến REDIS_URL thực tế.
