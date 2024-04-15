from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session


from src.api.database.session import get_db
from src.api.entrypoints.alunos.schema import AlunoBase, AlunoInDB
from src.api.services.aluno import ServiceAluno

router = APIRouter()


@router.post("/alunos", response_model=AlunoInDB, status_code=status.HTTP_201_CREATED)
def criar_aluno(aluno: AlunoBase, db: Session = Depends(get_db)):
    return ServiceAluno.criar_aluno(db, aluno)

@router.get("/alunos/{aluno_id}", response_model=AlunoInDB)
def get_aluno(aluno_id: int, db: Session = Depends(get_db)):
    return ServiceAluno.obter_aluno(db, aluno_id)

@router.delete("/alunos/{aluno_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_aluno(aluno_id: int, db: Session = Depends(get_db)):
    ServiceAluno.deletar_aluno(db, aluno_id)
    return {"ok": True}

@router.put("/alunos/{aluno_id}", response_model=AlunoInDB)
def atualizar_aluno(aluno_id: int, aluno: AlunoBase, db: Session = Depends(get_db)):
    return ServiceAluno.atualizar_aluno(db, aluno_id, aluno.dict())

@router.get("/alunos/cpf/{aluno_cpf}", response_model=AlunoInDB)
def get_aluno_cpf(aluno_cpf: str, db: Session = Depends(get_db)):
    return ServiceAluno.obter_aluno_por_cpf(db, aluno_cpf)

@router.get("/alunos/email/{aluno_email}", response_model=AlunoInDB)
def get_aluno_email(aluno_email: str, db: Session = Depends(get_db)):
    return ServiceAluno.obter_aluno_por_email(db, aluno_email)