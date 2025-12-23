# Hướng dẫn Setup Project

## Bước 1: Tạo Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

## Bước 2: Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

## Bước 3: Tạo file .env

Tạo file `.env` trong thư mục root với nội dung:

```env
# Database
DATABASE_URL=postgresql://postgres:tpkTj18500n!!@db.cxfnelcihtotonjedadk.supabase.co:5432/postgres

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=Financial Management API
APP_VERSION=1.0.0
DEBUG=True

# CORS (comma-separated or JSON array format)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
# Hoặc có thể dùng format JSON: CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

**Lưu ý:** Thay đổi `SECRET_KEY` thành một giá trị ngẫu nhiên và bảo mật trong production!

## Bước 4: Chạy Database Migrations (Tùy chọn)

Nếu bạn muốn sử dụng Alembic để quản lý migrations:

```bash
# Tạo migration đầu tiên
alembic revision --autogenerate -m "Initial migration"

# Chạy migrations
alembic upgrade head
```

Hoặc nếu bạn muốn tạo tables trực tiếp (đã có trong code), chỉ cần chạy server.

## Bước 5: Chạy Server

```bash
uvicorn app.main:app --reload
```

Server sẽ chạy tại: http://localhost:8000

## Bước 6: Kiểm tra API

- API Documentation (Swagger): http://localhost:8000/docs
- API Documentation (ReDoc): http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Các Endpoints Chính

### Authentication
- `POST /api/v1/auth/login` - Đăng nhập
- `GET /api/v1/auth/me` - Lấy thông tin user hiện tại

### Users
- `POST /api/v1/users/` - Tạo user mới
- `GET /api/v1/users/` - Lấy danh sách users
- `GET /api/v1/users/{user_id}` - Lấy thông tin user
- `PUT /api/v1/users/{user_id}` - Cập nhật user
- `DELETE /api/v1/users/{user_id}` - Xóa user

### Transactions
- `POST /api/v1/transactions/` - Tạo transaction mới
- `GET /api/v1/transactions/` - Lấy danh sách transactions (có filters)
- `GET /api/v1/transactions/{transaction_id}` - Lấy thông tin transaction
- `PUT /api/v1/transactions/{transaction_id}` - Cập nhật transaction
- `DELETE /api/v1/transactions/{transaction_id}` - Xóa transaction

### Categories
- `POST /api/v1/categories/` - Tạo category mới
- `GET /api/v1/categories/` - Lấy danh sách categories
- `GET /api/v1/categories/{category_id}` - Lấy thông tin category
- `PUT /api/v1/categories/{category_id}` - Cập nhật category
- `DELETE /api/v1/categories/{category_id}` - Xóa category

## Testing API

### 1. Tạo User mới
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

### 2. Đăng nhập
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"
```

### 3. Sử dụng token để truy cập API
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Cấu trúc Project

```
fastapi-backend/
├── app/
│   ├── api/              # API routes
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/             # Core configuration
│   ├── crud/             # CRUD operations
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   └── main.py          # Application entry point
├── alembic/              # Database migrations
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── README.md
```

## Troubleshooting

### Lỗi kết nối database
- Kiểm tra `DATABASE_URL` trong file `.env`
- Đảm bảo database đã được tạo và có thể truy cập

### Lỗi import modules
- Đảm bảo bạn đang chạy từ thư mục root của project
- Kiểm tra virtual environment đã được activate

### Lỗi CORS
- Thêm origin của frontend vào `CORS_ORIGINS` trong file `.env`

