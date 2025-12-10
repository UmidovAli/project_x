from sqlalchemy import Integer, String, DateTime, BigInteger, Float, Boolean
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class User(Base):

    __tablename__ = 'excahnge_users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    balance_rub: Mapped[float] = mapped_column(Float, default=0)
    balance_usd: Mapped[float] = mapped_column(Float, default=0)
    balance_eur: Mapped[float] = mapped_column(Float, default=0)
    balance_gbp: Mapped[float] = mapped_column(Float, default=0)
    balance_cny: Mapped[float] = mapped_column(Float, default=0)
    balance_jpy: Mapped[float] = mapped_column(Float, default=0)
    balance_sgd: Mapped[float] = mapped_column(Float, default=0)
    balance_aud: Mapped[float] = mapped_column(Float, default=0)
    balance_aed: Mapped[float] = mapped_column(Float, default=0)
    balance_irn: Mapped[float] = mapped_column(Float, default=0)

