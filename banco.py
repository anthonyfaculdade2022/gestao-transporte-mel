import sqlite3
import pandas as pd
from datetime import datetime

DATABASE_PATH = "transporte_mel.db"

ETAPAS_OPERACAO = [
    "Deslocamento vazio",
    "Ag. carregamento",
    "Carregando",
    "Deslocamento carregado",
    "Ag. descarregamento",
    "Descarregando",
]

ETAPAS_VALIDAS = [
    "Deslocamento vazio",
    "Ag. carregamento",
    "Carregando",
    "Deslocamento carregado",
    "Ag. descarregamento",
    "Descarregando",
    "Manutenção",
]

def conectar():
    return sqlite3.connect(DATABASE_PATH)


def formatar_tempo(segundos):
    """Formata segundos em HH:MM:SS."""
    if segundos is None or pd.isna(segundos):
        return ""
    segundos = int(segundos)
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segs = segundos % 60
    return f"{horas:02d}:{minutos:02d}:{segs:02d}"


def criar_banco():
    """Cria o banco de dados com as tabelas necessárias e faz migrações simples."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS frotas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE NOT NULL,
            unidade_carregamento TEXT NOT NULL,
            unidade_descarregamento TEXT NOT NULL,
            etapa_atual TEXT NOT NULL,
            inicio_etapa TEXT,
            em_manutencao INTEGER DEFAULT 0,
            motivo_manutencao TEXT,
            observacao_manutencao TEXT,
            previsao_retorno TEXT,
            data_criacao TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS viagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            frota_numero TEXT NOT NULL,
            unidade_carregamento TEXT NOT NULL,
            unidade_descarregamento TEXT NOT NULL,
            inicio TEXT NOT NULL,
            fim TEXT,
            lead_time_segundos INTEGER,
            status TEXT DEFAULT 'Em andamento',
            observacao TEXT,
            FOREIGN KEY (frota_numero) REFERENCES frotas(numero)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            viagem_id INTEGER,
            frota_numero TEXT NOT NULL,
            unidade_carregamento TEXT NOT NULL,
            unidade_descarregamento TEXT NOT NULL,
            etapa TEXT NOT NULL,
            inicio TEXT NOT NULL,
            fim TEXT,
            tempo_segundos INTEGER,
            observacao TEXT,
            FOREIGN KEY (frota_numero) REFERENCES frotas(numero),
            FOREIGN KEY (viagem_id) REFERENCES viagens(id)
        )
    """)

    # Migração para bancos antigos que não tinham viagem_id
    cursor.execute("PRAGMA table_info(historico)")
    colunas_historico = [col[1] for col in cursor.fetchall()]
    if "viagem_id" not in colunas_historico:
        cursor.execute("ALTER TABLE historico ADD COLUMN viagem_id INTEGER")

    conn.commit()
    conn.close()


