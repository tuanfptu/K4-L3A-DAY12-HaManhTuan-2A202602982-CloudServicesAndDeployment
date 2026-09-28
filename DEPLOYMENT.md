# Thông Tin Deploy — Checkpoint 5

> Điền file này sau khi deploy xong. `pytest tests/test_cp5.py` đọc file này
> để tìm địa chỉ service của bạn và gọi thử.
>
> **Chỉ ghi TÊN biến môi trường, tuyệt đối không dán giá trị API key vào đây.**
> Repo này công khai — dán khóa vào là mất khóa.

## Thông Tin Học Viên

| Mục | Nội dung |
|-----|----------|
| Họ và tên | Hà Mạnh Tuấn |
| Mã học viên | 2A202602982 |
| Repo | https://github.com/tuanfptu/K4-L3A-DAY12-HaManhTuan-2A202602982-CloudServicesAndDeployment |

## Service

| Mục | Nội dung |
|-----|----------|
| Public URL | https://day12-agent-production-3776.up.railway.app |
| Platform | Railway |
| Ngày deploy | 2026-09-28 |

## Biến Môi Trường Đã Set Trên Cloud

Ghi tên biến và **nguồn giá trị**, không ghi giá trị:

| Biến | Đã set | Ghi chú |
|------|--------|---------|
| `PORT` | ✅ | platform tự gán |
| `AGENT_API_KEY` | ✅ | đặt trong dashboard, không nằm trong repo |
| `REDIS_URL` | ✅ | Tham chiếu `${{day12-redis.REDIS_URL}}`, kết nối nội bộ tới service day12-redis có persistent volume |
| `RATE_LIMIT_PER_MINUTE` | ✅ | 10 |
| `MONTHLY_BUDGET_USD` | ✅ | 10.0 |
| `LOG_LEVEL` | ✅ | INFO |

## Lệnh Kiểm Tra

Thay `<URL>` bằng Public URL ở trên:

```bash
# 1. Liveness — mong đợi 200 {"status":"ok"}
curl -i <URL>/health

# 2. Readiness — mong đợi 200 {"status":"ready"} (đã nối được Redis)
curl -i <URL>/ready

# 3. Không có API key — mong đợi 401
curl -i -X POST <URL>/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'

# 4. Có API key — mong đợi 200 kèm câu trả lời
curl -i -X POST <URL>/ask \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $AGENT_API_KEY" \
  -H "X-User-Id: sv-test" \
  -d '{"question":"Deploy là gì?"}'

# 5. Rate limit — gọi 15 lần, những lần cuối phải trả 429
for i in $(seq 1 15); do
  curl -s -o /dev/null -w "%{http_code} " -X POST <URL>/ask \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $AGENT_API_KEY" \
    -H "X-User-Id: sv-test" \
    -d '{"question":"test"}'
done; echo
```

## Kết Quả Chạy Thật

Dán output của các lệnh trên vào đây:

```
GET /health: 200
{"status":"ok","service":"day12-agent","version":"1.0.0"}
GET /ready: 200
{"status":"ready","redis":true}
POST /ask không có API key: 401
POST /ask có khóa cloud hợp lệ: 200, 200
history_length của hai request cùng user: 0, 2
15 request liên tiếp của một user mới:
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429
```

## Ảnh Chụp Màn Hình

Đặt ảnh trong thư mục `screenshots/`:

- `screenshots/dashboard.png` — trang quản lý service trên platform
- `screenshots/network.png` — Railway Network Logs ghi nhận `/health`, `/ready`,
  `/ask` với mã HTTP 200, 401 và 429 từ kiểm tra thật.
- Kết quả HTTP thật được ghi ở trên. Trình duyệt automation báo
  `net::ERR_BLOCKED_BY_CLIENT` khi mở `/health`; không tạo ảnh giả cho endpoint.

## Lỗi Deploy Và Cách Sửa

Railway Metal builder từ chối cache mount ở dòng cài dependency:

```text
dockerfile invalid: flag '--mount=type=cache,target=/root/.cache/pip' is missing an id argument at Line 31
```

Thêm ID thông thường vẫn không đủ vì Railway yêu cầu cacheKey prefix riêng.
Bản cuối dùng `pip install --no-cache-dir --timeout 120 --retries 5` để Dockerfile
chạy được trên cả local và Railway. Deployment sau đó Online và vượt kiểm tra HTTPS.
Tham chiếu Redis ban đầu dùng `DATABASE_URL`, nhưng service Redis cấp `REDIS_URL`;
đã sửa tham chiếu về tên biến thực tế của `day12-redis`.

---

## Nếu Dùng Phương Án Dự Phòng

Không đăng ký được tài khoản cloud? Vẫn nộp được bài, nhưng CP5 tối đa 60% điểm:

1. Đặt `LOCAL_FALLBACK=true` trong `.env`
2. Chạy `docker compose up -d` rồi kiểm tra `docker compose ps`
3. Chụp màn hình vào `screenshots/`
4. Chạy `pytest tests/test_cp5.py -v` — bộ test sẽ tự chuyển sang kiểm tra
   `http://localhost:8000`
5. Ghi rõ lý do không deploy được vào phần dưới đây:

```
Không sử dụng phương án dự phòng: LOCAL_FALLBACK=false.
Service triển khai cloud thật bằng credit trial hiện có; chưa nâng cấp gói trả phí.
Theo dõi credit và thời hạn trial để URL còn hoạt động lúc chấm bài.
```
