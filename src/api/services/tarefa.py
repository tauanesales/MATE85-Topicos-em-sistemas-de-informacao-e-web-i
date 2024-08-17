from datetime import datetime, timedelta

from loguru import logger

from src.api.database.models.aluno import Aluno
from src.api.database.models.tarefa import Tarefa
from src.api.database.repository import PGCopRepository
from src.api.entrypoints.tarefas.errors import ExcecaoTarefaNaoEncontrada
from src.api.entrypoints.tarefas.schema import TarefaAtualizada, TarefaBase, TarefaInDB
from src.api.entrypoints.tarefas_base.schema import TarefaBaseInDB
from src.api.services.servico_base import ServicoBase
from src.api.services.tarefa_base import ServiceTarefaBase


class ServiceTarefa(ServicoBase):
    _repo: PGCopRepository

    async def criar_tarefa(self, tarefa: TarefaBase) -> TarefaInDB:
        logger.info(f"{tarefa.aluno_id=} | Validando se aluno existe.")
        await self._validador.buscar_e_validar_aluno_existe(tarefa.aluno_id)
        db_tarefa = Tarefa(
            nome=tarefa.nome,
            aluno_id=tarefa.aluno_id,
            descricao=tarefa.descricao,
            data_prazo=tarefa.data_prazo,
            data_ultima_notificacao=datetime.utcnow(),
            data_conclusao=None,
        )

        await self._repo.criar(db_tarefa)
        return self.de_tarefa_para_tarefa_in_db(db_tarefa)

    async def atualizar_tarefa(
        self, tarefa_id: int, tarefa_atualizada: TarefaAtualizada
    ):
        logger.info(
            f"{tarefa_id=} {tarefa_atualizada.aluno_id=} | Iniciando atualização \
            de tarefa  Validando informações. {tarefa_atualizada.model_dump()=}"
        )
        db_tarefa: Tarefa = await self.buscar_tarefa(tarefa_id)
        to_update = tarefa_atualizada.model_dump()
        for key, value in list(to_update.items())[::-1]:
            if value is None:
                to_update.pop(key)
        await self._repo.atualizar_por_id(tarefa_id, Tarefa, **to_update)
        return self.de_tarefa_para_tarefa_in_db(db_tarefa)

    async def deletar_tarefa(self, id: int) -> None:
        tarefa: Tarefa = await self.buscar_tarefa(id)
        tarefa.deleted_at = datetime.utcnow()
        logger.info(f"{tarefa.id=} | Tarefa deletada.")

    async def buscar_tarefa(self, id: int) -> Tarefa:
        db_tarefa = await self._repo.buscar_por_id(id, Tarefa)
        if not db_tarefa:
            raise ExcecaoTarefaNaoEncontrada()
        logger.info(f"{db_tarefa.id=} | Tarefa encontrada.")
        return db_tarefa

    async def buscar_tarefas_por_aluno(self, aluno_id: int) -> list[TarefaInDB]:
        db_tarefas: list[Tarefa] = await self._repo.buscar_tarefas_por_aluno_id(
            aluno_id
        )
        logger.info(f"{aluno_id=} | Busca de tarefas pra aluno realizada.")
        return [self.de_tarefa_para_tarefa_in_db(tarefa) for tarefa in db_tarefas]

    def de_tarefa_para_tarefa_in_db(self, tarefa: Tarefa) -> TarefaInDB:
        return TarefaInDB(
            id=tarefa.id,
            aluno_id=tarefa.aluno_id,
            nome=tarefa.nome,
            data_ultima_notificacao=tarefa.data_ultima_notificacao,
            data_conclusao=tarefa.data_conclusao,
            concluida=tarefa.concluida,
            descricao=tarefa.descricao,
            data_prazo=tarefa.data_prazo,
        )

    async def criar_tarefas_para_novo_aluno(self, aluno: Aluno) -> None:
        logger.info(f"{aluno.id=} | Criando tarefas para novo aluno.")
        tarefas_base: list[TarefaBaseInDB] = await ServiceTarefaBase(
            self._repo
        ).buscar_tarefas_base_por_curso(aluno.curso.value)

        for tarefa_base in tarefas_base:
            tarefa = Tarefa(
                nome=tarefa_base.nome,
                aluno_id=aluno.id,
                descricao=tarefa_base.descricao,
                data_prazo=datetime.utcnow()
                + timedelta(days=tarefa_base.prazo_em_meses * 30),
                data_conclusao=None,
            )
            await self._repo.criar(tarefa)

        logger.info(f"{aluno.id=} | Tarefas criadas para novo aluno.")
        return None
