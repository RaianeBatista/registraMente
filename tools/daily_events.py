from pydantic import BaseModel, Field
from typing import List
import uuid

class DailyEvents(BaseModel):
    """
    Identifica e registra eventos diários para salvar em uma planilha.
    
    Args:
        date (str): Data em que os eventos devem ser identificados, no formato YYYY-MM-DD
        events (List[Event]): Lista de eventos identificados no dia, cada um contendo título, 
            descrição e horário

    Returns:
        str: Confirmação do registro dos eventos
    """
    
    date: str = Field(
        description="Data em que os eventos ocorreram no formato DD/MM/YYYY"
    )
        
    events: List[str] = Field(
        description="Lista de eventos identificados no dia"
    )

class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID único do evento")
    title: str = Field(description="Título do evento")
    date: str = Field(description="Data do evento no formato DD/MM/YYYY")
    time: str = Field(description="Hora do evento no formato HH:MM")
    description: str = Field(description="Assunto ou descrição do evento")
    location: str = Field(description="Local do evento, se houver")