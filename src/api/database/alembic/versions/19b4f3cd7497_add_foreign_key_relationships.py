"""add foreign key relationships

Revision ID: 19b4f3cd7497
Revises: 28c8fa6ab154
Create Date: 2024-06-16 01:33:07.636508

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "19b4f3cd7497"
down_revision: Union[str, None] = "28c8fa6ab154"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, "alunos", "professores", ["orientador_id"], ["id"])
    op.create_foreign_key(None, "tarefas", "alunos", ["aluno_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "tarefas", type_="foreignkey")
    op.drop_constraint(None, "alunos", type_="foreignkey")
    # ### end Alembic commands ###
