import os
import json
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

MEMORY_DIR = Path(__file__).parent.parent / "history"

class PersistentChatMemory:
    """
    Clase para manejar el historial de conversación persistente a corto plazo
    de forma estructurada, permitiendo mantener coherencia en flujos prolongados
    identificados por session_id.
    """
    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id
        self.history_file = MEMORY_DIR / f"{session_id}.json"
        self.messages = []
        self._ensure_history_dir()
        self.load_history()

    def _ensure_history_dir(self):
        """Asegura que el directorio para el historial exista."""
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    def load_history(self):
        """Carga el historial desde un archivo JSON local."""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.messages = []
                    for msg in data:
                        role = msg.get("role")
                        content = msg.get("content")
                        if role == "user":
                            self.messages.append(HumanMessage(content=content))
                        elif role == "assistant":
                            self.messages.append(AIMessage(content=content))
                        elif role == "system":
                            self.messages.append(SystemMessage(content=content))
            except Exception as e:
                print(f"[Error al cargar memoria persistente: {e}]")
                self.messages = []
        else:
            self.messages = []

    def save_history(self):
        """Guarda el historial en un archivo JSON local."""
        try:
            data = []
            for msg in self.messages:
                if isinstance(msg, HumanMessage):
                    data.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    data.append({"role": "assistant", "content": msg.content})
                elif isinstance(msg, SystemMessage):
                    data.append({"role": "system", "content": msg.content})
            
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Error al guardar memoria persistente: {e}]")

    def add_user_message(self, content: str):
        """Añade un mensaje del usuario al historial."""
        self.messages.append(HumanMessage(content=content))
        self.save_history()

    def add_assistant_message(self, content: str):
        """Añade un mensaje del asistente al historial."""
        self.messages.append(AIMessage(content=content))
        self.save_history()

    def clear(self):
        """Limpia el historial conversacional actual."""
        self.messages = []
        if self.history_file.exists():
            try:
                self.history_file.unlink()
            except Exception as e:
                print(f"[Error al borrar archivo de historial: {e}]")

    def get_messages(self):
        """Retorna la lista de objetos de mensaje compatibles con LangChain."""
        return self.messages

    def get_as_string(self) -> str:
        """Retorna el historial en formato string para depuración o prompts simples."""
        lines = []
        for msg in self.messages:
            if isinstance(msg, HumanMessage):
                lines.append(f"Cliente: {msg.content}")
            elif isinstance(msg, AIMessage):
                lines.append(f"AsesorBot: {msg.content}")
        return "\n".join(lines)
