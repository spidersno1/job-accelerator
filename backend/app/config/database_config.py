from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DatabaseConfig:
    URL = "sqlite:///./job_accelerator.db"
    CONNECT_ARGS = {"check_same_thread": False}
    POOL_RECYCLE = 3600  # 每小时回收连接

engine = create_engine(
    DatabaseConfig.URL,
    connect_args=DatabaseConfig.CONNECT_ARGS,
    pool_recycle=DatabaseConfig.POOL_RECYCLE
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
