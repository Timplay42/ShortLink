import uuid

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from Shared.BaseModel import Base
from Shared.Config import Settings

setting = Settings()

class Post(Base):
    __tablename__ = "post"

    id: Mapped[uuid.UUID] = mapped_column(nullable=False, default=uuid.uuid4, primary_key=True)
    title: Mapped[str] = mapped_column(String(setting.project.length_title), nullable=False)
    description: Mapped[str] = mapped_column(String(setting.project.length_description), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)


