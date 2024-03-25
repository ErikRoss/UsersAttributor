from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from config import SQLALCHEMY_DATABASE_URI


engine = create_engine(SQLALCHEMY_DATABASE_URI)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    initiator = Column(String)
    service_tag = Column(String)
    panel_clid = Column(String, index=True)
    ip = Column(String, index=True)
    city = Column(String)
    user_agent_full = Column(String)
    user_agent_short = Column(String)
    os = Column(String)
    os_version = Column(String)
    browser = Column(String)
    browser_version = Column(String)
    device = Column(String)
    device_brand = Column(String)
    device_model = Column(String)
    is_mobile = Column(Boolean)
    unique_id = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def model_dump(self):
        return {
            "id": self.id,
            "initiator": self.initiator,
            "service_tag": self.service_tag,
            "panel_clid": self.panel_clid,
            "ip": self.ip,
            "city": self.city,
            "user_agent_full": self.user_agent_full,
            "user_agent_short": self.user_agent_short,
            "os": self.os,
            "os_version": self.os_version,
            "browser": self.browser,
            "browser_version": self.browser_version,
            "device": self.device,
            "device_brand": self.device_brand,
            "device_model": self.device_model,
            "is_mobile": self.is_mobile,
            "unique_id": self.unique_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


Base.metadata.create_all(bind=engine)