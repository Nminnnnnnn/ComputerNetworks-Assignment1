from sqlalchemy.orm import Session
from db_init import SessionLocal, User, File
import bcrypt

# Hàm để lấy phiên làm việc với cơ sở dữ liệu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mã hóa mật khẩu
def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

# Xác minh mật khẩu
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Thêm người dùng mới
def add_new_user(username: str, password: str, db: Session):
    hashed_password = hash_password(password)
    user = User(username=username, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Lấy mật khẩu người dùng
def get_user_password(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user.password
    return None

# Lấy danh sách tất cả người dùng
def get_all_users(db: Session):
    return db.query(User).all()

# Tìm người dùng theo tên
def get_user_by_username(username: str, db: Session):
    return db.query(User).filter(User.username == username).first()

# Thêm file mới
def add_new_file(user_id: int, file_name: str, file_path: str, db: Session):
    file = File(user_id=user_id, file_name=file_name, file_path=file_path)
    db.add(file)
    db.commit()
    db.refresh(file)
    return file

# Lấy danh sách file của người dùng
def get_user_files(user_id: int, db: Session):
    return db.query(File).filter(File.user_id == user_id).all()

# Xóa file của người dùng
def delete_user_file(user_id: int, file_name: str, db: Session):
    file = db.query(File).filter(File.user_id == user_id, File.file_name == file_name).first()
    if file:
        db.delete(file)
        db.commit()

# Cập nhật địa chỉ IP và cổng của người dùng
def update_user_address_port(username: str, ip_address: str, port: int, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.ip_address = ip_address
        user.port = port
        db.commit()

# Lấy danh sách người dùng trực tuyến
def get_online_users(db: Session):
    return db.query(User).filter(User.ip_address.isnot(None), User.port.isnot(None)).all()

# Xóa tất cả người dùng trực tuyến (dùng khi khởi tạo lại server)
def delete_all_online_users(db: Session):
    db.query(User).update({User.ip_address: None, User.port: None})
    db.commit()
