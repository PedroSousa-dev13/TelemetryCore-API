from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Sensor(Base):
    __tablename__ = "sensores"  # define o nome da tabela como sensores

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    localizacao: Mapped[str] = mapped_column(String(150), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # aqui e criada a relacao entre a tabela sensores e leituras,
    # onde cada sensor pode ter varias leituras
    leituras: Mapped[list["Leitura"]] = relationship(
        back_populates="sensor",  # atributo na classe Leitura que referencia o sensor
        cascade="all, delete-orphan",  # elimina as leituras quando o sensor e eliminado
    )


class Leitura(Base):
    __tablename__ = "leituras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sensor_id: Mapped[int] = mapped_column(
        ForeignKey("sensores.id", ondelete="CASCADE"),
        nullable=False,
    )
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    unidade: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # back_populates="leituras" define o atributo na classe Sensor
    # que referencia as leituras
    sensor: Mapped["Sensor"] = relationship(back_populates="leituras")