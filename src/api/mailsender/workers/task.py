from datetime import datetime, timedelta
from sqlalchemy import select, join, update
from typing import Callable, Optional

from src.api.database.models.aluno import Aluno
from src.api.database.models.tarefa import Tarefa
from src.api.mailsender.workers import MailerWorker
from src.api.database.session import session

import asyncio


class TaskMailerWorker(MailerWorker):
    """
    Classe responsável por notificar por email 
    os usuários sobre tarefas perto do prazo.
    """

    def __get_tasks_near_to_deadline(self):
        """
        Retorna as tarefas pendentes, próximas ao prazo de entrega.
        """
        deadline = datetime.now() + timedelta(days=30)  # Expires in 1 month
            
        query = (
            select([
                Aluno.c.id, 
                Aluno.c.nome, 
                Aluno.c.email, 
                Tarefa.c.id.label("tarefa_id"), 
                Tarefa.c.data_prazo, 
                Tarefa.c.nome.label("titulo")
            ])
            .select_from(
                join(Aluno, Tarefa, Aluno.id == Tarefa.aluno_id)
            )
            .where(Tarefa.data_prazo <= deadline.date())
            .where(Tarefa.last_notified.is_(None))
        )
        result = session.execute(query)

        return result.scalars().all()
    
    async def start(self, stop_function: Optional[Callable] = None):
        while stop_function is None or not stop_function():
            for task in self.__get_tasks_near_to_deadline():
                # TODO: Definir o corpo do email e o título
                subject = f"[AVISO PGCOP] - Tarefa Pendente"
                body = f"Olá {task.nome}! Estou passando aqui para notificá-lo que a tarefa {task.titulo} está ainda pendente."
                
                self.send_message(task.email, subject, body)

                query = update(Tarefa).where(Tarefa.id == task.tarefa_id).values(last_notified=datetime.now())
                session.execute(query)

            await asyncio.sleep(60 * 60)