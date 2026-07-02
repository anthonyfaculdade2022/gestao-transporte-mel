# Gestão de Transporte de Mel

Sistema Streamlit para controle operacional de frotas, histórico, viagens consolidadas e indicadores.

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar e gerar link público

### Opção recomendada: Render

1. Crie um repositório no GitHub.
2. Envie estes arquivos do projeto para o repositório.
3. Acesse `https://render.com`.
4. Clique em `New` > `Web Service`.
5. Conecte o repositório do GitHub.
6. Use estas configurações:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
7. Clique em `Deploy`.

Ao finalizar, o Render gera um link público parecido com:

```text
https://gestao-transporte-mel.onrender.com
```

### Opção alternativa: Streamlit Community Cloud

1. Suba o projeto no GitHub.
2. Acesse `https://share.streamlit.io`.
3. Clique em `New app`.
4. Selecione o repositório.
5. Em `Main file path`, informe:

```text
app.py
```

6. Clique em `Deploy`.

O Streamlit gera um link parecido com:

```text
https://gestao-transporte-mel.streamlit.app
```

## Observação sobre o banco SQLite

O sistema usa SQLite local. Isso funciona para testes e uso simples, mas em hospedagens gratuitas os dados podem ser reiniciados em redeploys ou reinicializações.

Para uso definitivo com várias pessoas, o ideal é migrar o banco para PostgreSQL.