def _obter_viagem_aberta(cursor, numero):
    cursor.execute("""
        SELECT id
        FROM viagens
        WHERE frota_numero = ? AND status = 'Em andamento'
        ORDER BY id DESC
        LIMIT 1
    """, (numero,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None


def _criar_viagem(cursor, numero, unidade_carregamento, unidade_descarregamento, inicio):
    cursor.execute("""
        INSERT INTO viagens (
            frota_numero,
            unidade_carregamento,
            unidade_descarregamento,
            inicio,
            status
        )
        VALUES (?, ?, ?, ?, 'Em andamento')
    """, (numero, unidade_carregamento, unidade_descarregamento, inicio))
    return cursor.lastrowid


def _finalizar_viagem_se_necessario(cursor, viagem_id, fim):
    if not viagem_id:
        return

    cursor.execute("SELECT inicio FROM viagens WHERE id = ?", (viagem_id,))
    resultado = cursor.fetchone()
    if not resultado:
        return

    inicio = datetime.fromisoformat(resultado[0])
    fim_dt = datetime.fromisoformat(fim)
    lead_time = int((fim_dt - inicio).total_seconds())

    cursor.execute("""
        UPDATE viagens
        SET fim = ?, lead_time_segundos = ?, status = 'Finalizada'
        WHERE id = ?
    """, (fim, lead_time, viagem_id))


def _finalizar_etapa_aberta(cursor, numero, fim):
    """Finaliza a última etapa aberta de uma frota e retorna viagem_id da etapa finalizada."""
    cursor.execute("""
        SELECT id, inicio, viagem_id
        FROM historico
        WHERE frota_numero = ? AND fim IS NULL
        ORDER BY id DESC
        LIMIT 1
    """, (numero,))
    resultado = cursor.fetchone()

    if not resultado:
        return None

    historico_id, inicio_str, viagem_id = resultado
    inicio = datetime.fromisoformat(inicio_str)
    fim_dt = datetime.fromisoformat(fim)
    tempo_segundos = int((fim_dt - inicio).total_seconds())

    cursor.execute("""
        UPDATE historico
        SET fim = ?, tempo_segundos = ?
        WHERE id = ?
    """, (fim, tempo_segundos, historico_id))

    return viagem_id


def adicionar_frota(numero, unidade_carregamento, unidade_descarregamento, etapa_inicial="Deslocamento vazio"):
    """Adiciona uma nova frota ao sistema."""
    conn = conectar()
    cursor = conn.cursor()

    try:
        agora = datetime.now().replace(microsecond=0).isoformat()

        viagem_id = None
        if etapa_inicial != "Manutenção":
            viagem_id = _criar_viagem(cursor, numero, unidade_carregamento, unidade_descarregamento, agora)

        cursor.execute("""
            INSERT INTO frotas (
                numero,
                unidade_carregamento,
                unidade_descarregamento,
                etapa_atual,
                inicio_etapa,
                data_criacao
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (numero, unidade_carregamento, unidade_descarregamento, etapa_inicial, agora, agora))

        cursor.execute("""
            INSERT INTO historico (
                viagem_id,
                frota_numero,
                unidade_carregamento,
                unidade_descarregamento,
                etapa,
                inicio
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (viagem_id, numero, unidade_carregamento, unidade_descarregamento, etapa_inicial, agora))

        conn.commit()
        return True, "Frota adicionada com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Frota com este número já existe!"
    finally:
        conn.close()


def obter_frotas():
    """Obtém todas as frotas."""
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM frotas ORDER BY numero", conn)
    conn.close()
    return df


def obter_frotas_ativas():
    """Obtém frotas que não estão em manutenção."""
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM frotas WHERE em_manutencao = 0 ORDER BY numero", conn)
    conn.close()
    return df


def obter_frotas_em_manutencao():
    """Obtém frotas em manutenção."""
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM frotas WHERE em_manutencao = 1 ORDER BY numero", conn)
    conn.close()
    return df


def excluir_frota(numero):
    """Exclui uma frota do sistema."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM historico WHERE frota_numero = ?", (numero,))
    cursor.execute("DELETE FROM viagens WHERE frota_numero = ?", (numero,))
    cursor.execute("DELETE FROM frotas WHERE numero = ?", (numero,))

    conn.commit()
    conn.close()
    return True, "Frota excluída com sucesso!"


def alterar_etapa(numero, nova_etapa):
    """Altera a etapa de uma frota, finaliza a anterior e abre nova etapa no histórico."""
    if nova_etapa not in ETAPAS_VALIDAS:
        return False, f"Etapa inválida: {nova_etapa}"

    conn = conectar()
    cursor = conn.cursor()

    agora = datetime.now().replace(microsecond=0).isoformat()

    viagem_id_anterior = _finalizar_etapa_aberta(cursor, numero, agora)

    cursor.execute("""
        SELECT unidade_carregamento, unidade_descarregamento, etapa_atual
        FROM frotas
        WHERE numero = ?
    """, (numero,))
    frota_info = cursor.fetchone()

    if not frota_info:
        conn.close()
        return False, "Frota não encontrada."

    unidade_carregamento, unidade_descarregamento, etapa_anterior = frota_info

    viagem_id = viagem_id_anterior or _obter_viagem_aberta(cursor, numero)

    # Se a viagem anterior estava finalizada ou não existe, cria uma nova viagem.
    if not viagem_id and nova_etapa != "Manutenção":
        viagem_id = _criar_viagem(cursor, numero, unidade_carregamento, unidade_descarregamento, agora)

    cursor.execute("""
        INSERT INTO historico (
            viagem_id,
            frota_numero,
            unidade_carregamento,
            unidade_descarregamento,
            etapa,
            inicio
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (viagem_id, numero, unidade_carregamento, unidade_descarregamento, nova_etapa, agora))

    cursor.execute("""
        UPDATE frotas
        SET etapa_atual = ?, inicio_etapa = ?
        WHERE numero = ?
    """, (nova_etapa, agora, numero))

    # Se saiu de Deslocamento vazio com histórico aberto, finaliza o ciclo vazio e abre a viagem carregada.
    if etapa_anterior == "Deslocamento vazio" and nova_etapa in ["Ag. carregamento", "Carregando"] and viagem_id_anterior:
        _finalizar_viagem_se_necessario(cursor, viagem_id_anterior, agora)
        novo_viagem_id = _criar_viagem(cursor, numero, unidade_carregamento, unidade_descarregamento, agora)

        cursor.execute("""
            UPDATE historico
            SET viagem_id = ?
            WHERE frota_numero = ? AND fim IS NULL
        """, (novo_viagem_id, numero))

    conn.commit()
    conn.close()
    return True, f"Etapa alterada para '{nova_etapa}' com sucesso!"


def alterar_inicio_etapa(numero, novo_inicio):
    """Altera o horário de início da etapa atual."""
    conn = conectar()
    cursor = conn.cursor()

    try:
        novo_inicio_iso = datetime.fromisoformat(novo_inicio).replace(microsecond=0).isoformat()

        cursor.execute("""
            UPDATE frotas
            SET inicio_etapa = ?
            WHERE numero = ?
        """, (novo_inicio_iso, numero))

        cursor.execute("""
            UPDATE historico
            SET inicio = ?
            WHERE frota_numero = ? AND fim IS NULL
        """, (novo_inicio_iso, numero))

        cursor.execute("""
            SELECT viagem_id
            FROM historico
            WHERE frota_numero = ? AND fim IS NULL
            ORDER BY id DESC
            LIMIT 1
        """, (numero,))
        resultado = cursor.fetchone()

        if resultado and resultado[0]:
            cursor.execute("""
                UPDATE viagens
                SET inicio = ?
                WHERE id = ? AND status = 'Em andamento'
            """, (novo_inicio_iso, resultado[0]))

        conn.commit()
        return True, "Horário de início alterado com sucesso!"
    except Exception as e:
        return False, f"Erro ao alterar horário: {str(e)}"
    finally:
        conn.close()


def alterar_unidades(numero, unidade_carregamento, unidade_descarregamento):
    """Altera as unidades de uma frota e atualiza etapa/viagem em andamento."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE frotas
        SET unidade_carregamento = ?, unidade_descarregamento = ?
        WHERE numero = ?
    """, (unidade_carregamento, unidade_descarregamento, numero))

    cursor.execute("""
        UPDATE historico
        SET unidade_carregamento = ?, unidade_descarregamento = ?
        WHERE frota_numero = ? AND fim IS NULL
    """, (unidade_carregamento, unidade_descarregamento, numero))

    cursor.execute("""
        SELECT viagem_id
        FROM historico
        WHERE frota_numero = ? AND fim IS NULL
        ORDER BY id DESC
        LIMIT 1
    """, (numero,))
    resultado = cursor.fetchone()

    if resultado and resultado[0]:
        cursor.execute("""
            UPDATE viagens
            SET unidade_carregamento = ?, unidade_descarregamento = ?
            WHERE id = ? AND status = 'Em andamento'
        """, (unidade_carregamento, unidade_descarregamento, resultado[0]))

    conn.commit()
    conn.close()
    return True, "Unidades alteradas com sucesso!"


def enviar_manutencao(numero, motivo, observacao, previsao_retorno):
    """Envia uma frota para manutenção."""
    conn = conectar()
    cursor = conn.cursor()

    agora = datetime.now().replace(microsecond=0).isoformat()

    viagem_id_anterior = _finalizar_etapa_aberta(cursor, numero, agora)

    cursor.execute("""
        UPDATE frotas
        SET em_manutencao = 1,
            motivo_manutencao = ?,
            observacao_manutencao = ?,
            previsao_retorno = ?,
            etapa_atual = 'Manutenção',
            inicio_etapa = ?
        WHERE numero = ?
    """, (motivo, observacao, previsao_retorno, agora, numero))

    cursor.execute("""
        SELECT unidade_carregamento, unidade_descarregamento
        FROM frotas
        WHERE numero = ?
    """, (numero,))
    frota_info = cursor.fetchone()

    if frota_info:
        cursor.execute("""
            INSERT INTO historico (
                viagem_id,
                frota_numero,
                unidade_carregamento,
                unidade_descarregamento,
                etapa,
                inicio,
                observacao
            )
            VALUES (?, ?, ?, ?, 'Manutenção', ?, ?)
        """, (viagem_id_anterior, numero, frota_info[0], frota_info[1], agora, f"Motivo: {motivo}. Obs: {observacao}"))

    conn.commit()
    conn.close()
    return True, "Frota enviada para manutenção!"


def retornar_manutencao(numero, etapa_retorno="Deslocamento vazio"):
    """Retorna uma frota da manutenção."""
    conn = conectar()
    cursor = conn.cursor()

    agora = datetime.now().replace(microsecond=0).isoformat()

    viagem_id_anterior = _finalizar_etapa_aberta(cursor, numero, agora)

    cursor.execute("""
        UPDATE frotas
        SET em_manutencao = 0,
            motivo_manutencao = NULL,
            observacao_manutencao = NULL,
            previsao_retorno = NULL,
            etapa_atual = ?,
            inicio_etapa = ?
        WHERE numero = ?
    """, (etapa_retorno, agora, numero))

    cursor.execute("""
        SELECT unidade_carregamento, unidade_descarregamento
        FROM frotas
        WHERE numero = ?
    """, (numero,))
    frota_info = cursor.fetchone()

    viagem_id = viagem_id_anterior
    if etapa_retorno != "Manutenção" and not viagem_id:
        viagem_id = _criar_viagem(cursor, numero, frota_info[0], frota_info[1], agora)

    if frota_info:
        cursor.execute("""
            INSERT INTO historico (
                viagem_id,
                frota_numero,
                unidade_carregamento,
                unidade_descarregamento,
                etapa,
                inicio
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (viagem_id, numero, frota_info[0], frota_info[1], etapa_retorno, agora))

    conn.commit()
    conn.close()
    return True, "Frota retornada da manutenção!"


def obter_historico():
    """Obtém o histórico completo formatado."""
    conn = conectar()
    df = pd.read_sql_query("""
        SELECT
            id,
            viagem_id,
            frota_numero,
            unidade_carregamento,
            unidade_descarregamento,
            etapa,
            inicio,
            fim,
            tempo_segundos,
            observacao
        FROM historico
        ORDER BY id DESC
    """, conn)
    conn.close()

    if not df.empty:
        df["inicio"] = pd.to_datetime(df["inicio"], format="mixed", errors="coerce").dt.strftime("%d/%m %H:%M")
        df["fim"] = df["fim"].apply(
            lambda x: pd.to_datetime(x, format="mixed", errors="coerce").strftime("%d/%m %H:%M")
            if pd.notna(x) and x != ""
            else ""
        )
        df["tempo"] = df["tempo_segundos"].apply(lambda x: formatar_tempo(x) if pd.notna(x) else "")

    return df


def obter_historico_bruto():
    """Obtém histórico bruto, ideal para filtros, cálculos e telas avançadas."""
    conn = conectar()
    df = pd.read_sql_query("""
        SELECT
            id,
            viagem_id,
            frota_numero,
            unidade_carregamento,
            unidade_descarregamento,
            etapa,
            inicio,
            fim,
            tempo_segundos,
            observacao
        FROM historico
        ORDER BY id DESC
    """, conn)
    conn.close()

    if not df.empty:
        df["inicio_dt"] = pd.to_datetime(df["inicio"], format="mixed", errors="coerce")
        df["fim_dt"] = pd.to_datetime(df["fim"], format="mixed", errors="coerce")
        df["data"] = df["inicio_dt"].dt.date
        df["operacao"] = df["unidade_carregamento"] + " → " + df["unidade_descarregamento"]
        df["tempo"] = df["tempo_segundos"].apply(lambda x: formatar_tempo(x) if pd.notna(x) else "")

    return df


def obter_viagens_consolidadas():
    """Consolida viagens usando viagem_id e tempos por etapa."""
    historico = obter_historico_bruto()

    if historico.empty or "viagem_id" not in historico.columns:
        return pd.DataFrame()

    historico = historico[
        historico["viagem_id"].notna() &
        historico["etapa"].isin(ETAPAS_OPERACAO)
    ].copy()

    if historico.empty:
        return pd.DataFrame()

    historico["viagem_id"] = historico["viagem_id"].astype(int)
    historico["tempo_segundos"] = historico["tempo_segundos"].fillna(0)

    etapas_pivot = historico.pivot_table(
        index=["viagem_id", "frota_numero", "operacao"],
        columns="etapa",
        values="tempo_segundos",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    for etapa in ETAPAS_OPERACAO:
        if etapa not in etapas_pivot.columns:
            etapas_pivot[etapa] = 0

    resumo = historico.groupby(["viagem_id", "frota_numero", "operacao"], as_index=False).agg(
        inicio_viagem=("inicio_dt", "min"),
        fim_viagem=("fim_dt", "max"),
        lead_time_segundos=("tempo_segundos", "sum")
    )

    viagens = resumo.merge(etapas_pivot, on=["viagem_id", "frota_numero", "operacao"], how="left")

    viagens["Data"] = viagens["inicio_viagem"].dt.strftime("%d/%m/%Y")
    viagens["Frota"] = viagens["frota_numero"]
    viagens["Operação"] = viagens["operacao"]

    for etapa in ETAPAS_OPERACAO:
        viagens[etapa] = viagens[etapa].apply(formatar_tempo)

    viagens["Lead Time"] = viagens["lead_time_segundos"].apply(formatar_tempo)

    colunas = [
        "viagem_id",
        "Data",
        "Frota",
        "Operação",
        "Deslocamento vazio",
        "Ag. carregamento",
        "Carregando",
        "Deslocamento carregado",
        "Ag. descarregamento",
        "Descarregando",
        "Lead Time",
    ]

    return viagens[colunas].rename(columns={"viagem_id": "Viagem"})


def atualizar_historico_linha(
    linha_id,
    novo_inicio,
    novo_fim,
    observacao,
    frota_numero=None,
    unidade_carregamento=None,
    unidade_descarregamento=None,
    etapa=None
):
    """Atualiza uma linha do histórico e recalcula tempo."""
    conn = conectar()
    cursor = conn.cursor()

    try:
        novo_inicio_iso = datetime.fromisoformat(novo_inicio).replace(microsecond=0).isoformat()
        novo_fim_iso = datetime.fromisoformat(novo_fim).replace(microsecond=0).isoformat() if novo_fim else None

        tempo_segundos = None
        if novo_fim_iso:
            inicio_dt = datetime.fromisoformat(novo_inicio_iso)
            fim_dt = datetime.fromisoformat(novo_fim_iso)
            tempo_segundos = int((fim_dt - inicio_dt).total_seconds())
            if tempo_segundos < 0:
                return False, "Erro ao atualizar: tempo negativo não permitido."

        if frota_numero is None or unidade_carregamento is None or unidade_descarregamento is None or etapa is None:
            cursor.execute("""
                SELECT frota_numero, unidade_carregamento, unidade_descarregamento, etapa
                FROM historico
                WHERE id = ?
            """, (linha_id,))
            dados_atuais = cursor.fetchone()
            if not dados_atuais:
                return False, "Erro ao atualizar: registro não encontrado."

            frota_atual, carga_atual, descarga_atual, etapa_atual = dados_atuais
            frota_numero = frota_numero or frota_atual
            unidade_carregamento = unidade_carregamento or carga_atual
            unidade_descarregamento = unidade_descarregamento or descarga_atual
            etapa = etapa or etapa_atual

        cursor.execute("""
            UPDATE historico
            SET frota_numero = ?,
                unidade_carregamento = ?,
                unidade_descarregamento = ?,
                etapa = ?,
                inicio = ?,
                fim = ?,
                tempo_segundos = ?,
                observacao = ?
            WHERE id = ?
        """, (
            frota_numero,
            unidade_carregamento,
            unidade_descarregamento,
            etapa,
            novo_inicio_iso,
            novo_fim_iso,
            tempo_segundos,
            observacao,
            linha_id
        ))

        cursor.execute("SELECT viagem_id FROM historico WHERE id = ?", (linha_id,))
        resultado = cursor.fetchone()

        if resultado and resultado[0]:
            viagem_id = resultado[0]
            placeholders = ",".join("?" for _ in ETAPAS_OPERACAO)
            cursor.execute("""
                SELECT
                    MIN(inicio),
                    MAX(fim),
                    SUM(COALESCE(tempo_segundos, 0)),
                    SUM(CASE WHEN fim IS NULL THEN 1 ELSE 0 END)
                FROM historico
                WHERE viagem_id = ?
                  AND etapa IN ({})
            """.format(placeholders), (viagem_id, *ETAPAS_OPERACAO))
            dados_viagem = cursor.fetchone()

            if dados_viagem:
                inicio_viagem, fim_viagem, lead_time, etapas_abertas = dados_viagem

                possui_etapa_aberta = (etapas_abertas or 0) > 0
                fim_viagem_atualizado = None if possui_etapa_aberta else fim_viagem
                status = "Em andamento" if possui_etapa_aberta else "Finalizada"

                cursor.execute("""
                    UPDATE viagens
                    SET inicio = ?, fim = ?, lead_time_segundos = ?, status = ?
                    WHERE id = ?
                """, (inicio_viagem, fim_viagem_atualizado, lead_time or 0, status, viagem_id))

        conn.commit()
        return True, "Histórico atualizado com sucesso!"
    except Exception as e:
        return False, f"Erro ao atualizar: {str(e)}"
    finally:
        conn.close()


def obter_dados_relatorios():
    """Obtém dados para gerar relatórios."""
    conn = conectar()

    tempo_por_etapa = pd.read_sql_query("""
        SELECT etapa, AVG(tempo_segundos) as tempo_medio, COUNT(*) as quantidade
        FROM historico
        WHERE tempo_segundos IS NOT NULL AND etapa != 'Manutenção'
        GROUP BY etapa
        ORDER BY tempo_medio DESC
    """, conn)

    tempo_por_operacao = pd.read_sql_query("""
        SELECT
            unidade_carregamento || ' → ' || unidade_descarregamento as operacao,
            AVG(tempo_segundos) as tempo_medio,
            COUNT(*) as quantidade
        FROM historico
        WHERE tempo_segundos IS NOT NULL AND etapa != 'Manutenção'
        GROUP BY unidade_carregamento, unidade_descarregamento
        ORDER BY tempo_medio DESC
    """, conn)

    etapas_por_frota = pd.read_sql_query("""
        SELECT frota_numero, COUNT(*) as quantidade_etapas, SUM(tempo_segundos) as tempo_total
        FROM historico
        WHERE tempo_segundos IS NOT NULL
        GROUP BY frota_numero
        ORDER BY frota_numero
    """, conn)

    tempo_manutencao = pd.read_sql_query("""
        SELECT frota_numero, SUM(tempo_segundos) as tempo_total_manutencao
        FROM historico
        WHERE etapa = 'Manutenção' AND tempo_segundos IS NOT NULL
        GROUP BY frota_numero
        ORDER BY tempo_total_manutencao DESC
    """, conn)

    viagens_por_frota = pd.read_sql_query("""
        SELECT frota_numero, COUNT(*) as quantidade_viagens
        FROM viagens
        GROUP BY frota_numero
        ORDER BY quantidade_viagens DESC
    """, conn)

    conn.close()

    return tempo_por_etapa, tempo_por_operacao, etapas_por_frota, tempo_manutencao, viagens_por_frota


def calcular_tempo_etapa(numero):
    """Calcula o tempo decorrido da etapa atual."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT inicio_etapa FROM frotas WHERE numero = ?", (numero,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado and resultado[0]:
        inicio = datetime.fromisoformat(resultado[0])
        agora = datetime.now()
        tempo = int((agora - inicio).total_seconds())
        return formatar_tempo(tempo)

    return "-"


def inserir_dados_exemplo():
    """Insere dados de exemplo no banco."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM frotas")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    frotas_exemplo = [
        ("911302", "Figueira", "Alcoazul", "Descarregando"),
        ("911388", "Figueira", "Alcoazul", "Deslocamento vazio"),
        ("911321", "Figueira", "Generalco", "Carregando"),
        ("911330", "Aralco", "Alcoazul", "Ag. carregamento"),
        ("911340", "Aralco", "Generalco", "Deslocamento carregado"),
        ("911350", "Figueira", "Generalco", "Deslocamento vazio"),
        ("911360", "Aralco", "Alcoazul", "Deslocamento vazio"),
        ("911355", "Figueira", "Alcoazul", "Carregando"),
    ]

    agora = datetime.now().replace(microsecond=0).isoformat()

    for numero, carga, descar, etapa in frotas_exemplo:
        try:
            viagem_id = _criar_viagem(cursor, numero, carga, descar, agora)

            cursor.execute("""
                INSERT INTO frotas (
                    numero,
                    unidade_carregamento,
                    unidade_descarregamento,
                    etapa_atual,
                    inicio_etapa,
                    data_criacao
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (numero, carga, descar, etapa, agora, agora))

            cursor.execute("""
                INSERT INTO historico (
                    viagem_id,
                    frota_numero,
                    unidade_carregamento,
                    unidade_descarregamento,
                    etapa,
                    inicio
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (viagem_id, numero, carga, descar, etapa, agora))
        except Exception:
            pass

    conn.commit()
    conn.close()
