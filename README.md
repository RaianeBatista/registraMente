# 🧠 RegistraMente - Agente de Memória

## 📋 Sobre o Projeto

O **RegistraMente** é um assistente inteligente que funciona como seu "assistente virtual", capaz de:

- 🎤 Gravar áudio através do microfone
- 📝 Transcrever sua fala usando IA (Whisper da OpenAI)
- 🤖 Processar e registrar os eventos descritos no áudio usando GPT-4
- 💾 Salvar tudo em uma memória persistente para consultas futuras

Este projeto é uma excelente introdução para **iniciantes em Python e IA** que desejam entender como integrar diferentes tecnologias de inteligência artificial.

## 🚀 Tecnologias Utilizadas

- **Python 3.11+**: Linguagem principal de desenvolvimento.
- **OpenAI API**: Utilizada para transcrição de áudio (Whisper) e processamento de linguagem natural (GPT-4).
- **PyAudio**: Biblioteca para gravação de áudio do microfone.
- **Pydantic**: Usada para validação e estruturação de dados.
- **Python-dotenv**: Para gerenciamento seguro de variáveis de ambiente.
- **Firebase Admin SDK**: Para interação com o Firebase para armazenamento de dados (inferido do nome do arquivo `firebase_credentials.json`).
- **LangChain**: Framework Python para desenvolver aplicações com modelos de linguagem. (inferido do `requirements.txt` e uso comum em projetos de agentes de IA)

## 📁 Estrutura do Projeto

```
.
├── agent_service.py              # Serviço principal do agente
├── app.py                        # Aplicação principal ou interface (se houver)
├── firebase_credentials.json     # Credenciais para acesso ao Firebase
├── main.py                       # Script principal para execução do agente
├── requirements.txt              # Dependências do projeto
├── stackspot_agent.py            # Componente relacionado ao Stackspot (se aplicável)
├── tools/                        # Ferramentas e modelos de dados para o agente
│   └── daily_events.py           # Modelo Pydantic para eventos diários
├── utils/                        # Utilitários e funções auxiliares
│   ├── basemodel2tool.py         # Conversor de modelos Pydantic para ferramentas da OpenAI
│   └── record_audio.py           # Função para gravar áudio
└── .env                          # Variáveis de ambiente (excluído pelo .gitignore)
└── README.md                     # Este arquivo
```

## ⚙️ Configuração do Ambiente

Siga os passos abaixo para configurar e executar o projeto:

### 1. Clone o repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd agent-memory
```

### 2. Crie e ative o ambiente virtual

É recomendável usar um ambiente virtual para gerenciar as dependências do projeto.

```bash
# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No macOS/Linux:
source venv/bin/activate
# No Windows:
venv\Scripts\activate
```

### 3. Instale as dependências

Com o ambiente virtual ativado, instale as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

### 4. Configure a API Key da OpenAI e Credenciais Firebase

1.  **OpenAI API Key**:

    - Crie uma conta na [OpenAI](https://platform.openai.com/).
    - Gere uma API Key no painel de controle.
    - Crie um arquivo `.env` na raiz do projeto (`agent-memory/`).
    - Adicione sua API Key no arquivo `.env`:
      ```
      OPENAI_API_KEY=sua_chave_api_aqui
      ```
    - ⚠️ **Importante**: Nunca compartilhe sua API Key! O arquivo `.env` já está no `.gitignore` para protegê-la.

2.  **Firebase Credentials**:
    - Obtenha o arquivo `firebase_credentials.json` do seu projeto Firebase.
    - Coloque este arquivo na raiz do projeto (`agent-memory/`). Este arquivo é essencial para a memória persistente do agente.

## 🎯 Como Usar

### 1. Execute o programa

Navegue até o diretório principal do projeto e execute o script `main.py`:

```bash
python main.py
```

### 2. Interaja com o agente

1.  **Fale sobre seu dia**: O programa começará a gravar automaticamente.
2.  **Conte eventos**: Por exemplo: "Hoje de manhã fui ao médico e à tarde tive uma reunião importante".
3.  **Aguarde o processamento**: O agente irá transcrever sua fala e processar os eventos usando IA.
4.  **Veja o resultado**: Os eventos serão salvos na memória persistente e uma confirmação será exibida.

### 3. Exemplo de interação

```
🎤 Gravando... (Fale sobre seus eventos do dia)

