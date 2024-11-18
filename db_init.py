from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Thiết lập cơ sở dữ liệu SQLite
DATABASE_URL = "sqlite:///tracker.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Định nghĩa bảng User
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    ip_address = Column(String)
    port = Column(Integer)

# Định nghĩa bảng File
class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    file_name = Column(String)
    file_path = Column(String)

# Khởi tạo cơ sở dữ liệu và các bảng
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
