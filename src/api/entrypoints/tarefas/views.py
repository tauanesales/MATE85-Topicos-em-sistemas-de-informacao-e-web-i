from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from fastapi import HTTPException

from src.api.database.models.professor import Professor
from src.api.database.session import get_repo
from src.api.entrypoints.tarefas.schema import TarefaAtualizada, TarefaBase, TarefaInDB, TarefaUpdate
from src.api.exceptions.credentials_exception import NaoAutorizadoException
from src.api.services.tarefa import ServiceTarefa
from src.api.services.tipo_usuario import ServicoTipoUsuarioGenerico
from src.api.utils.enums import TipoUsuarioEnum

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/", response_model=TarefaInDB, status_code=status.HTTP_201_CREATED)
async def criar_tarefa(tarefa: TarefaBase,token: str = Depends(oauth2_scheme), repository=Depends(get_repo())):
    professor: Professor = await ServicoTipoUsuarioGenerico(
        repository
    ).buscar_usuario_atual(token=token)

    if professor.usuario.tipo_usuario.titulo not in [
        TipoUsuarioEnum.COORDENADOR,
        TipoUsuarioEnum.PROFESSOR,
    ]:
        raise NaoAutorizadoException()
    
    return await ServiceTarefa(repository).criar_tarefa(tarefa)


@router.put("/{tarefa_id}", response_model=None)
async def atualizar_tarefa(
    tarefa_id: int, tarefa: TarefaAtualizada,token: str = Depends(oauth2_scheme), repository=Depends(get_repo())
):
    professor: Professor = await ServicoTipoUsuarioGenerico(
        repository
    ).buscar_usuario_atual(token=token)

    if professor.usuario.tipo_usuario.titulo not in [
        TipoUsuarioEnum.COORDENADOR,
        TipoUsuarioEnum.PROFESSOR,
    ]:
        raise NaoAutorizadoException()
    
    return await ServiceTarefa(repository).atualizar_tarefa(tarefa_id, tarefa)

@router.put("/concluir/{tarefa_id}", response_model=None)
async def concluir_tarefa(
    tarefa_id: int, 
    tarefa_update: TarefaUpdate, 
    token: str = Depends(oauth2_scheme), 
    repository=Depends(get_repo())
):
    pessoa: Professor = await ServicoTipoUsuarioGenerico(
        repository
    ).buscar_usuario_atual(token=token)
    logger.info(
        f"{pessoa.id=} | Tipo usuário atual é {pessoa.usuario.tipo_usuario.titulo}."
    )

    tarefa_service = ServiceTarefa(repository)
    tarefa = await tarefa_service.buscar_tarefa(tarefa_id)

    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa not found")

    # Permitir que alunos acessem apenas suas próprias tarefas.
    if pessoa.usuario.tipo_usuario.titulo == TipoUsuarioEnum.ALUNO:
        if pessoa.id != tarefa.aluno_id:
            raise NaoAutorizadoException(detail="Acesso negado. Alunos só podem acessar suas próprias tarefas.")
    elif pessoa.usuario.tipo_usuario.titulo not in [TipoUsuarioEnum.COORDENADOR, TipoUsuarioEnum.PROFESSOR]:
        raise NaoAutorizadoException()  # Usará a mensagem padrão "Não autorizado."
    

    # Convert Tarefa to TarefaAtualizada
    tarefa_atualizada = TarefaAtualizada(
        nome=tarefa.nome,  # You might want to adjust fields as needed
        descricao=tarefa.descricao,
        data_prazo=tarefa.data_prazo,
        aluno_id=tarefa.aluno_id,
        concluida=tarefa_update.concluida,  # Apply updates from tarefa_update
        data_conclusao=tarefa_update.data_conclusao
    )

    return await ServiceTarefa(repository).atualizar_tarefa(tarefa_id, tarefa_atualizada)



@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_tarefa(tarefa_id: int, token: str = Depends(oauth2_scheme), repository=Depends(get_repo())):
    
    professor: Professor = await ServicoTipoUsuarioGenerico(
        repository
    ).buscar_usuario_atual(token=token)

    if professor.usuario.tipo_usuario.titulo not in [
        TipoUsuarioEnum.COORDENADOR,
        TipoUsuarioEnum.PROFESSOR,
    ]:
        raise NaoAutorizadoException()
    
    await ServiceTarefa(repository).deletar_tarefa(tarefa_id)
    return {"ok": True}


@router.get("/{tarefa_id}", response_model=TarefaInDB)
async def buscar_tarefa(tarefa_id: int,token: str = Depends(oauth2_scheme), repository=Depends(get_repo())):
    professor: Professor = await ServicoTipoUsuarioGenerico(
        repository
    ).buscar_usuario_atual(token=token)

    if professor.usuario.tipo_usuario.titulo not in [
        TipoUsuarioEnum.COORDENADOR,
        TipoUsuarioEnum.PROFESSOR,
    ]:
        raise NaoAutorizadoException()
    return await ServiceTarefa(repository).buscar_tarefa(tarefa_id)

#####
@router.get("/aluno/{aluno_id}", response_model=list[TarefaInDB])
async def buscar_tarefas_por_aluno(
    aluno_id: int, token: str = Depends(oauth2_scheme), repository=Depends(get_repo())
):
    logger.info(
        f"Solicitado lista de tarefas do aluno {aluno_id=}"
        f" | Autenticando usuário atual."
    )

    pessoa: Professor = await ServicoTipoUsuarioGenerico(
        repository
    ).buscar_usuario_atual(token=token)
    logger.info(
        f"{pessoa.id=} | Tipo usuário atual é {pessoa.usuario.tipo_usuario.titulo}."
    )

    # Permitir que alunos acessem apenas suas próprias tarefas.
    if pessoa.usuario.tipo_usuario.titulo == TipoUsuarioEnum.ALUNO:
        if pessoa.id != aluno_id:
            raise NaoAutorizadoException(detail="Acesso negado. Alunos só podem acessar suas próprias tarefas.")
    elif pessoa.usuario.tipo_usuario.titulo not in [TipoUsuarioEnum.COORDENADOR, TipoUsuarioEnum.PROFESSOR]:
        raise NaoAutorizadoException()  # Usará a mensagem padrão "Não autorizado."

    return await ServiceTarefa(repository).buscar_tarefas_por_aluno(aluno_id)
