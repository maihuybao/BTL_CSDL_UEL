import os
import sqlite3


def run_setup():
    # Tên file script SQL và file DB đầu ra
    sql_file_path = "Bang.sql"
    db_file_path = "data_db.sqlite"

    # 1. Kiểm tra sự tồn tại của file Bang.sql
    if not os.path.exists(sql_file_path):
        print(f"Không tìm thấy file script SQL tại đường dẫn: {sql_file_path}")
        return

    # Xóa file CSDL cũ nếu tồn tại để tạo mới hoàn toàn
    if os.path.exists(db_file_path):
        try:
            os.remove(db_file_path)
            print(f"Đã xóa file cơ sở dữ liệu cũ: {db_file_path}")
        except OSError as e:
            print(f"Không thể xóa file cơ sở dữ liệu cũ: {e}")

    print(f"Đang đọc dữ liệu từ file {sql_file_path}...")

    # 2. Đọc toàn bộ nội dung file Bang.sql
    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # 3. Chuẩn hóa một số kiểu dữ liệu của SQL Server sang SQLite để tránh lỗi cú pháp
    # - SQLite không có nvarchar(max), thay bằng TEXT
    # - Bỏ qua các ràng buộc viết gộp kiểu T-SQL 'foreign key references' ở ngang dòng
    sql_script = sql_script.replace("nvarchar(max)", "TEXT")
    sql_script = sql_script.replace("nvarchar", "TEXT")
    sql_script = sql_script.replace("varchar", "TEXT")
    sql_script = sql_script.replace("datetime", "TEXT")

    # Chuẩn hóa tiền tố N' sang ' của T-SQL để SQLite không báo lỗi
    import re
    sql_script = re.sub(r"\bN'", "'", sql_script)

    # 4. Kết nối đến SQLite và thực thi toàn bộ cấu trúc lệnh
    try:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()

        # Kích hoạt tính năng khóa ngoại
        cursor.execute("PRAGMA foreign_keys = ON;")

        print(f"Đang thiết lập bảng và nạp dữ liệu vào {db_file_path}...")
        # executescript cho phép chạy toàn bộ file SQL chứa nhiều câu lệnh ngăn cách bởi dấu ;
        cursor.executescript(sql_script)

        conn.commit()
        print(
            f"Chúc mừng! Đã khởi tạo cấu trúc và nạp dữ liệu vào file '{db_file_path}' thành công từ file gốc!"
        )

    except sqlite3.Error as e:
        print(f"Có lỗi xảy ra trong quá trình nạp SQL: {e}")

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    run_setup()