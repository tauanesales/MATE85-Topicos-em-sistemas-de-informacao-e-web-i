from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.database.models.base_model import BaseModel
from src.api.utils.enums import CursoAlunoEnum


class Aluno(BaseModel):
    __tablename__ = "alunos"

    cpf: Mapped[str] = mapped_column(
        String(14), nullable=False, unique=True, index=True
    )
    telefone: Mapped[str] = mapped_column(
        String(23), nullable=False, unique=True, index=True
    )
    matricula: Mapped[str] = mapped_column(
        String(20), nullable=False, unique=True, index=True
    )
    lattes: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    curso: Mapped[CursoAlunoEnum] = mapped_column(nullable=False, index=True)
    data_ingresso: Mapped[date] = mapped_column(Date(), nullable=False, index=True)
    data_qualificacao: Mapped[date] = mapped_column(Date(), nullable=True, index=True)
    data_defesa: Mapped[date] = mapped_column(Date(), nullable=True, index=True)
    tarefas: Mapped["Tarefa"] = relationship(  # noqa: F821
        "Tarefa", back_populates="aluno"
    )

    orientador_id: Mapped[int] = mapped_column(
        ForeignKey("professores.id"), nullable=True, index=True
    )
    orientador: Mapped["Professor"] = relationship(  # noqa: F821
        "Professor", back_populates="alunos"
    )
