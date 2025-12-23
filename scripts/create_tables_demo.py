"""
Script demo: Giải thích cách tạo tables từ SQLAlchemy models

Chạy script này để xem cách SQLAlchemy tạo tables:
python scripts/create_tables_demo.py
"""

from sqlalchemy import create_engine, inspect, text
from app.core.database import Base, engine
from app.core.config import settings
from app.models import User, Transaction, Category  # Import để đăng ký models

def print_section(title):
    """In tiêu đề section"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def demo_metadata():
    """Demo: Xem metadata của models"""
    print_section("1. METADATA - Thông tin về tất cả models")
    
    print("\n📋 Các tables được đăng ký trong Base.metadata:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")
    
    print("\n📊 Chi tiết từng table:")
    for table_name, table in Base.metadata.tables.items():
        print(f"\n  Table: {table_name}")
        print(f"  Columns:")
        for column in table.columns:
            col_type = str(column.type)
            nullable = "NULL" if column.nullable else "NOT NULL"
            pk = "PRIMARY KEY" if column.primary_key else ""
            fk = f"FK -> {column.foreign_keys}" if column.foreign_keys else ""
            print(f"    - {column.name}: {col_type} {nullable} {pk} {fk}")

def demo_create_tables():
    """Demo: Tạo tables trong database"""
    print_section("2. TẠO TABLES - Base.metadata.create_all()")
    
    print("\n🔧 Đang tạo tables...")
    print("   (Chỉ tạo tables chưa tồn tại, không xóa dữ liệu)")
    
    try:
        # Tạo tất cả tables
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("   ✅ Tables đã được tạo thành công!")
    except Exception as e:
        print(f"   ❌ Lỗi: {e}")
        return False
    
    return True

def demo_inspect_tables():
    """Demo: Kiểm tra tables đã tạo"""
    print_section("3. KIỂM TRA - Tables trong database")
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📋 Tổng số tables: {len(tables)}")
        for table_name in tables:
            print(f"  ✓ {table_name}")
            
            # Xem columns của table
            columns = inspector.get_columns(table_name)
            print(f"    Columns ({len(columns)}):")
            for col in columns:
                col_type = col['type']
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f"DEFAULT {col['default']}" if col.get('default') else ""
                print(f"      - {col['name']}: {col_type} {nullable} {default}")
            
            # Xem foreign keys
            fks = inspector.get_foreign_keys(table_name)
            if fks:
                print(f"    Foreign Keys:")
                for fk in fks:
                    print(f"      - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            
            # Xem indexes
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print(f"    Indexes:")
                for idx in indexes:
                    print(f"      - {idx['name']}: {idx['column_names']}")
            
            print()
            
    except Exception as e:
        print(f"   ❌ Lỗi khi kiểm tra: {e}")

def demo_sql_statements():
    """Demo: Xem SQL statements được tạo"""
    print_section("4. SQL STATEMENTS - Câu lệnh SQL được tạo")
    
    print("\n📝 SQL để tạo table 'users':")
    from sqlalchemy.schema import CreateTable
    users_table = Base.metadata.tables['users']
    print(CreateTable(users_table).compile(engine))
    
    print("\n📝 SQL để tạo table 'transactions':")
    transactions_table = Base.metadata.tables['transactions']
    print(CreateTable(transactions_table).compile(engine))

def demo_relationships():
    """Demo: Giải thích relationships"""
    print_section("5. RELATIONSHIPS - Mối quan hệ giữa tables")
    
    print("""
    📊 Sơ đồ relationships:
    
    User (1) ────────< (N) Transaction
      │                    │
      │                    │
      │                    └───> (N) Category
      │
      └───< (N) Category
    
    Giải thích:
    - 1 User có nhiều Transactions (1:N)
    - 1 User có nhiều Categories (1:N)  
    - 1 Transaction thuộc về 1 User (N:1)
    - 1 Transaction có thể có 1 Category (N:1)
    - 1 Category có nhiều Transactions (1:N)
    """)
    
    print("\n💡 Cách sử dụng relationships trong code:")
    print("""
    # Lấy user và tất cả transactions của user
    user = db.query(User).first()
    transactions = user.transactions  # Tự động load từ relationship
    
    # Lấy transaction và user của nó
    transaction = db.query(Transaction).first()
    user = transaction.user  # Tự động load từ relationship
    
    # Lấy category và tất cả transactions
    category = db.query(Category).first()
    transactions = category.transactions
    """)

def main():
    """Hàm main"""
    print("\n" + "🚀"*30)
    print("  DEMO: TẠO TABLES TỪ SQLALCHEMY MODELS")
    print("🚀"*30)
    
    print(f"\n📌 Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'N/A'}")
    
    # 1. Xem metadata
    demo_metadata()
    
    # 2. Tạo tables
    if demo_create_tables():
        # 3. Kiểm tra tables
        demo_inspect_tables()
    
    # 4. Xem SQL statements
    demo_sql_statements()
    
    # 5. Giải thích relationships
    demo_relationships()
    
    print_section("HOÀN THÀNH")
    print("\n✅ Đã hoàn thành demo!")
    print("\n💡 Tips:")
    print("   - Xem file DATABASE_SCHEMA_GUIDE.md để hiểu chi tiết hơn")
    print("   - Sử dụng Alembic migrations cho production")
    print("   - Luôn backup database trước khi thay đổi schema")

if __name__ == "__main__":
    main()