Você: "Hoje de manhã às 9h fui ao dentista, e à tarde às 15h tive uma reunião com o cliente João"

🤖 Agente: "Evento do dia 15/01/2024 registrado com sucesso, posso te ajudar com mais alguma coisa?"
```

## 📊 Como Funciona Internamente

### Fluxo do Programa

```mermaid
graph TD
    A[Início] --> B[Gravar Áudio]
    B --> C[Transcrever com Whisper]
    C --> D[Processar com GPT-4]
    D --> E[Identificar Eventos]
    E --> F[Salvar na Memória (Firebase)]
    F --> G[Exibir Confirmação]
    G --> B
```

### Componentes Principais

1.  **`record_audio.py`**: Gerencia a gravação de áudio do microfone e salva como arquivo WAV.
2.  **`main.py`**: O loop principal que orquestra todo o processo, desde a gravação até o armazenamento dos eventos.
3.  **`daily_events.py`**: Define o modelo de dados Pydantic para a estruturação de eventos diários.
4.  **Firebase**: Usado como a memória persistente onde todos os eventos e interações são salvos.

## 🔧 Personalização

### Adicionando novos tipos de eventos

1.  Crie um novo modelo Pydantic no diretório `tools/`:

    ```python
    from pydantic import BaseModel, Field
    from typing import List

    class TaskEvents(BaseModel):
        """Registra tarefas e compromissos"""
        date: str = Field(description="Data da tarefa")
        tasks: List[str] = Field(description="Lista de tarefas")
    ```

2.  Importe e adicione o novo modelo à lista de ferramentas no `main.py`.

### Mudando o idioma

Para alterar o idioma de transcrição e processamento, ajuste a configuração de idioma no `main.py` (por exemplo, para inglês):

```python
language="en"  # Linha da transcrição
```

## ❌ Solução de Problemas

### Erro de permissão do microfone

- **macOS**: Vá em Configurações do Sistema > Privacidade e Segurança > Microfone e permita o acesso para o Terminal ou a aplicação Python.
- **Windows**: Vá em Configurações > Privacidade > Microfone e permita o acesso de aplicativos ao microfone.

### Erro de instalação do PyAudio

- **macOS (usando Homebrew)**:

  ```bash
  brew install portaudio
  pip install pyaudio
  ```

- **Ubuntu/Debian**:

  ```bash
  sudo apt-get install portaudio19-dev
  pip install pyaudio
  ```

### API Key inválida ou problemas com Firebase

- Verifique se a `OPENAI_API_KEY` está correta no arquivo `.env`.
- Confirme se você tem créditos válidos na sua conta OpenAI.
- Assegure-se de que o arquivo `firebase_credentials.json` está na raiz do projeto e é válido.

## 📚 Próximos Passos

Explore e aprimore o projeto com as seguintes ideias:

1.  **Adicionar interface gráfica**: Desenvolva uma interface de usuário com bibliotecas como Tkinter, PyQt ou Streamlit.
2.  **Integrar com calendário**: Conecte o agente a serviços de calendário (como Google Calendar API) para gerenciar eventos.
3.  **Adicionar busca avançada**: Implemente funcionalidades de busca por eventos usando filtros de data, palavras-chave ou categorias.
4.  **Classificação automática de eventos**: Utilize modelos de IA para classificar eventos em categorias predefinidas.
5.  **Geração de relatórios**: Crie relatórios semanais ou mensais dos eventos registrados.
6.  **Lembretes automáticos**: Implemente um sistema de lembretes para eventos futuros.

## 🤝 Contribuição

Este é um projeto educacional e a contribuição é bem-vinda! Sinta-se à vontade para:

- Fazer fork do projeto.
- Propor melhorias.
- Reportar bugs.
- Adicionar novas funcionalidades.

## 📄 Licença

Este projeto é desenvolvido para fins educacionais. Use, modifique e compartilhe livremente.

---

💡 **Dica**: Este projeto oferece uma excelente base para explorar o desenvolvimento de Agentes de IA. Continue explorando e criando!
