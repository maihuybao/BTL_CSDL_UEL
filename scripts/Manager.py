import pyodbc

SERVER = 'localhost'
DATABASE = 'tendtb'


def get_connection():
    """
    Thiết lập và trả về kết nối đến cơ sở dữ liệu SQL Server.
    Tự động phát hiện driver ODBC phù hợp trên máy tính.
    """
    available_drivers = pyodbc.drivers()
    sql_drivers = [d for d in available_drivers if 'SQL Server' in d]

    if not sql_drivers:
        raise RuntimeError(
            "Không tìm thấy driver ODBC SQL Server nào trên máy tính này. Vui lòng cài đặt SQL Server ODBC Driver.")

    # Ưu tiên Driver 18, sau đó là 17, và cuối cùng là driver SQL Server cơ bản
    preferred_driver = None
    for d in ['ODBC Driver 18 for SQL Server', 'ODBC Driver 17 for SQL Server', 'SQL Server']:
        if d in sql_drivers:
            preferred_driver = d
            break
    if not preferred_driver:
        preferred_driver = sql_drivers[0]

    conn_str = f"DRIVER={{{preferred_driver}}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"

    # Driver 18 bắt buộc phải có thêm chứng chỉ bảo mật TrustServerCertificate
    if 'Driver 18' in preferred_driver:
        conn_str += "TrustServerCertificate=yes;"

    return pyodbc.connect(conn_str)