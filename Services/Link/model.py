import secrets
import string

from sqlalchemy.orm import Mapped, mapped_column

from Shared.BaseModel import Base
from Shared.Config import Settings

settings = Settings()


def generate_custom_id(length: int) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


class Link(Base):
    __tablename__ = 'link'

    original_url: Mapped[str] = mapped_column(nullable=False)
    short_id: Mapped[str] = mapped_column(
        nullable=False,
        unique=True,
        primary_key=True,
        default=lambda: generate_custom_id(settings.project.length_short_id)
    )
    title: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    count_redirect: Mapped[int] = mapped_column(nullable=False, default=0)
