# Financial Management API

Backend API cho ứng dụng quản lý tài chính được xây dựng với FastAPI.

## Cấu trúc Project

```
fastapi-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   ├── schemas/
│   ├── crud/
│   └── main.py
├── alembic/
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

## Cài đặt

**Lưu ý:** Project này yêu cầu Python 3.11 hoặc 3.12 (khuyến nghị 3.12). Python 3.14 có thể gặp vấn đề tương thích với một số packages.

1. Tạo virtual environment:
```bash
python3.12 -m venv venv  # Hoặc python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Copy file .env.example thành .env và cập nhật các giá trị:
```bash
cp .env.example .env
```

4. Chạy migrations (nếu có):
```bash
alembic upgrade head
```

5. Chạy server:
```bash
uvicorn app.main:app --reload
```

API sẽ chạy tại: http://localhost:8000

Documentation: http://localhost:8000/docs

## Environment Variables

- `DATABASE_URL`: Connection string cho PostgreSQL database
- `SECRET_KEY`: Secret key cho JWT tokens
- `ALGORITHM`: Algorithm cho JWT (mặc định: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Thời gian hết hạn của access token
- `DEBUG`: Chế độ debug (True/False)
- `CORS_ORIGINS`: Danh sách origins được phép CORS

