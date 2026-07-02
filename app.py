import streamlit as st
import pandas as pd
from html import escape
from datetime import datetime
import plotly.express as px
from banco import (
    criar_banco, inserir_dados_exemplo, obter_frotas_ativas, obter_frotas_em_manutencao,
    adicionar_frota, excluir_frota, alterar_etapa, alterar_inicio_etapa, alterar_unidades,
    enviar_manutencao, retornar_manutencao, obter_historico, atualizar_historico_linha,
    calcular_tempo_etapa, formatar_tempo, obter_frotas
)

# Configuração da página
st.set_page_config(
    page_title="Gestão de Transporte de Mel",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar banco de dados
criar_banco()
inserir_dados_exemplo()

# CSS personalizado - Painel Profissional Compacto (unificado)

st.markdown("""
                             
<style>
@import url('https://fonts.googleapis.com/css2?family=Material+Icons');
:root{
    --bg: #0F172A;
    --card: #1E293B;
    --sidebar: #111827;
    --line: #334155;
    --text: #FFFFFF;
    --muted: #CBD5E1;
    --accent: #20BA58;
}
* { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

[data-testid="stSidebar"] {
    background-color: var(--sidebar) !important;
    color: var(--muted) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 22px 16px 18px !important;
}
[data-testid="stSidebar"] hr {
    margin: 18px 0 !important;
    border-color: rgba(203,213,225,.22) !important;
}
[data-testid="stSidebar"] [role="radiogroup"] {
    display:flex;
    flex-direction:column;
    gap:8px;
}
[data-testid="stSidebar"] label[data-baseweb="radio"] {
    width:100%;
    min-height:40px;
    margin:0 !important;
    padding:0 12px !important;
    border:1px solid rgba(51,65,85,.72);
    border-radius:10px;
    background:rgba(30,41,59,.58);
    color:#CBD5E1 !important;
    display:flex !important;
    align-items:center !important;
    transition:background .18s ease, border-color .18s ease, transform .18s ease;
}
[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
    background:#263445;
    border-color:#38BDF8;
    transform:translateX(2px);
}
[data-testid="stSidebar"] label[data-baseweb="radio"] p {
    color:#CBD5E1 !important;
    font-size:13px !important;
    font-weight:750 !important;
}
[data-testid="stSidebar"] label[data-baseweb="radio"] div:first-child {
    margin-right:8px !important;
}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) {
    background:rgba(34,197,94,.15);
    border-color:#22C55E;
    box-shadow:0 8px 20px rgba(2,6,23,.28);
}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) p {
    color:#FFFFFF !important;
}

/* Headings */
h1, h2, h3 { color: var(--text); font-weight:600; }

/* Operation Card */
.operation-box {
    background: #1E293B;
    border: 1px solid #334155;
    border-left: 4px solid #20BA58;
    padding: 12px 16px;
    margin: 24px 0 12px;
    border-radius: 10px;
    box-shadow: 0 12px 28px rgba(2,6,23,0.42);
    transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
}
.operation-box:hover { transform: translateY(-2px); box-shadow: 0 16px 34px rgba(2,6,23,0.58); background:#263445; }
.operation-box strong { color: var(--text); font-size: 1.05rem; letter-spacing: .02em; }
.operation-box.route-figueira-alcoazul { border-left-color:#22C55E; }
.operation-box.route-figueira-generalco { border-left-color:#38BDF8; }
.operation-box.route-aralco-alcoazul { border-left-color:#F59E0B; }
.operation-box.route-aralco-generalco { border-left-color:#A78BFA; }
.operation-head {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:14px;
}
.operation-meta { color:#CBD5E1; font-size:.86rem; font-weight:700; white-space:nowrap; }

/* Fleet Row - Compact */
.fleet-row {
    display:flex;
    align-items:center;
    justify-content:flex-start;
    gap:12px;
    padding:0 14px;
    margin:5px 0;
    height:48px;
    min-height:48px;
    max-height:48px;
    box-sizing:border-box;
    background: rgba(255,255,255,0.025);
    border-radius:10px; font-size:0.95em; border-left:3px solid var(--line);
    border-top:1px solid rgba(255,255,255,0.035);
    border-bottom:1px solid rgba(0,0,0,0.12);
    transition: background .18s ease, transform .18s ease, border-color .18s ease;
}
.fleet-row:hover {
    background:#263445;
    transform: translateY(-1px);
}
.fleet-row-number { font-weight:800; min-width:86px; color:var(--text); font-size:18px; letter-spacing:.01em; }
.fleet-row-units { color:var(--muted); font-size:0.85em; }
.fleet-row.cell-center { justify-content:center; text-align:center; }
.fleet-row.stage-cell { justify-content:center; overflow:hidden; }
.fleet-row-time { color:#FFFFFF; min-width:96px; text-align:center; font-size:17px; font-weight:800; line-height:1; }
.fleet-row-start { color:#CBD5E1; font-size:15px; font-weight:750; display:block; width:100%; text-align:center; }

/* Badges suaves */
.fleet-row-stage {
    height:32px;
    min-height:32px;
    max-height:32px;
    box-sizing:border-box;
    font-weight:700;
    color:var(--text);
    font-size:13px;
    padding:0 14px;
    border-radius:999px;
    display:inline-flex;
    align-items:center;
    justify-content:center;
    gap:7px;
    white-space:nowrap;
    border:1px solid rgba(255,255,255,0.14);
    line-height:1;
}
.badge-descarregando { background:rgba(249,115,22,.18); color:#FDBA74; border-color:#F97316; }
.badge-agdescarregamento { background:rgba(245,158,11,.18); color:#FCD34D; border-color:#F59E0B; }
.badge-deslocamentocarregado { background:rgba(132,204,22,.18); color:#BEF264; border-color:#84CC16; }
.badge-carregando { background:rgba(34,197,94,.18); color:#BBF7D0; border-color:#22C55E; }
.badge-agcarregamento { background:rgba(250,204,21,.18); color:#FEF08A; border-color:#FACC15; }
.badge-deslocamentovazio { background:rgba(56,189,248,.18); color:#BAE6FD; border-color:#38BDF8; }
.badge-default { background:rgba(148,163,184,.18); color:#CBD5E1; }
.badge-manutencao { background:rgba(239,68,68,.18); color:#FCA5A5; border-color:#EF4444; }

/* Stage border colors */
.stage-color-descarregando { border-left-color: #F97316; }
.stage-color-agdescarregamento { border-left-color: #F59E0B; }
.stage-color-deslocamentocarregado { border-left-color: #84CC16; }
.stage-color-carregando { border-left-color: #22C55E; }
.stage-color-agcarregamento { border-left-color: #FACC15; }
.stage-color-deslocamentovazio { border-left-color: #38BDF8; }
.stage-color-default { border-left-color: #6B7280; }
.stage-color-manutencao { border-left-color: #EF4444; }

/* Sidebar */
.sidebar-brand {
    display:flex;
    align-items:center;
    gap:10px;
    padding:12px 10px;
    border-radius:12px;
    background:linear-gradient(135deg, rgba(30,41,59,.95), rgba(15,23,42,.72));
    border:1px solid rgba(51,65,85,.9);
    box-shadow:0 12px 26px rgba(2,6,23,.34);
}
.sidebar-brand-icon {
    width:38px;
    height:38px;
    min-width:38px;
    border-radius:10px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:rgba(34,197,94,.15);
    border:1px solid rgba(34,197,94,.42);
    color:#BBF7D0;
    font-size:20px;
}
.sidebar-title {
    color:#FFFFFF;
    font-size:12px;
    font-weight:850;
    line-height:1.2;
    letter-spacing:.03em;
    text-transform:uppercase;
}
.sidebar-kicker {
    margin:18px 0 8px;
    color:#94A3B8;
    font-size:10px;
    font-weight:850;
    letter-spacing:.11em;
    text-transform:uppercase;
}
.sidebar-footer {
    padding:12px;
    border-radius:10px;
    background:rgba(30,41,59,.54);
    border:1px solid rgba(51,65,85,.72);
    color:#CBD5E1;
    font-size:12px;
    font-weight:700;
    line-height:1.35;
}
.sidebar-footer strong {
    color:#FFFFFF;
    display:block;
    font-size:12px;
    margin-bottom:2px;
}

/* Edit Drawer (coluna direita) */

.edit-drawer {
    background: #1E293B;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #334155;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
}
            
/* Buttons modernos */
div[data-testid="stButton"] {
    margin: 5px 0 !important;
}
div[data-testid="stButton"] button {
    border-radius:8px;
    height:48px;
    min-height:48px;
    max-height:48px;
    display:flex;
    align-items:center;
    justify-content:center;
    padding:0 10px !important;
    white-space:nowrap;
    background:#1E293B !important;
    color:#FFFFFF !important;
    border:1px solid #334155 !important;
    box-shadow:none !important;
}

/* Compactar espaços */
.stMarkdown { margin-bottom:6px !important; }

/* Maintenance Section */
.maintenance-section {
    background: #1E293B;
    border-left: 4px solid #EF4444;
    padding: 11px 12px;
    margin: 8px 0;
    border-radius: 8px;
    color: #FFFFFF;
    box-shadow: 0 4px 12px rgba(0,0,0,0.35);
}

.ops-header {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 22px 24px;
    margin: 4px 0 24px;
    box-shadow: 0 12px 28px rgba(2,6,23,0.34);
}
.ops-title {
    color: #FFFFFF;
    font-size: 2rem;
    font-weight: 750;
    line-height: 1.15;
}
.ops-subtitle {
    color: #CBD5E1;
    font-size: .98rem;
    margin-top: 7px;
}
.ops-section-title {
    color: #FFFFFF;
    font-size: 1.1rem;
    font-weight: 750;
    margin: 18px 0 10px;
}
.ops-table-head {
    color:#CBD5E1;
    font-size:.76rem;
    font-weight:800;
    text-transform:uppercase;
    letter-spacing:.05em;
    padding: 0 4px 2px;
    height:22px;
    line-height:22px;
    white-space:nowrap;
}
.ops-table-head.center {
    text-align:center;
}
.ops-empty-badge {
    display:inline-flex;
    align-items:center;
    gap:7px;
    background:rgba(34,197,94,.16);
    color:#86EFAC;
    border:1px solid rgba(34,197,94,.32);
    border-radius:999px;
    padding:8px 13px;
    font-size:.86rem;
    font-weight:750;
}
.ops-maintenance-card {
    background:#1E293B;
    border:1px solid #334155;
    border-left:4px solid #2DD4BF;
    border-radius:12px;
    padding:16px;
    margin:22px 0 14px;
    box-shadow:0 12px 28px rgba(2,6,23,.34);
}
.ops-maintenance-title {
    color:#FFFFFF;
    font-size:1.05rem;
    font-weight:800;
    margin-bottom:10px;
}
.maintenance-grid-head,
.maintenance-grid-row {
    display:grid;
    grid-template-columns:19% 22% 35% 24%;
    gap:8px;
    align-items:center;
}
.maintenance-grid-head {
    margin-top:4px;
}
.maintenance-grid-row {
    margin:5px 0;
}
.maintenance-cell {
    height:48px;
    min-height:48px;
    max-height:48px;
    margin:0;
    padding:0 12px;
}
.maintenance-cell .fleet-row-time {
    min-width:0;
    width:100%;
    font-size:16px;
}
.maintenance-action-head {
    height:22px;
    line-height:22px;
    text-align:center;
}
.maintenance-action-cell {
    height:48px;
    display:flex;
    align-items:center;
    justify-content:center;
    margin:5px 0;
}
.ops-action-button {
    height:56px;
    min-height:56px;
    max-height:56px;
    display:flex;
    align-items:center;
    justify-content:center;
    margin:8px 0;
}
.ops-sidebar-card {
    background:#1E293B;
    border:1px solid #334155;
    border-radius:12px;
    padding:16px;
    margin-bottom:18px;
    box-shadow:0 10px 24px rgba(2,6,23,.28);
}
.ops-card-title {
    color:#FFFFFF;
    font-size:1rem;
    font-weight:800;
    margin-bottom:12px;
}
.ops-fleet-mini {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    background:rgba(255,255,255,.025);
    border:1px solid #334155;
    border-radius:10px;
    padding:10px 12px;
    margin:8px 0;
}
.ops-fleet-mini strong {
    color:#FFFFFF;
    font-size:.98rem;
}

/* Edit Modal - Menor */
.edit-modal {
    background: #1E293B;
    padding: 14px;
    border-radius: 10px;
    border: 1px solid #334155;
    color: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.35);
}

/* Buttons */
.stButton>button {
    font-weight: 600;
    border-radius: 8px;
    padding: 6px 12px;
    transition: all 0.18s ease;
    border: none;
    font-size: 0.9em;
    background: rgba(255,255,255,0.03);
    color: var(--text);
}
            
.stForm button {
    background: rgba(255,255,255,0.03);
    color: var(--text) !important;
}            

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(2,6,23,0.6);
    background: #2563EB !important;
    color: #FFFFFF !important;
}

.btn-edit {
    padding: 4px 8px !important;
    font-size: 1.1em !important;
    min-width: auto !important;
}

/* WhatsApp Button (aplicado globalmente via seletor) */
div[data-testid="stButton"] button.whatsapp, .btn-whatsapp {
    background: linear-gradient(135deg, #25D366 0%, #20BA58 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 1em !important;
    padding: 12px 20px !important;
    box-shadow: 0 4px 15px rgba(37, 211, 102, 0.35) !important;
}
div[data-testid="stButton"] button.whatsapp:hover, .btn-whatsapp:hover {
    box-shadow: 0 6px 25px rgba(37, 211, 102, 0.5) !important;
    transform: translateY(-3px) !important;
}

/* Forms */
.stForm {
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: 10px;
    padding: 12px;
}

/* Selectbox e inputs */
.stSelectbox, .stTextInput, .stTextArea {
    border-radius: 6px !important;                
}
            
.stTextArea textarea {
    background: #1E293B !important;
    color: #FFFFFF !important;
    border: 1px solid #475569 !important;
    border-radius: 8px !important;
}            

div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"],
div[data-testid="stTimeInput"] input {
    min-height: 42px;
}

/* Divider */
hr {
    margin: 12px 0 !important;
    border: 1px solid #e2e8f0 !important;
}

/* Compactar espaços */
.stMarkdown {
    margin-bottom: 4px !important;
}

/* Historico - TMS operacional */
.block-container {
    max-width: 1380px;
    padding-top: 2rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
}

.hist-header {
    background: #1E293B;
    border: 1px solid #334155;
    border-left: 4px solid #3B82F6;
    border-radius: 12px;
    padding: 22px 24px;
    margin: 4px 0 12px 0;
    box-shadow: 0 12px 28px rgba(2,6,23,0.34);
}

.hist-title {
    color: #FFFFFF;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: 0;
    margin: 0;
}

.hist-subtitle {
    color: #CBD5E1;
    font-size: 0.98rem;
    margin-top: 6px;
}

.hist-divider {
    height: 1px;
    background: #334155;
    margin: 0 0 30px;
}

.hist-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-left: 4px solid #3B82F6;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 10px 24px rgba(2, 6, 23, 0.32);
    min-height: 150px;
    transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
}

.hist-card.registros { border-left-color:#3B82F6; }
.hist-card.frotas { border-left-color:#14B8A6; }
.hist-card.tempo-total { border-left-color:#EAB308; }
.hist-card.tempo-medio { border-left-color:#8B5CF6; }
.hist-card.unidade-carga { border-left-color:#14B8A6; }
.hist-card.unidade-descarga { border-left-color:#3B82F6; }

.hist-unit-card {
    position:relative;
    min-height:214px;
    padding:18px 18px 16px;
    overflow:hidden;
}

.hist-unit-card.unidade-carga {
    background:linear-gradient(180deg, rgba(20,184,166,.16), rgba(30,41,59,1) 44%);
    border-color:rgba(20,184,166,.42);
    border-left-color:#14B8A6;
}

.hist-unit-card.unidade-descarga {
    background:linear-gradient(180deg, rgba(59,130,246,.16), rgba(30,41,59,1) 44%);
    border-color:rgba(59,130,246,.42);
    border-left-color:#3B82F6;
}

.hist-unit-top {
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:10px;
    margin-bottom:14px;
}

.hist-unit-name {
    color:#FFFFFF;
    font-size:1.42rem;
    font-weight:900;
    line-height:1.1;
}

.hist-unit-type {
    color:#CBD5E1;
    font-size:.72rem;
    font-weight:850;
    text-transform:uppercase;
    letter-spacing:.06em;
    margin-bottom:4px;
}

.hist-unit-status {
    display:inline-flex;
    align-items:center;
    justify-content:center;
    white-space:nowrap;
    min-height:28px;
    padding:0 10px;
    border-radius:999px;
    background:rgba(34,197,94,.14);
    border:1px solid rgba(34,197,94,.34);
    color:#BBF7D0;
    font-size:.72rem;
    font-weight:850;
}

.hist-unit-metrics {
    display:grid;
    grid-template-columns:repeat(2, minmax(0, 1fr));
    gap:10px;
}

.hist-unit-metric {
    background:rgba(15,23,42,.42);
    border:1px solid rgba(51,65,85,.86);
    border-radius:10px;
    padding:9px 10px;
    min-width:0;
}

.hist-unit-label {
    color:#94A3B8;
    font-size:.68rem;
    font-weight:800;
    text-transform:uppercase;
    letter-spacing:.04em;
    margin-bottom:4px;
}

.hist-unit-number {
    color:#FFFFFF;
    font-size:1.02rem;
    font-weight:900;
    line-height:1.1;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap;
}

.hist-insight-card {
    background:#1E293B;
    border:1px solid #334155;
    border-radius:12px;
    padding:16px 18px;
    box-shadow:0 10px 24px rgba(2,6,23,.26);
    min-height:116px;
}

.hist-insight-title {
    color:#CBD5E1;
    font-size:.72rem;
    font-weight:850;
    text-transform:uppercase;
    letter-spacing:.05em;
    margin-bottom:8px;
}

.hist-insight-value {
    color:#FFFFFF;
    font-size:1.45rem;
    font-weight:900;
    line-height:1.1;
}

.hist-insight-desc {
    color:#94A3B8;
    font-size:.78rem;
    margin-top:8px;
}

.hist-compare-card {
    background:#1E293B;
    border:1px solid #334155;
    border-radius:12px;
    padding:16px;
    box-shadow:0 10px 24px rgba(2,6,23,.26);
}

.hist-compare-title {
    color:#FFFFFF;
    font-size:1rem;
    font-weight:900;
    margin-bottom:12px;
}

.hist-compare-grid {
    display:grid;
    grid-template-columns:1fr auto 1fr;
    gap:12px;
    align-items:stretch;
}

.hist-compare-side {
    background:rgba(15,23,42,.42);
    border:1px solid #334155;
    border-radius:10px;
    padding:12px;
}

.hist-compare-vs {
    display:flex;
    align-items:center;
    justify-content:center;
    color:#CBD5E1;
    font-weight:900;
    font-size:.78rem;
}

.hist-card-icon {
    font-size:1.45rem;
    line-height:1;
    margin-bottom:8px;
}

.hist-card:hover {
    background: #263445;
    transform: translateY(-2px);
    box-shadow: 0 14px 30px rgba(2, 6, 23, 0.42);
}

.hist-card-title {
    color: #CBD5E1;
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .04em;
    margin-bottom: 10px;
}

.hist-card-value {
    color: #FFFFFF;
    font-size: clamp(1.25rem, 1.8vw, 1.95rem);
    line-height: 1.1;
    font-weight: 850;
    min-height: 2.18rem;
    overflow-wrap:anywhere;
    word-break:break-word;
}

.hist-card-desc {
    color:#CBD5E1;
    font-size:.76rem;
    margin-top:8px;
    min-height:1.1rem;
    line-height:1.35;
    overflow:hidden;
    text-overflow:ellipsis;
}

.hist-card-detail {
    color:#CBD5E1;
    font-size:.78rem;
    font-weight:700;
    line-height:1.4;
    margin-top:8px;
}

.hist-card-detail strong {
    color:#FFFFFF;
}

.hist-kpi-card {
    min-height:176px;
    display:flex;
    flex-direction:column;
}

.hist-kpi-card .hist-card-value {
    font-size:clamp(1.2rem, 1.55vw, 1.75rem);
    min-height:2.4rem;
}

.hist-kpi-total {
    display:inline-flex;
    align-items:center;
    justify-content:flex-start;
    width:fit-content;
    max-width:100%;
    margin-top:auto;
    padding:6px 10px;
    border-radius:999px;
    background:rgba(15,23,42,.42);
    border:1px solid rgba(148,163,184,.22);
    color:#FFFFFF;
    font-size:.8rem;
    font-weight:850;
    white-space:nowrap;
}

.hist-section-title {
    color: #FFFFFF;
    font-size: 1.08rem;
    font-weight: 700;
    margin: 26px 0 10px;
}

.hist-edit-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 10px 24px rgba(2, 6, 23, 0.26);
}

.hist-edit-card {
    margin-top: 6px;
}

.hist-table-wrap {
    border: 1px solid #334155;
    border-radius: 12px;
    overflow: hidden;
    overflow-x: auto;
    background: #1E293B;
    box-shadow: 0 10px 24px rgba(2, 6, 23, 0.26);
    max-height: 430px;
    overflow-y: auto;
    margin-top: 6px;
}

.hist-table {
    width: 100%;
    min-width: 760px;
    border-collapse: collapse;
    table-layout: fixed;
}

.hist-table thead th {
    position: sticky;
    top: 0;
    z-index: 2;
    background: #263445;
    color: #CBD5E1;
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: .04em;
    padding: 12px 10px;
    border-bottom: 1px solid #334155;
    text-align: left;
}

.hist-table thead th.hist-center {
    text-align: center;
}

.hist-table tbody td {
    color: #FFFFFF;
    padding: 13px 10px;
    border-bottom: 1px solid #334155;
    font-size: 0.86rem;
    vertical-align: middle;
    word-wrap: break-word;
    overflow-wrap: anywhere;
}

.hist-table tbody tr:nth-child(even) td {
    background: rgba(15,23,42,.28);
}

.hist-table tbody tr:hover td {
    background: #263445 !important;
}

.hist-table td.hist-center {
    text-align: center;
}

.hist-table th.hist-right,
.hist-table td.hist-right {
    text-align: right;
}

.hist-date {
    display: flex;
    flex-direction: column;
    gap: 2px;
    line-height: 1.15;
}

.hist-date span:first-child {
    color: #FFFFFF;
    font-weight: 650;
}

.hist-date span:last-child {
    color: #CBD5E1;
    font-size: 0.78rem;
}

.hist-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    border-radius: 999px;
    min-height: 30px;
    padding: 0 11px;
    font-weight: 800;
    font-size: 0.76rem;
    white-space: nowrap;
    border: 1px solid rgba(255,255,255,0.14);
    max-width: 100%;
}

.hist-operation-badge {
    background: rgba(59,130,246,.14);
    border-color: rgba(59,130,246,.36);
    color: #BFDBFE;
}

.hist-time {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    min-height: 30px;
    padding: 0 10px;
    border-radius: 999px;
    font-weight: 850;
    border: 1px solid rgba(255,255,255,.12);
}

.hist-time-ok { background:rgba(34,197,94,.12); color:#FFFFFF; border-color:rgba(34,197,94,.25); }
.hist-time-warning { background:rgba(234,179,8,.12); color:#FFFFFF; border-color:rgba(234,179,8,.25); }
.hist-time-critical { background:rgba(239,68,68,.12); color:#FFFFFF; border-color:rgba(239,68,68,.25); }

.hist-travel-time {
    display:inline-flex;
    align-items:center;
    justify-content:center;
    min-height:28px;
    min-width:76px;
    padding:0 9px;
    border-radius:999px;
    background:rgba(51,65,85,.72);
    border:1px solid rgba(148,163,184,.22);
    color:#F8FAFC;
    font-weight:800;
    font-size:.78rem;
}

.hist-empty-time {
    color:#64748B;
    font-weight:700;
}

.hist-stage-carregando { background: rgba(34,197,94,.18); color:#BBF7D0; border-color:#22C55E; }
.hist-stage-ag-carregamento { background: rgba(250,204,21,.18); color:#FEF08A; border-color:#FACC15; }
.hist-stage-deslocamento-carregado { background: rgba(132,204,22,.18); color:#BEF264; border-color:#84CC16; }
.hist-stage-ag-descarregamento { background: rgba(245,158,11,.18); color:#FCD34D; border-color:#F59E0B; }
.hist-stage-descarregando { background: rgba(249,115,22,.18); color:#FDBA74; border-color:#F97316; }
.hist-stage-deslocamento-vazio { background: rgba(56,189,248,.18); color:#BAE6FD; border-color:#38BDF8; }
.hist-stage-manutencao { background: rgba(239,68,68,.18); color:#FCA5A5; border-color:#EF4444; }
.hist-stage-default { background: rgba(148,163,184,.18); color:#CBD5E1; }

.hist-status-open { background: rgba(34,197,94,.18); color:#86EFAC; }
.hist-status-done { background: rgba(148,163,184,.16); color:#E2E8F0; border-color:rgba(226,232,240,.28); }

.hist-status-open,
.hist-status-done {
    max-width:100%;
    padding:0 8px;
    font-size:.72rem !important;
    overflow:hidden;
}

.hist-obs {
    color: #CBD5E1;
    cursor: help;
    display: -webkit-box;
    max-width: 100%;
    overflow: hidden;
    overflow-wrap: anywhere;
    word-break: break-word;
    text-overflow: ellipsis;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    line-height: 1.25;
}

.hist-table strong {
    font-weight: 800;
}

.hist-download-row {
    margin-top: 12px;
}

.hist-toolbar {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    margin: 4px 0 10px;
    color:#CBD5E1;
    font-size:.86rem;
    font-weight:700;
}

.hist-toolbar strong {
    color:#FFFFFF;
}

.hist-lead {
    display:inline-flex;
    align-items:center;
    justify-content:center;
    min-height:30px;
    min-width:92px;
    padding:0 14px;
    border-radius:999px;
    background:linear-gradient(135deg, rgba(59,130,246,.22), rgba(20,184,166,.18));
    color:#FFFFFF;
    border:1px solid rgba(96,165,250,.46);
    box-shadow:0 8px 18px rgba(2,6,23,.24);
    font-weight:850;
}

.hist-chart-card {
    background:#1E293B;
    border:1px solid #334155;
    border-radius:12px;
    padding:14px 16px 8px;
    box-shadow:0 10px 24px rgba(2,6,23,.26);
    margin-top:12px;
}

.hist-row-grid,
.hist-row-head {
    display:grid;
    grid-template-columns: 5% 9% 19% 18% 10% 10% 10% 19%;
    gap:8px;
    align-items:center;
}

.hist-row-grid > div,
.hist-row-head > div {
    min-width: 0;
}

.hist-row-grid strong {
    font-size:1.02rem;
}

.hist-row-grid .hist-badge {
    font-size:.76rem;
    min-height:32px;
    padding:0 10px;
}

.hist-row-grid .hist-time {
    font-size:.9rem;
    min-height:32px;
}

.hist-row-head {
    background:#263445;
    border:1px solid #334155;
    border-radius:12px 12px 0 0;
    padding:12px 10px;
    color:#CBD5E1;
    font-size:.74rem;
    font-weight:850;
    text-transform:uppercase;
    letter-spacing:.04em;
}

.hist-row-grid {
    min-height:58px;
    padding:9px 10px;
    border-left:1px solid #334155;
    border-right:1px solid #334155;
    border-bottom:1px solid #334155;
    background:#1E293B;
    color:#FFFFFF;
    font-size:.94rem;
    transition:background .18s ease;
}

.hist-row-grid:nth-child(even) {
    background:rgba(15,23,42,.28);
}

.hist-row-grid:hover {
    background:#263445;
}

.hist-row-grid.last {
    border-radius:0 0 12px 12px;
}

.hist-cell-center {
    text-align:center;
}

.hist-action-cell {
    display:flex;
    align-items:center;
    justify-content:center;
}

.hist-action-head {
    background:#263445;
    border:1px solid #334155;
    border-radius:12px 12px 0 0;
    padding:12px 4px;
    color:#CBD5E1;
    font-size:.74rem;
    font-weight:850;
    text-transform:uppercase;
    letter-spacing:.04em;
    text-align:center;
}

.hist-action-head + div button,
div[data-testid="column"]:last-child div[data-testid="stButton"] button {
    background:#1E293B !important;
    color:#FFFFFF !important;
    border:1px solid #334155 !important;
    box-shadow:none !important;
    font-weight:800 !important;
}

.hist-action-head + div button:hover,
div[data-testid="column"]:last-child div[data-testid="stButton"] button:hover {
    background:#2563EB !important;
    border-color:#3B82F6 !important;
    color:#FFFFFF !important;
}

div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 10px;
    border-bottom: 1px solid #334155;
    padding-top: 18px;
}

div[data-testid="stTabs"] [data-baseweb="tab"] {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 10px;
    color: #CBD5E1;
    padding: 10px 18px;
    height: auto;
    transition: background .18s ease, color .18s ease, transform .18s ease, border-color .18s ease;
}

div[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    background: #263445;
    color: #FFFFFF;
    transform: translateY(-1px);
}

div[data-testid="stTabs"] [aria-selected="true"] {
    background: #263445;
    color: #FFFFFF;
    border-color: #3B82F6;
    box-shadow: inset 0 -2px 0 #3B82F6;
}

@media (max-width: 1100px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .hist-table {
        min-width: 1280px;
    }
    .hist-table-wrap {
        overflow-x: auto;
    }
}
</style>
""", unsafe_allow_html=True)

# Menu lateral
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">🚛</div>
            <div class="sidebar-title">Gestão do<br>Transporte de Mel</div>
        </div>
        <div class="sidebar-kicker">Navegação</div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
    pagina = st.radio(
        "Menu",
        ["Painel de Operações", "Histórico"],
        key="menu",
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown(
        """
        <div class="sidebar-footer">
            <strong>Sistema de Controle</strong>
            Frotas e histórico operacional
        </div>
        """,
        unsafe_allow_html=True
    )

# FUNÇÃO AUXILIAR
def obter_cor_etapa(etapa):
    """Retorna a cor da etapa."""
    cores = {
        "Deslocamento vazio": "#38BDF8",
        "Ag. carregamento": "#FACC15",
        "Carregando": "#22C55E",
        "Deslocamento carregado": "#84CC16",
        "Ag. descarregamento": "#F59E0B",
        "Descarregando": "#F97316",
        "Manutenção": "#EF4444"
    }
    return cores.get(etapa, "#999999")

def obter_classe_cor_etapa(etapa):
    """Retorna a classe CSS para cor da etapa."""
    classes = {
        "Descarregando": "stage-color-descarregando",
        "Ag. descarregamento": "stage-color-agdescarregamento",
        "Deslocamento carregado": "stage-color-deslocamentocarregado",
        "Carregando": "stage-color-carregando",
        "Ag. carregamento": "stage-color-agcarregamento",
        "Deslocamento vazio": "stage-color-deslocamentovazio",
        "Manutenção": "stage-color-manutencao"
    }
    return classes.get(etapa, "")

def obter_ordem_etapa(etapa):
    """Retorna a ordem de prioridade da etapa."""
    ordem = {
        "Descarregando": 1,
        "Ag. descarregamento": 2,
        "Deslocamento carregado": 3,
        "Carregando": 4,
        "Ag. carregamento": 5,
        "Deslocamento vazio": 6,
        "Manutenção": 8
    }
    return ordem.get(etapa, 99)

def obter_badge_etapa(etapa):
    """Retorna HTML com badge colorido para a etapa."""
    badge_classes = {
        "Descarregando": "badge-descarregando",
        "Ag. descarregamento": "badge-agdescarregamento",
        "Deslocamento carregado": "badge-deslocamentocarregado",
        "Carregando": "badge-carregando",
        "Ag. carregamento": "badge-agcarregamento",
        "Deslocamento vazio": "badge-deslocamentovazio",
        "Manutenção": "badge-manutencao"
    }
    badge_icons = {
        "Deslocamento vazio": "🔵",
        "Ag. carregamento": "🟡",
        "Carregando": "🟢",
        "Deslocamento carregado": "🟩",
        "Ag. descarregamento": "🟠",
        "Descarregando": "🟧",
        "Manutenção": "🔴"
    }
    classe = badge_classes.get(etapa, "badge-default")
    icone = badge_icons.get(etapa, "⚪")
    return f"<span class='fleet-row-stage {classe}'>{icone} {etapa}</span>"

def obter_datetime_painel(valor):
    try:
        return datetime.fromisoformat(str(valor))
    except Exception:
        try:
            dt = pd.to_datetime(valor, errors="coerce")
            if pd.isna(dt):
                return None
            return dt.to_pydatetime()
        except Exception:
            return None

def formatar_inicio_painel(valor):
    """Exibe somente DD/MM HH:MM no painel operacional."""
    dt = obter_datetime_painel(valor)
    return dt.strftime("%d/%m %H:%M") if dt else "-"

def formatar_hora_painel(valor):
    """Exibe somente HH:MM em campos auxiliares."""
    dt = obter_datetime_painel(valor)
    return dt.strftime("%H:%M") if dt else "-"

# PAINEL DE OPERAÇÕES
if pagina == "Painel de Operações":
    st.markdown(
        """
        <div class="ops-header">
            <div class="ops-title">🚛 Painel de Operações</div>
            <div class="ops-subtitle">Monitoramento em tempo real das frotas</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Inicializar estado se não existir
    if 'frota_em_edicao' not in st.session_state:
        st.session_state.frota_em_edicao = None
    
    frotas_ativas = obter_frotas_ativas()
    frotas_manutencao = obter_frotas_em_manutencao()
    
    # Layout: Main + Sidebar de Edição - Proporção 3:1
    col_main, col_edit = st.columns([3, 1], gap="small")
    
    with col_main:
        st.markdown("<div class='ops-section-title'>Operações Ativas</div>", unsafe_allow_html=True)
        
        # Agrupar frotas por operação
        operacoes = [
            ("Figueira", "Alcoazul"),
            ("Figueira", "Generalco"),
            ("Aralco", "Alcoazul"),
            ("Aralco", "Generalco")
        ]
        
        # Mostrar operações
        for unidade_carga, unidade_descar in operacoes:
            rota_classe = f"route-{unidade_carga.lower()}-{unidade_descar.lower()}"
            frotas_operacao = frotas_ativas[
                (frotas_ativas['unidade_carregamento'] == unidade_carga) &
                (frotas_ativas['unidade_descarregamento'] == unidade_descar)
            ].sort_values('etapa_atual', key=lambda x: x.map(obter_ordem_etapa))
            
            if not frotas_operacao.empty:
                # Cabeçalho da operação com design aprimorado
                st.markdown(f"""
                    <div class="operation-box {rota_classe}">
                        <div class="operation-head">
                            <strong>🏭 {unidade_carga.upper()} → {unidade_descar.upper()}</strong>
                            <div class="operation-meta">{len(frotas_operacao)} Frota{'s' if len(frotas_operacao) > 1 else ''}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Cabeçalho da tabela com proporções fixas: 18/34/16/18/14.
                col1, col2, col3, col4, col5 = st.columns([18, 32, 16, 16, 18], gap="small")
                with col1:
                    st.markdown("<div class='ops-table-head'>Frota</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown("<div class='ops-table-head'>🔄 Etapa</div>", unsafe_allow_html=True)
                with col3:
                    st.markdown("<div class='ops-table-head center'>🕒 Início</div>", unsafe_allow_html=True)
                with col4:
                    st.markdown("<div class='ops-table-head center'>⏱ Tempo</div>", unsafe_allow_html=True)
                with col5:
                    st.markdown("<div class='ops-table-head center'>✏ Ação</div>", unsafe_allow_html=True)
                
                # Tabela compacta de frotas
                for _, frota in frotas_operacao.iterrows():
                    tempo_etapa = calcular_tempo_etapa(frota['numero'])
                    clase_cor = obter_classe_cor_etapa(frota['etapa_atual'])
                    inicio_formatado = formatar_inicio_painel(frota['inicio_etapa'])
                    badge_etapa = obter_badge_etapa(frota['etapa_atual'])
                    
                    col1, col2, col3, col4, col5 = st.columns([18, 32, 16, 16, 18], gap="small")

                    with col1:
                        st.markdown(f"<div class='fleet-row {clase_cor}'><span class='fleet-row-number'>{frota['numero']}</span></div>", unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"<div class='fleet-row stage-cell {clase_cor}'>{badge_etapa}</div>", unsafe_allow_html=True)

                    with col3:
                        st.markdown(f"<div class='fleet-row cell-center {clase_cor}'><span class='fleet-row-start'>{inicio_formatado}</span></div>", unsafe_allow_html=True)

                    with col4:
                        st.markdown(f"<div class='fleet-row cell-center {clase_cor}'><span class='fleet-row-time'>{tempo_etapa}</span></div>", unsafe_allow_html=True)

                    with col5:
                        if st.button("Editar", key=f"edit_{frota['numero']}", use_container_width=True):
                            st.session_state.frota_em_edicao = frota['numero']
                            st.rerun()
                
                st.markdown("")
        
        if frotas_ativas.empty:
            st.info("✅ Nenhuma frota ativa no momento")
        
        # Seção de Frotas em Manutenção (separada e bem dividida)
        st.markdown(
            """
            <div class="ops-maintenance-card">
                <div class="ops-maintenance-title">🔧 Manutenção</div>
            """,
            unsafe_allow_html=True
        )
        
        if not frotas_manutencao.empty:
            header_col, action_head_col = st.columns([90, 10], gap="medium")
            with header_col:
                st.markdown(
                    """
                        <div class="maintenance-grid-head">
                            <div class="ops-table-head">Frota</div>
                            <div class="ops-table-head center">Entrada</div>
                            <div class="ops-table-head center">Etapa</div>
                            <div class="ops-table-head center">Tempo</div>
                        </div>
                    """,
                    unsafe_allow_html=True
                )
            with action_head_col:
                st.markdown("<div class='ops-table-head maintenance-action-head'>Ação</div>", unsafe_allow_html=True)
            
            for _, frota in frotas_manutencao.iterrows():
                tempo_etapa = calcular_tempo_etapa(frota['numero'])
                entrada = formatar_inicio_painel(frota['data_criacao']) if frota['data_criacao'] else "-"
                badge_manutencao = obter_badge_etapa("Manutenção")
                
                row_col, action_col = st.columns([90, 10], gap="medium")
                with row_col:
                    st.markdown(
                        f"""
                        <div class="maintenance-grid-row">
                            <div class="fleet-row maintenance-cell stage-color-manutencao"><span class="fleet-row-number">{escape(str(frota['numero']))}</span></div>
                            <div class="fleet-row maintenance-cell cell-center stage-color-manutencao"><span class="fleet-row-start">{escape(str(entrada))}</span></div>
                            <div class="fleet-row maintenance-cell stage-cell stage-color-manutencao">{badge_manutencao}</div>
                            <div class="fleet-row maintenance-cell cell-center stage-color-manutencao"><span class="fleet-row-time">{escape(str(tempo_etapa))}</span></div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with action_col:
                    if st.button("Editar", key=f"edit_maint_{frota['numero']}", use_container_width=True):
                        st.session_state.frota_em_edicao = frota['numero']
                        st.rerun()
        else:
            st.markdown("<span class='ops-empty-badge'>🟢 Nenhuma frota em manutenção</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Painel lateral de edição
    with col_edit:
        st.markdown('<div class="edit-drawer">', unsafe_allow_html=True)
        
        if st.session_state.frota_em_edicao:
            frota_sel = st.session_state.frota_em_edicao
            
            # Buscar dados da frota
            if not frotas_ativas.empty:
                frota_data = frotas_ativas[frotas_ativas['numero'] == frota_sel]
                if frota_data.empty and not frotas_manutencao.empty:
                    frota_data = frotas_manutencao[frotas_manutencao['numero'] == frota_sel]
            else:
                frota_data = frotas_manutencao[frotas_manutencao['numero'] == frota_sel]
            
            if not frota_data.empty:
                frota_info = frota_data.iloc[0]
                
                st.markdown("<div class='ops-card-title'>Editar Frota</div>", unsafe_allow_html=True)
                st.markdown(f"<strong style='color: #FFFFFF;'>🚛 {frota_sel}</strong>", unsafe_allow_html=True)
                
                with st.form("form_editar_frota"):
                    st.markdown("<small style='font-weight: 700; color: #CBD5E1;'>Etapa Atual</small>", unsafe_allow_html=True)
                    etapas = [
                        "Descarregando", "Ag. descarregamento", "Deslocamento carregado",
                        "Carregando", "Ag. carregamento", "Deslocamento vazio", "Manutenção"
                    ]
                    
                    etapa_atual = st.selectbox("Etapa", etapas, 
                        index=etapas.index(frota_info['etapa_atual']) if frota_info['etapa_atual'] in etapas else 5,
                        label_visibility="collapsed")
                    
                    inicio_dt_edicao = obter_datetime_painel(frota_info['inicio_etapa']) or datetime(2026, 1, 1)
                    st.markdown("<small style='font-weight: 700; color: #CBD5E1; margin-top: 12px;'>Data de Início</small>", unsafe_allow_html=True)
                    data_inicio_etapa = st.text_input(
                        "Data de Início",
                        value=inicio_dt_edicao.strftime("%d/%m"),
                        placeholder="DD/MM",
                        label_visibility="collapsed"
                    )
                    st.markdown("<small style='font-weight: 700; color: #CBD5E1; margin-top: 12px;'>Horário de Início</small>", unsafe_allow_html=True)
                    horario = st.text_input(
                        "Horário",
                        value=inicio_dt_edicao.strftime("%H:%M"),
                        placeholder="HH:MM",
                        label_visibility="collapsed"
                    )
                    
                    st.markdown("<small style='font-weight: 700; color: #CBD5E1; margin-top: 12px;'>Unidade de Carga</small>", unsafe_allow_html=True)
                    carga = st.selectbox("Carga", ["Figueira", "Aralco"], 
                        index=["Figueira", "Aralco"].index(frota_info['unidade_carregamento']),
                        label_visibility="collapsed")
                    
                    st.markdown("<small style='font-weight: 700; color: #CBD5E1; margin-top: 12px;'>Unidade de Descarga</small>", unsafe_allow_html=True)
                    descar = st.selectbox("Descar", ["Alcoazul", "Generalco"],
                        index=["Alcoazul", "Generalco"].index(frota_info['unidade_descarregamento']),
                        label_visibility="collapsed")
                    
                    st.markdown("<small style='font-weight: 700; color: #CBD5E1; margin-top: 12px;'>Observação</small>", unsafe_allow_html=True)
                    obs = st.text_area("Obs", value="", height=60, label_visibility="collapsed")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Salvar", use_container_width=True):
                            try:
                                data_validada = datetime.strptime(f"{data_inicio_etapa.strip()}/2026", "%d/%m/%Y").date()
                                hora_validada = datetime.strptime(horario.strip(), "%H:%M").time()
                                novo_inicio_painel = datetime.combine(data_validada, hora_validada).replace(microsecond=0).isoformat()

                                # Alterar etapa
                                if etapa_atual != frota_info['etapa_atual']:
                                    alterar_etapa(frota_sel, etapa_atual)
                                
                                # Alterar data/hora de início
                                if novo_inicio_painel != inicio_dt_edicao.replace(microsecond=0).isoformat():
                                    alterar_inicio_etapa(frota_sel, novo_inicio_painel)
                                
                                # Alterar unidades
                                if carga != frota_info['unidade_carregamento'] or descar != frota_info['unidade_descarregamento']:
                                    alterar_unidades(frota_sel, carga, descar)
                                
                                st.success("✅ Alterado!", icon="✅")
                                st.session_state.frota_em_edicao = None
                                st.rerun()
                            except ValueError:
                                st.error("Informe a data como DD/MM e o horário como HH:MM.")
                    
                    with col2:
                        if st.form_submit_button("Cancelar", use_container_width=True):
                            st.session_state.frota_em_edicao = None
                            st.rerun()
                
                st.markdown("<div class='ops-card-title' style='margin-top:18px;'>Ações Rápidas</div>", unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Manutenção", use_container_width=True):
                        st.session_state.show_manut_form = True
                
                with col_b:
                    if st.button("Deletar", use_container_width=True):
                        excluir_frota(frota_sel)
                        st.success("Deletado!")
                        st.session_state.frota_em_edicao = None
                        st.rerun()
                
                # Formulário de manutenção em sessão
                if 'show_manut_form' in st.session_state and st.session_state.show_manut_form:
                    st.markdown("---")
                    st.markdown("<strong style='color: #FF4444;'>Enviar para Manutenção</strong>", unsafe_allow_html=True)
                    with st.form("form_manut"):
                        motivo = st.text_input("Motivo", label_visibility="collapsed")
                        obs = st.text_area("Observação", height=60, label_visibility="collapsed")
                        prev = st.text_input("Previsão", placeholder="HH:MM", label_visibility="collapsed")
                        
                        col_x, col_y = st.columns(2)
                        with col_x:
                            if st.form_submit_button("Enviar", use_container_width=True):
                                enviar_manutencao(frota_sel, motivo, obs, prev)
                                st.success("Enviado!")
                                st.session_state.frota_em_edicao = None
                                st.session_state.show_manut_form = False
                                st.rerun()
                        with col_y:
                            if st.form_submit_button("Cancelar", use_container_width=True):
                                st.session_state.show_manut_form = False
        else:            
            st.markdown("<div class='ops-card-title'>➕ Nova Frota</div>", unsafe_allow_html=True)
            
            with st.form("form_adicionar_frota"):
                st.markdown("<small style='font-weight: 700; color: #CBD5E1;'>Número</small>", unsafe_allow_html=True)
                numero = st.text_input("Número", placeholder="911XXX", label_visibility="collapsed")
                st.markdown("<small style='font-weight: 700; color: #CBD5E1; margin-top: 8px;'>Carga</small>", unsafe_allow_html=True)
                carga = st.selectbox("Carga", ["Figueira", "Aralco"], label_visibility="collapsed")
                st.markdown("<small style='font-weight: 700; color: #CBD5E1; margin-top: 8px;'>Descarga</small>", unsafe_allow_html=True)
                descar = st.selectbox("Descar", ["Alcoazul", "Generalco"], label_visibility="collapsed")
                
                if st.form_submit_button("➕ Adicionar Frota", use_container_width=True):
                    if numero:
                        success, msg = adicionar_frota(numero, carga, descar)
                        if success:
                            st.success(msg, icon="✅")
                            st.session_state.frota_em_edicao = None
                            st.rerun()
                        else:
                            st.error(msg)
            
            st.markdown("<div class='ops-card-title' style='margin-top:20px;'>🔧 Manutenção</div>", unsafe_allow_html=True)
            
            if not frotas_manutencao.empty:
                for _, frota_manut in frotas_manutencao.iterrows():
                    st.markdown(
                        f"<div class='ops-fleet-mini'><strong>{frota_manut['numero']}</strong><span class='fleet-row-stage badge-manutencao'>🔧 Manutenção</span></div>",
                        unsafe_allow_html=True
                    )
                with st.form("form_retorno_manut"):
                    st.markdown("<small style='font-weight: 700; color: #CBD5E1;'>Retornar Frota</small>", unsafe_allow_html=True)
                    num = st.selectbox("Frota", frotas_manutencao['numero'].tolist(), label_visibility="collapsed")
                    st.markdown("<small style='font-weight: 700; color: #CBD5E1;'>Etapa Inicial</small>", unsafe_allow_html=True)
                    etapa = st.selectbox("Etapa Inicial", 
                        ["Carregando", "Deslocamento vazio", "Deslocamento carregado"],
                        key="etapa_retorno_painel",
                        label_visibility="collapsed")
                    
                    if st.form_submit_button("↩ Retornar", use_container_width=True):
                        retornar_manutencao(num, etapa)
                        st.success("✅ Retornado!", icon="✅")
                        st.rerun()
            else:
                st.markdown("<span class='ops-empty-badge'>✅ Nenhuma frota em manutenção</span>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Botão para gerar WhatsApp (abaixo)
    st.markdown("---")
    
    # (Estilos de botão centralizados no bloco CSS principal)
    
    if st.button("📱 Gerar Situação para WhatsApp", use_container_width=True):
        frotas_ativas = obter_frotas_ativas()
        frotas_manutencao = obter_frotas_em_manutencao()
        
        operacoes = [
            ("Figueira", "Alcoazul"),
            ("Figueira", "Generalco"),
            ("Aralco", "Alcoazul"),
            ("Aralco", "Generalco")
        ]
        
        texto = "🚛 SITUAÇÃO DAS FROTAS\n\n"
        
        for unidade_carga, unidade_descar in operacoes:
            frotas_operacao = frotas_ativas[
                (frotas_ativas['unidade_carregamento'] == unidade_carga) &
                (frotas_ativas['unidade_descarregamento'] == unidade_descar)
            ].sort_values('etapa_atual', key=lambda x: x.map(obter_ordem_etapa))
            
            if not frotas_operacao.empty:
                texto += f"{unidade_carga} → {unidade_descar}\n"
                for _, frota in frotas_operacao.iterrows():
                    tempo_etapa = calcular_tempo_etapa(frota['numero'])
                    texto += f" {frota['numero']} - {frota['etapa_atual']} - {tempo_etapa}\n"
                texto += "\n"
        
        if not frotas_manutencao.empty:
            texto += "🔧 MANUTENÇÃO\n"
            for _, frota in frotas_manutencao.iterrows():
                texto += f" {frota['numero']} - {frota['motivo_manutencao']}\n"
        
        st.text_area("📋 Copie o texto abaixo:", value=texto, height=250)

# HISTÓRICO
elif pagina == "Histórico":
    def limpar_filtros_historico(data_minima, data_maxima):
        st.session_state["hist_data_inicial"] = data_minima
        st.session_state["hist_data_final"] = data_maxima
        st.session_state["hist_frota"] = []
        st.session_state["hist_operacao"] = []
        st.session_state["hist_etapa"] = []
        st.session_state["hist_situacao"] = []

    def classe_etapa_historico(etapa):
        etapa_normalizada = str(etapa or "").lower().replace(".", "").strip()
        mapa = {
            "carregando": "hist-stage-carregando",
            "ag carregamento": "hist-stage-ag-carregamento",
            "deslocamento carregado": "hist-stage-deslocamento-carregado",
            "ag descarregamento": "hist-stage-ag-descarregamento",
            "descarregando": "hist-stage-descarregando",
            "deslocamento vazio": "hist-stage-deslocamento-vazio",
            "manutencao": "hist-stage-manutencao",
            "manutenção": "hist-stage-manutencao",
        }
        return mapa.get(etapa_normalizada, "hist-stage-default")

    def icone_etapa_historico(etapa):
        etapa_normalizada = str(etapa or "").lower().replace(".", "").strip()
        mapa = {
            "deslocamento vazio": "🔵",
            "ag carregamento": "🟡",
            "carregando": "🟢",
            "deslocamento carregado": "🟩",
            "ag descarregamento": "🟠",
            "descarregando": "🟧",
            "manutencao": "🔴",
            "manutenção": "🔴",
        }
        return mapa.get(etapa_normalizada, "⚪")

    def formatar_data_historico(valor_dt, vazio="-"):
        if pd.isna(valor_dt):
            return escape(vazio)
        return valor_dt.strftime("%d/%m %H:%M")

    def classe_tempo_historico(_tempo_segundos):
        # Estrutura preparada para regras futuras de criticidade.
        return "hist-time-ok"

    def renderizar_tabela_historico(tabela):
        colunas = [
            ("ID", "5%"),
            ("Frota", "8%"),
            ("Operação", "18%"),
            ("Etapa", "16%"),
            ("Início", "10%"),
            ("Fim", "10%"),
            ("Tempo", "9%"),
            ("Situação", "12%"),
            ("Observação", "12%"),
        ]
        colunas_centralizadas = {"ID", "Frota", "Início", "Fim", "Tempo", "Situação"}
        cabecalho = "".join([
            f"<th class='{'hist-center' if titulo in colunas_centralizadas else ''}' style='width:{largura}'>{titulo}</th>"
            for titulo, largura in colunas
        ])
        linhas = []

        for _, linha in tabela.iterrows():
            etapa = str(linha["etapa"] or "")
            situacao = str(linha["situacao"] or "")
            observacao_completa = str(linha["observacao"] or "").strip()
            observacao_curta = "—" if not observacao_completa else observacao_completa[:25]
            if observacao_completa and len(observacao_completa) > 25:
                observacao_curta += "..."

            status_classe = "hist-status-open" if situacao == "Em andamento" else "hist-status-done"
            status_icone = "🟢" if situacao == "Em andamento" else "⚪"
            tempo_texto = str(linha["tempo"] or "-")

            linhas.append(
                "<tr>"
                f"<td class='hist-center'>{int(linha['id'])}</td>"
                f"<td class='hist-center'><strong>🚛 {escape(str(linha['frota_numero']))}</strong></td>"
                f"<td><span class='hist-badge hist-operation-badge'>🏭 {escape(str(linha['operacao']))}</span></td>"
                f"<td><span class='hist-badge {classe_etapa_historico(etapa)}'>{icone_etapa_historico(etapa)} {escape(etapa)}</span></td>"
                f"<td class='hist-center'>{formatar_data_historico(linha['inicio_dt'])}</td>"
                f"<td class='hist-center'>{formatar_data_historico(linha['fim_dt'])}</td>"
                f"<td class='hist-center'><span class='hist-time {classe_tempo_historico(linha['tempo_segundos'])}'>⏱ {escape(tempo_texto)}</span></td>"
                f"<td class='hist-center'><span class='hist-badge {status_classe}'>{status_icone} {escape(situacao)}</span></td>"
                f"<td><span class='hist-obs' title='{escape(observacao_completa)}'>{escape(observacao_curta)}</span></td>"
                "</tr>"
            )

        return (
            "<div class='hist-table-wrap'>"
            "<table class='hist-table'>"
            f"<thead><tr>{cabecalho}</tr></thead>"
            f"<tbody>{''.join(linhas)}</tbody>"
            "</table>"
            "</div>"
        )

    def renderizar_tabela_premium(cabecalhos, linhas):
        def classe_alinhamento(valor):
            if valor == "right":
                return "hist-right"
            if valor:
                return "hist-center"
            return ""

        header_html = "".join(
            f"<th class='{classe_alinhamento(alinhamento)}' style='width:{largura}'>{titulo}</th>"
            for titulo, largura, alinhamento in cabecalhos
        )
        body_html = "".join(
            "<tr>" + "".join(
                f"<td class='{classe_alinhamento(alinhamento)}'>{conteudo}</td>"
                for conteudo, alinhamento in linha
            ) + "</tr>"
            for linha in linhas
        )
        return (
            "<div class='hist-table-wrap'>"
            "<table class='hist-table'>"
            f"<thead><tr>{header_html}</tr></thead>"
            f"<tbody>{body_html}</tbody>"
            "</table>"
            "</div>"
        )

    def renderizar_tempo_viagem(valor):
        texto = str(valor or "").strip()
        if not texto:
            return "<span class='hist-empty-time'>—</span>"
        return f"<span class='hist-travel-time'>{escape(texto)}</span>"

    def aplicar_tema_grafico_historico(fig, altura=360, mostrar_legenda=False):
        for trace in fig.data:
            tipo_trace = getattr(trace, "type", "")

            if tipo_trace == "bar":
                trace.update(
                    textposition="outside",
                    marker_line_width=1,
                    marker_line_color="#334155"
                )
            elif tipo_trace == "box":
                trace.update(
                    boxmean=True,
                    line=dict(width=1.4),
                    marker=dict(size=5, opacity=0.82, line=dict(width=1, color="#334155"))
                )
            elif tipo_trace in {"scatter", "scattergl"}:
                trace.update(
                    line=dict(width=2.6),
                    marker=dict(size=8, line=dict(width=1, color="#334155"))
                )
            elif tipo_trace == "pie":
                trace.update(
                    textinfo="percent+label",
                    marker=dict(line=dict(width=1, color="#334155"))
                )
            else:
                try:
                    trace.update(marker=dict(line=dict(width=1, color="#334155")))
                except ValueError:
                    pass

        fig.update_layout(
            showlegend=mostrar_legenda,
            paper_bgcolor="#0F172A",
            plot_bgcolor="#0F172A",
            font=dict(color="#CBD5E1", size=14),
            title_font=dict(color="#FFFFFF", size=20),
            legend=dict(font=dict(color="#CBD5E1"), bgcolor="rgba(15,23,42,0)"),
            margin=dict(l=20, r=20, t=58, b=72),
            height=altura,
            xaxis=dict(gridcolor="#334155", zerolinecolor="#334155", tickfont=dict(color="#CBD5E1", size=13)),
            yaxis=dict(gridcolor="#334155", zerolinecolor="#334155", tickfont=dict(color="#CBD5E1", size=13)),
            hoverlabel=dict(bgcolor="#1E293B", font_color="#FFFFFF", bordercolor="#334155"),
            uniformtext_minsize=10,
            uniformtext_mode="hide",
        )
        return fig

    def calcular_indicadores_unidade(df_base, coluna_unidade, unidades, metricas):
        linhas = []
        for unidade in unidades:
            df_unidade = df_base[df_base[coluna_unidade] == unidade].copy()
            tempo_total = int(df_unidade["tempo_segundos"].dropna().sum()) if not df_unidade.empty else 0
            linha = {
                "unidade": unidade,
                "registros": int(len(df_unidade)),
                "frotas": int(df_unidade["frota_numero"].nunique()) if not df_unidade.empty else 0,
                "tempo_total": formatar_tempo(tempo_total),
            }
            for chave, etapa in metricas:
                tempos = df_unidade.loc[
                    (df_unidade["etapa"] == etapa) & df_unidade["tempo_segundos"].notna(),
                    "tempo_segundos"
                ]
                linha[chave] = formatar_tempo(int(tempos.mean())) if not tempos.empty else "—"
            linhas.append(linha)
        return linhas

    def renderizar_cards_unidade(df_base, cards_unidade):
        colunas_cards = st.columns(len(cards_unidade))
        total_historico = int(df_base["tempo_segundos"].dropna().sum()) if not df_base.empty else 0
        for coluna, (unidade, tipo, coluna_unidade) in zip(colunas_cards, cards_unidade):
            df_unidade = df_base[df_base[coluna_unidade] == unidade].copy()
            tempo_total = int(df_unidade["tempo_segundos"].dropna().sum()) if not df_unidade.empty else 0
            tempo_medio = int(df_unidade["tempo_segundos"].dropna().mean()) if not df_unidade["tempo_segundos"].dropna().empty else 0
            participacao = (tempo_total / total_historico * 100) if total_historico else 0
            classe = "unidade-carga" if tipo == "Carga" else "unidade-descarga"
            icone = "🏭" if tipo == "Carga" else "📍"
            with coluna:
                st.markdown(
                    f"""
                    <div class="hist-card hist-unit-card {classe}">
                        <div class="hist-unit-top">
                            <div>
                                <div class="hist-unit-type">{icone} {escape(tipo)}</div>
                                <div class="hist-unit-name">{escape(unidade)}</div>
                            </div>
                            <div class="hist-unit-status">🟢 Dentro do esperado</div>
                        </div>
                        <div class="hist-unit-metrics">
                            <div class="hist-unit-metric">
                                <div class="hist-unit-label">🚛 Frotas</div>
                                <div class="hist-unit-number">{df_unidade["frota_numero"].nunique()}</div>
                            </div>
                            <div class="hist-unit-metric">
                                <div class="hist-unit-label">📄 Registros</div>
                                <div class="hist-unit-number">{len(df_unidade)}</div>
                            </div>
                            <div class="hist-unit-metric">
                                <div class="hist-unit-label">⏱ Total</div>
                                <div class="hist-unit-number">{formatar_tempo(tempo_total)}</div>
                            </div>
                            <div class="hist-unit-metric">
                                <div class="hist-unit-label">⏱ Média</div>
                                <div class="hist-unit-number">{formatar_tempo(tempo_medio)}</div>
                            </div>
                            <div class="hist-unit-metric">
                                <div class="hist-unit-label">📊 Participação</div>
                                <div class="hist-unit-number">{participacao:.1f}%</div>
                            </div>
                            <div class="hist-unit-metric">
                                <div class="hist-unit-label">🚦 Status</div>
                                <div class="hist-unit-number">OK</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    def renderizar_linha_historico(linha, ultima=False):
        etapa = str(linha["etapa"] or "")
        situacao = str(linha["situacao"] or "")
        status_classe = "hist-status-open" if situacao == "Em andamento" else "hist-status-done"
        status_icone = "🟢" if situacao == "Em andamento" else "⚪"
        tempo_texto = str(linha["tempo"] or "-")
        classe_final = "hist-row-grid last" if ultima else "hist-row-grid"

        return (
            f"<div class='{classe_final}'>"
            f"<div class='hist-cell-center'><strong>{int(linha['id'])}</strong></div>"
            f"<div class='hist-cell-center'><strong>🚛 {escape(str(linha['frota_numero']))}</strong></div>"
            f"<div><span class='hist-badge hist-operation-badge'>🏭 {escape(str(linha['operacao']))}</span></div>"
            f"<div><span class='hist-badge {classe_etapa_historico(etapa)}'>{icone_etapa_historico(etapa)} {escape(etapa)}</span></div>"
            f"<div class='hist-cell-center'>{formatar_data_historico(linha['inicio_dt'])}</div>"
            f"<div class='hist-cell-center'>{formatar_data_historico(linha['fim_dt'])}</div>"
            f"<div class='hist-cell-center'><span class='hist-time {classe_tempo_historico(linha['tempo_segundos'])}'>⏱ {escape(tempo_texto)}</span></div>"
            f"<div class='hist-cell-center'><span class='hist-badge {status_classe}'>{status_icone} {escape(situacao)}</span></div>"
            "</div>"
        )

    st.markdown(
        """
        <div class="hist-header">
            <div class="hist-title">📋 Histórico de Operações</div>
            <div class="hist-subtitle">Consulta de todas as etapas registradas.</div>
        </div>
        <div class="hist-divider"></div>
        """,
        unsafe_allow_html=True
    )

    from banco import DATABASE_PATH
    import sqlite3

    conn = sqlite3.connect(DATABASE_PATH)
    df_raw = pd.read_sql_query("""
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

    if df_raw.empty:
        st.info("Nenhum histórico registrado ainda")
    else:
        # Tratamento seguro das datas, aceitando ISO com ou sem microssegundos
        df_raw["inicio_dt"] = pd.to_datetime(df_raw["inicio"], format="mixed", errors="coerce")
        df_raw["fim_dt"] = pd.to_datetime(df_raw["fim"], format="mixed", errors="coerce")
        df_raw = df_raw.dropna(subset=["inicio_dt"]).copy()

        df_raw["data"] = df_raw["inicio_dt"].dt.date
        df_raw["operacao"] = df_raw["unidade_carregamento"] + " → " + df_raw["unidade_descarregamento"]
        df_raw["tempo"] = df_raw["tempo_segundos"].apply(lambda x: formatar_tempo(x) if pd.notna(x) else "")
        df_raw["situacao"] = df_raw["fim_dt"].apply(lambda x: "Finalizada" if pd.notna(x) else "Em andamento")

        data_minima = df_raw["inicio_dt"].min().date()
        data_maxima = df_raw["inicio_dt"].max().date()

        with st.container(border=True):
            st.markdown("<div class='hist-section-title' style='margin-top:0;'>🔎 Filtros</div>", unsafe_allow_html=True)
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1, 1, 1, 1, 1, 1, 1])

            with col1:
                data_inicial = st.date_input("Data Inicial", value=data_minima, key="hist_data_inicial")

            with col2:
                data_final = st.date_input("Data Final", value=data_maxima, key="hist_data_final")

            with col3:
                frota_filtro = st.multiselect(
                    "Frota",
                    sorted(df_raw["frota_numero"].dropna().astype(str).unique()),
                    key="hist_frota"
                )

            with col4:
                operacao_filtro = st.multiselect(
                    "Operação",
                    sorted(df_raw["operacao"].dropna().astype(str).unique()),
                    key="hist_operacao"
                )

            with col5:
                etapa_filtro = st.multiselect(
                    "Etapa",
                    sorted(df_raw["etapa"].dropna().astype(str).unique()),
                    key="hist_etapa"
                )

            with col6:
                situacao_filtro = st.multiselect(
                    "Situação",
                    ["Em andamento", "Finalizada"],
                    key="hist_situacao"
                )

            with col7:
                st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
                if st.button("🔄 Atualizar", key="hist_atualizar", use_container_width=True):
                    st.rerun()

            with col8:
                st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
                st.button(
                    "🗑 Limpar filtros",
                    key="hist_limpar_filtros",
                    use_container_width=True,
                    on_click=limpar_filtros_historico,
                    args=(data_minima, data_maxima)
                )

        df_filtrado = df_raw.copy()
        df_filtrado = df_filtrado[
            (df_filtrado["data"] >= data_inicial) &
            (df_filtrado["data"] <= data_final)
        ]

        if frota_filtro:
            df_filtrado = df_filtrado[df_filtrado["frota_numero"].astype(str).isin(frota_filtro)]

        if etapa_filtro:
            df_filtrado = df_filtrado[df_filtrado["etapa"].isin(etapa_filtro)]

        if operacao_filtro:
            df_filtrado = df_filtrado[df_filtrado["operacao"].isin(operacao_filtro)]

        if situacao_filtro:
            df_filtrado = df_filtrado[df_filtrado["situacao"].isin(situacao_filtro)]

        # Cards de resumo
        total_registros = len(df_filtrado)
        total_segundos = int(df_filtrado["tempo_segundos"].dropna().sum()) if not df_filtrado.empty else 0
        media_segundos = int(df_filtrado["tempo_segundos"].dropna().mean()) if not df_filtrado["tempo_segundos"].dropna().empty else 0
        total_frotas = df_filtrado["frota_numero"].nunique() if not df_filtrado.empty else 0

        st.markdown("<div class='hist-section-title'>Resumo</div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        cards = [
            (c1, "📄", "Registros", total_registros, "Total filtrado", "registros"),
            (c2, "🚛", "Frotas", total_frotas, "Frotas distintas", "frotas"),
            (c3, "⏱", "Tempo Total", formatar_tempo(total_segundos), "Soma das etapas", "tempo-total"),
            (c4, "📈", "Tempo Médio", formatar_tempo(media_segundos), "Média por registro", "tempo-medio"),
        ]
        for coluna, icone, titulo, valor, descricao, classe in cards:
            with coluna:
                st.markdown(
                    f"""
                    <div class="hist-card {classe}">
                        <div class="hist-card-icon">{icone}</div>
                        <div class="hist-card-title">{titulo}</div>
                        <div class="hist-card-value">{valor}</div>
                        <div class="hist-card-desc">{descricao}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        tab_etapas, tab_viagens, tab_indicadores, tab_unidades = st.tabs([
            "📋 Etapas",
            "🚛 Viagens",
            "📊 Indicadores",
            "🏭 Indicadores por Unidade"
        ])

        with tab_etapas:
            st.markdown("<div class='hist-section-title'>Tabela de Etapas</div>", unsafe_allow_html=True)

            tabela_etapas = df_filtrado.copy()
            tabela_etapas["Início"] = tabela_etapas["inicio_dt"].dt.strftime("%d/%m %H:%M")
            tabela_etapas["Fim"] = tabela_etapas["fim_dt"].dt.strftime("%d/%m %H:%M")
            tabela_etapas["Fim"] = tabela_etapas["Fim"].fillna("-")
            tabela_etapas = tabela_etapas.rename(columns={
                "id": "ID",
                "frota_numero": "Frota",
                "operacao": "Operação",
                "etapa": "Etapa",
                "tempo": "Tempo",
                "situacao": "Situação"
            })

            colunas_etapas = ["ID", "Frota", "Operação", "Etapa", "Início", "Fim", "Tempo", "Situação"]

            if df_filtrado.empty:
                st.info("Nenhum registro encontrado para os filtros selecionados.")
            else:
                header_col, header_action_col = st.columns([93, 7], gap="small")
                with header_col:
                    st.markdown(
                        """
                        <div class="hist-row-head">
                            <div class="hist-cell-center">ID</div>
                            <div class="hist-cell-center">Frota</div>
                            <div>Operação</div>
                            <div>Etapa</div>
                            <div class="hist-cell-center">Início</div>
                            <div class="hist-cell-center">Fim</div>
                            <div class="hist-cell-center">Tempo</div>
                            <div class="hist-cell-center">Situação</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with header_action_col:
                    st.markdown("<div class='hist-action-head'>Ação</div>", unsafe_allow_html=True)
                total_linhas = len(df_filtrado)
                for posicao, (_, linha_hist) in enumerate(df_filtrado.iterrows(), start=1):
                    linha_col, acao_col = st.columns([93, 7], gap="small")
                    with linha_col:
                        st.markdown(renderizar_linha_historico(linha_hist, ultima=posicao == total_linhas), unsafe_allow_html=True)
                    with acao_col:
                        if st.button("Editar", key=f"hist_edit_{int(linha_hist['id'])}", help="Editar registro", use_container_width=True):
                            st.session_state["hist_registro_em_edicao"] = int(linha_hist["id"])
                            st.rerun()

            csv_etapas = tabela_etapas[colunas_etapas].to_csv(index=False, sep=";", encoding="utf-8-sig")
            st.download_button(
                "⬇️ Baixar etapas filtradas em CSV",
                data=csv_etapas,
                file_name="historico_etapas.csv",
                mime="text/csv",
                use_container_width=True
            )

            linha_id_edicao = st.session_state.get("hist_registro_em_edicao")

            if linha_id_edicao and linha_id_edicao in df_filtrado["id"].tolist():
                st.markdown("<div class='hist-section-title'>✏ Editar Registro</div>", unsafe_allow_html=True)
                with st.form("form_editar_historico"):
                    st.markdown("<div style='color:#FFFFFF;font-size:1rem;font-weight:800;margin-bottom:10px;'>✏ Editar Registro</div>", unsafe_allow_html=True)
                    linha_selecionada = df_raw[df_raw["id"] == linha_id_edicao].iloc[0]
                    inicio_dt = pd.to_datetime(linha_selecionada["inicio"], format="mixed").to_pydatetime()

                    fim_vazio = pd.isna(linha_selecionada["fim"]) or linha_selecionada["fim"] == ""
                    if fim_vazio:
                        fim_dt = datetime.now()
                    else:
                        fim_dt = pd.to_datetime(linha_selecionada["fim"], format="mixed").to_pydatetime()

                    etapas_historico = [
                        "Deslocamento vazio",
                        "Ag. carregamento",
                        "Carregando",
                        "Deslocamento carregado",
                        "Ag. descarregamento",
                        "Descarregando",
                        "Manutenção",
                    ]

                    r0, r1, r2, r3 = st.columns([0.7, 1, 1, 1])
                    with r0:
                        st.text_input("ID", value=str(linha_id_edicao), disabled=True)
                    with r1:
                        frota_editada = st.text_input("Frota", value=str(linha_selecionada["frota_numero"] or ""), key="edit_hist_frota")
                    with r2:
                        unidade_carga_editada = st.selectbox(
                            "Unidade de carregamento",
                            ["Aralco", "Figueira"],
                            index=["Aralco", "Figueira"].index(linha_selecionada["unidade_carregamento"]) if linha_selecionada["unidade_carregamento"] in ["Aralco", "Figueira"] else 0,
                            key="edit_hist_carga"
                        )
                    with r3:
                        unidade_descarga_editada = st.selectbox(
                            "Unidade de descarregamento",
                            ["Alcoazul", "Generalco"],
                            index=["Alcoazul", "Generalco"].index(linha_selecionada["unidade_descarregamento"]) if linha_selecionada["unidade_descarregamento"] in ["Alcoazul", "Generalco"] else 0,
                            key="edit_hist_descarga"
                        )

                    e1, e2, e3, e4, e5 = st.columns([1.3, 1, 1, 1, 1])

                    with e1:
                        etapa_editada = st.selectbox(
                            "Etapa",
                            etapas_historico,
                            index=etapas_historico.index(linha_selecionada["etapa"]) if linha_selecionada["etapa"] in etapas_historico else 0,
                            key="edit_hist_etapa"
                        )

                    with e2:
                        situacao_editada = st.selectbox(
                            "Situação",
                            ["Em andamento", "Finalizada"],
                            index=0 if fim_vazio else 1,
                            key="edit_hist_situacao"
                        )

                    with e3:
                        data_inicio = st.date_input("Data Início", value=inicio_dt.date(), key="edit_data_inicio")

                    with e4:
                        hora_inicio = st.time_input("Hora Início", value=inicio_dt.time().replace(microsecond=0), key="edit_hora_inicio")

                    etapa_em_aberto = situacao_editada == "Em andamento"

                    if etapa_em_aberto:
                        data_fim = None
                        hora_fim = None
                        with e5:
                            st.text_input("Fim", value="Em andamento", disabled=True)
                    else:
                        with e5:
                            data_fim = st.date_input("Data Fim", value=fim_dt.date(), key="edit_data_fim")
                        hora_fim = st.time_input("Hora Fim", value=fim_dt.time().replace(microsecond=0), key="edit_hora_fim")

                    observacao = st.text_area(
                        "Observação",
                        value=linha_selecionada["observacao"] or "",
                        height=78,
                        key="edit_obs"
                    )

                    b1, b2, b3 = st.columns([1, 1, 3])
                    with b1:
                        atualizar = st.form_submit_button("Atualizar", use_container_width=True, type="primary")
                    with b2:
                        cancelar = st.form_submit_button("Cancelar", use_container_width=True, type="secondary")

                    if cancelar:
                        st.session_state["hist_registro_em_edicao"] = None
                        st.rerun()

                    if atualizar:
                        try:
                            if not frota_editada.strip():
                                st.error("Informe a frota do registro.")
                                st.stop()

                            novo_inicio_dt = datetime.combine(data_inicio, hora_inicio).isoformat()

                            if etapa_em_aberto:
                                novo_fim_dt = None
                            else:
                                if data_fim is None or hora_fim is None:
                                    st.error("Informe data e hora de fim para registros finalizados.")
                                    st.stop()
                                fim_combinado = datetime.combine(data_fim, hora_fim)
                                inicio_combinado = datetime.combine(data_inicio, hora_inicio)
                                if fim_combinado < inicio_combinado:
                                    st.error("Tempo negativo não permitido. O fim deve ser maior ou igual ao início.")
                                    st.stop()
                                novo_fim_dt = fim_combinado.isoformat()

                            success, msg = atualizar_historico_linha(
                                linha_id_edicao,
                                novo_inicio_dt,
                                novo_fim_dt,
                                observacao,
                                frota_numero=frota_editada.strip(),
                                unidade_carregamento=unidade_carga_editada,
                                unidade_descarregamento=unidade_descarga_editada,
                                etapa=etapa_editada
                            )

                            if success:
                                st.session_state["hist_registro_em_edicao"] = None
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                        except Exception as e:
                            st.error(f"Erro: {str(e)}")

        with tab_viagens:
            st.subheader("Viagens Consolidadas")
            st.caption("Cada linha consolida os tempos por frota e operação. As etapas continuam registradas isoladamente no histórico.")

            etapas_oficiais = [
                "Deslocamento vazio",
                "Ag. carregamento",
                "Carregando",
                "Deslocamento carregado",
                "Ag. descarregamento",
                "Descarregando"
            ]

            df_base_viagens = df_filtrado[
                df_filtrado["etapa"].isin(etapas_oficiais) &
                df_filtrado["viagem_id"].notna()
            ].copy()

            if df_base_viagens.empty:
                st.info("Nenhuma etapa operacional encontrada para consolidar viagens.")
            else:
                # Consolidação por viagem real. A etapa permanece isolada no histórico;
                # aqui apenas somamos tempos das etapas pertencentes ao mesmo viagem_id.
                df_base_viagens["viagem_id"] = df_base_viagens["viagem_id"].astype(int)
                df_base_viagens["tempo_consolidado"] = df_base_viagens["tempo_segundos"]
                etapas_abertas = df_base_viagens["tempo_consolidado"].isna() & df_base_viagens["fim_dt"].isna()
                if etapas_abertas.any():
                    agora_hist = pd.Timestamp.now()
                    tempo_em_aberto = (
                        agora_hist - df_base_viagens.loc[etapas_abertas, "inicio_dt"]
                    ).dt.total_seconds().clip(lower=0).astype(int)
                    df_base_viagens.loc[etapas_abertas, "tempo_consolidado"] = tempo_em_aberto
                df_base_viagens["tempo_consolidado"] = df_base_viagens["tempo_consolidado"].fillna(0)

                tabela_pivot = pd.pivot_table(
                    df_base_viagens,
                    index=["viagem_id", "frota_numero", "operacao"],
                    columns="etapa",
                    values="tempo_consolidado",
                    aggfunc="sum",
                    fill_value=0
                ).reset_index()

                for etapa in etapas_oficiais:
                    if etapa not in tabela_pivot.columns:
                        tabela_pivot[etapa] = 0

                tabela_pivot["Lead Time"] = tabela_pivot[etapas_oficiais].sum(axis=1)

                resumo_viagens = (
                    df_base_viagens.groupby(["viagem_id", "frota_numero", "operacao"], as_index=False)
                    .agg(
                        inicio_viagem=("inicio_dt", "min"),
                        fim_viagem=("fim_dt", "max")
                    )
                )

                tabela_pivot = tabela_pivot.merge(
                    resumo_viagens,
                    on=["viagem_id", "frota_numero", "operacao"],
                    how="left"
                )

                tabela_viagens = tabela_pivot.copy()
                tabela_viagens["Data"] = pd.to_datetime(tabela_viagens["inicio_viagem"]).dt.strftime("%d/%m")
                tabela_viagens = tabela_viagens.rename(columns={
                    "frota_numero": "Frota",
                    "operacao": "Operação"
                })

                for etapa in etapas_oficiais:
                    tabela_viagens[etapa] = tabela_viagens[etapa].apply(lambda x: formatar_tempo(x) if x else "")

                tabela_viagens["Lead Time"] = tabela_viagens["Lead Time"].apply(lambda x: formatar_tempo(x) if x else "")

                colunas_viagens = ["Data", "Frota", "Operação"] + etapas_oficiais + ["Lead Time"]

                total_viagens = len(tabela_viagens)
                tb1, tb2, tb3, tb4 = st.columns([2, 1, 1, 1])
                with tb1:
                    st.markdown(
                        f"<div class='hist-toolbar'><span><strong>{total_viagens}</strong> viagens consolidadas</span></div>",
                        unsafe_allow_html=True
                    )
                with tb2:
                    page_size = st.selectbox("Por página", [5, 10, 15, 20], index=1, key="hist_viagens_page_size")

                total_paginas = max(1, (total_viagens + page_size - 1) // page_size)
                st.session_state["hist_viagens_page"] = min(st.session_state.get("hist_viagens_page", 1), total_paginas)

                with tb3:
                    st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
                    if st.button("◀", key="hist_viagens_prev", use_container_width=True):
                        st.session_state["hist_viagens_page"] = max(1, st.session_state["hist_viagens_page"] - 1)
                        st.rerun()
                with tb4:
                    st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
                    if st.button("▶", key="hist_viagens_next", use_container_width=True):
                        st.session_state["hist_viagens_page"] = min(total_paginas, st.session_state["hist_viagens_page"] + 1)
                        st.rerun()

                pagina_atual = st.session_state.get("hist_viagens_page", 1)
                inicio_pagina = (pagina_atual - 1) * page_size
                fim_pagina = inicio_pagina + page_size
                tabela_viagens_pagina = tabela_viagens[colunas_viagens].iloc[inicio_pagina:fim_pagina]

                st.markdown(
                    f"<div class='hist-toolbar'><span>Página <strong>{pagina_atual}</strong> de <strong>{total_paginas}</strong></span></div>",
                    unsafe_allow_html=True
                )

                headers_viagens = [
                    ("Data", "6%", True),
                    ("Frota", "7%", True),
                    ("Operação", "18%", False),
                    ("Desloc. vazio", "9%", True),
                    ("Ag. carreg.", "9%", True),
                    ("Carregando", "8%", True),
                    ("Desloc. carregado", "11%", True),
                    ("Ag. descarreg.", "10%", True),
                    ("Descarregando", "9%", True),
                    ("Lead Time", "13%", True),
                ]
                linhas_viagens = []
                for _, row in tabela_viagens_pagina.iterrows():
                    linhas_viagens.append([
                        (escape(str(row["Data"])), True),
                        (f"<strong>🚛 {escape(str(row['Frota']))}</strong>", True),
                        (f"<span class='hist-badge hist-operation-badge'>🏭 {escape(str(row['Operação']))}</span>", False),
                        (renderizar_tempo_viagem(row["Deslocamento vazio"]), True),
                        (renderizar_tempo_viagem(row["Ag. carregamento"]), True),
                        (renderizar_tempo_viagem(row["Carregando"]), True),
                        (renderizar_tempo_viagem(row["Deslocamento carregado"]), True),
                        (renderizar_tempo_viagem(row["Ag. descarregamento"]), True),
                        (renderizar_tempo_viagem(row["Descarregando"]), True),
                        (f"<span class='hist-lead'>{escape(str(row['Lead Time'] or '—'))}</span>", True),
                    ])

                st.markdown(renderizar_tabela_premium(headers_viagens, linhas_viagens), unsafe_allow_html=True)

                csv_viagens = tabela_viagens[colunas_viagens].to_csv(index=False, sep=";", encoding="utf-8-sig")
                st.download_button(
                    "⬇️ Baixar viagens consolidadas em CSV",
                    data=csv_viagens,
                    file_name="historico_viagens.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        with tab_indicadores:
            st.markdown("<div class='hist-section-title'>Indicadores do Histórico</div>", unsafe_allow_html=True)

            df_ind = df_filtrado[df_filtrado["tempo_segundos"].notna()].copy()

            if df_ind.empty:
                st.info("Ainda não há tempos finalizados para gerar indicadores.")
            else:
                ordem_etapas_indicadores = [
                    "Deslocamento vazio",
                    "Ag. carregamento",
                    "Carregando",
                    "Deslocamento carregado",
                    "Ag. descarregamento",
                    "Descarregando",
                    "Manutenção",
                ]
                mapa_cores_etapas = {etapa: obter_cor_etapa(etapa) for etapa in ordem_etapas_indicadores}

                tempo_por_etapa = (
                    df_ind.groupby("etapa", as_index=False)
                    .agg(
                        tempo_medio=("tempo_segundos", "mean"),
                        quantidade=("id", "count"),
                        tempo_total=("tempo_segundos", "sum")
                    )
                )
                tempo_por_etapa["ordem"] = tempo_por_etapa["etapa"].apply(
                    lambda etapa: ordem_etapas_indicadores.index(etapa) if etapa in ordem_etapas_indicadores else 99
                )
                tempo_por_etapa = tempo_por_etapa.sort_values(["ordem", "etapa"])
                tempo_por_etapa["Tempo Médio"] = tempo_por_etapa["tempo_medio"].apply(formatar_tempo)
                tempo_por_etapa["Tempo Total"] = tempo_por_etapa["tempo_total"].apply(formatar_tempo)
                total_tempo_ind = float(tempo_por_etapa["tempo_total"].sum())
                tempo_por_etapa["Percentual"] = tempo_por_etapa["tempo_total"].apply(
                    lambda valor: (valor / total_tempo_ind * 100) if total_tempo_ind else 0
                )
                tempo_por_etapa["Percentual Texto"] = tempo_por_etapa["Percentual"].apply(lambda valor: f"{valor:.1f}%")
                tempo_por_etapa = tempo_por_etapa.rename(columns={"etapa": "Etapa", "quantidade": "Quantidade"})

                etapas_viagem_ind = [
                    "Deslocamento vazio",
                    "Ag. carregamento",
                    "Carregando",
                    "Deslocamento carregado",
                    "Ag. descarregamento",
                    "Descarregando",
                ]
                df_viagens_ind = df_filtrado[
                    df_filtrado["etapa"].isin(etapas_viagem_ind) &
                    df_filtrado["viagem_id"].notna()
                ].copy()
                tabela_viagens_ind = pd.DataFrame()
                if not df_viagens_ind.empty:
                    df_viagens_ind["viagem_id"] = df_viagens_ind["viagem_id"].astype(int)
                    tabela_viagens_ind = pd.pivot_table(
                        df_viagens_ind,
                        index=["viagem_id", "frota_numero", "operacao"],
                        columns="etapa",
                        values="tempo_segundos",
                        aggfunc="sum",
                        fill_value=0
                    ).reset_index()
                    for etapa in etapas_viagem_ind:
                        if etapa not in tabela_viagens_ind.columns:
                            tabela_viagens_ind[etapa] = 0
                    tabela_viagens_ind["Lead Time"] = tabela_viagens_ind[etapas_viagem_ind].sum(axis=1)

                tempo_por_operacao = (
                    df_ind.groupby("operacao", as_index=False)
                    .agg(tempo_medio=("tempo_segundos", "mean"), quantidade=("id", "count"))
                    .sort_values("tempo_medio", ascending=False)
                )
                tempo_por_operacao["Tempo Médio"] = tempo_por_operacao["tempo_medio"].apply(formatar_tempo)

                if not tabela_viagens_ind.empty:
                    viagens_por_operacao = (
                        tabela_viagens_ind.groupby("operacao", as_index=False)
                        .agg(viagens=("frota_numero", "count"), lead_time_medio=("Lead Time", "mean"))
                        .sort_values("operacao")
                    )
                    viagens_por_operacao["Lead Time Médio"] = viagens_por_operacao["lead_time_medio"].apply(formatar_tempo)
                else:
                    viagens_por_operacao = pd.DataFrame(columns=["operacao", "viagens", "lead_time_medio", "Lead Time Médio"])

                df_ag_carregamento = df_ind[df_ind["etapa"] == "Ag. carregamento"].copy()
                df_ag_descarregamento = df_ind[df_ind["etapa"] == "Ag. descarregamento"].copy()
                df_esperas = df_ind[df_ind["etapa"].isin(["Ag. carregamento", "Ag. descarregamento"])].copy()

                if not df_esperas.empty:
                    idx_etapa_critica = df_esperas["tempo_segundos"].idxmax()
                    linha_etapa_critica = df_esperas.loc[idx_etapa_critica]
                    etapa_critica_valor = str(linha_etapa_critica["etapa"])
                    etapa_critica_tempo = formatar_tempo(int(linha_etapa_critica["tempo_segundos"]))
                    etapa_critica_qtd = len(df_esperas[df_esperas["etapa"] == etapa_critica_valor])
                else:
                    etapa_critica_valor = "Sem dados"
                    etapa_critica_tempo = "Sem dados"
                    etapa_critica_qtd = 0

                if not df_ag_carregamento.empty:
                    idx_maior_ag_carga = df_ag_carregamento["tempo_segundos"].idxmax()
                    maior_ag_carga = df_ag_carregamento.loc[idx_maior_ag_carga]
                    maior_ag_carga_tempo = formatar_tempo(int(maior_ag_carga["tempo_segundos"]))
                    maior_ag_carga_operacao = str(maior_ag_carga["operacao"])
                    maior_ag_carga_frota = str(maior_ag_carga["frota_numero"])
                else:
                    maior_ag_carga_tempo = "Sem dados"
                    maior_ag_carga_operacao = "Sem dados"
                    maior_ag_carga_frota = "Sem dados"

                if not df_ag_descarregamento.empty:
                    idx_maior_ag_descarga = df_ag_descarregamento["tempo_segundos"].idxmax()
                    maior_ag_descarga = df_ag_descarregamento.loc[idx_maior_ag_descarga]
                    maior_ag_descarga_tempo = formatar_tempo(int(maior_ag_descarga["tempo_segundos"]))
                    maior_ag_descarga_operacao = str(maior_ag_descarga["operacao"])
                    maior_ag_descarga_frota = str(maior_ag_descarga["frota_numero"])
                else:
                    maior_ag_descarga_tempo = "Sem dados"
                    maior_ag_descarga_operacao = "Sem dados"
                    maior_ag_descarga_frota = "Sem dados"

                if not df_esperas.empty:
                    espera_por_operacao = (
                        df_esperas.groupby("operacao", as_index=False)
                        .agg(tempo_medio=("tempo_segundos", "mean"), viagens=("frota_numero", "count"))
                        .sort_values("tempo_medio", ascending=False)
                    )
                    operacao_critica = espera_por_operacao.iloc[0]
                    operacao_critica_valor = str(operacao_critica["operacao"])
                    operacao_critica_tempo = formatar_tempo(int(operacao_critica["tempo_medio"]))
                    operacao_critica_viagens = int(operacao_critica["viagens"])
                else:
                    operacao_critica_valor = "Sem dados"
                    operacao_critica_tempo = "Sem dados"
                    operacao_critica_viagens = 0

                total_ag_carga = int(df_ag_carregamento["tempo_segundos"].sum()) if not df_ag_carregamento.empty else 0
                total_ag_descarga = int(df_ag_descarregamento["tempo_segundos"].sum()) if not df_ag_descarregamento.empty else 0
                total_ag_carga_texto = formatar_tempo(total_ag_carga) if total_ag_carga else "Sem dados"
                total_ag_descarga_texto = formatar_tempo(total_ag_descarga) if total_ag_descarga else "Sem dados"

                maior_ag_carga_desc = (
                    f"{escape(maior_ag_carga_operacao)}<br>Frota {escape(maior_ag_carga_frota)}"
                    if not df_ag_carregamento.empty else "Sem dados"
                )
                maior_ag_descarga_desc = (
                    f"{escape(maior_ag_descarga_operacao)}<br>Frota {escape(maior_ag_descarga_frota)}"
                    if not df_ag_descarregamento.empty else "Sem dados"
                )

                k1, k2, k3, k4 = st.columns(4)
                cards_ind = [
                    (k1, "🚦", "Etapa Crítica", etapa_critica_valor, f"⏱ {etapa_critica_tempo}<br>{etapa_critica_qtd} ocorrências", f"Total espera: {total_ag_carga_texto if etapa_critica_valor == 'Ag. carregamento' else total_ag_descarga_texto}", "tempo-medio"),
                    (k2, "🏭", "Operação Crítica", operacao_critica_valor, f"⏱ {operacao_critica_tempo}<br>🚛 {operacao_critica_viagens} viagens", f"Total esperas: {formatar_tempo(total_ag_carga + total_ag_descarga) if (total_ag_carga + total_ag_descarga) else 'Sem dados'}", "frotas"),
                    (k3, "🟡", "Maior Ag. carregamento", f"⏱ {maior_ag_carga_tempo}", maior_ag_carga_desc, f"Total Ag. carreg.: {total_ag_carga_texto}", "tempo-total"),
                    (k4, "🟣", "Maior Ag. descarregamento", f"⏱ {maior_ag_descarga_tempo}", maior_ag_descarga_desc, f"Total Ag. descarreg.: {total_ag_descarga_texto}", "registros"),
                ]
                for coluna, icone, titulo, valor, descricao, total_card, classe in cards_ind:
                    with coluna:
                        st.markdown(
                            f"""
                            <div class="hist-card hist-kpi-card {classe}">
                                <div class="hist-card-icon">{icone}</div>
                                <div class="hist-card-title">{titulo}</div>
                                <div class="hist-card-value">{escape(str(valor))}</div>
                                <div class="hist-card-detail">{descricao}</div>
                                <div class="hist-kpi-total">⏱ {escape(str(total_card))}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                ac1, ac2, ac3 = st.columns([1, 1, 1])
                with ac1:
                    st.download_button(
                        "⬇ Exportar",
                        data=tempo_por_etapa[["Etapa", "Tempo Médio", "Tempo Total", "Quantidade", "Percentual Texto"]].to_csv(index=False, sep=";", encoding="utf-8-sig"),
                        file_name="indicadores_historico.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                with ac2:
                    if st.button("🔄 Atualizar", key="hist_ind_atualizar", use_container_width=True):
                        st.rerun()
                with ac3:
                    if st.button("⛶ Expandir", key="hist_ind_expandir", use_container_width=True):
                        st.session_state["hist_ind_expandido"] = not st.session_state.get("hist_ind_expandido", False)
                        st.rerun()

                st.markdown("<div class='hist-section-title'>Resumo por Etapa</div>", unsafe_allow_html=True)
                headers_ind = [
                    ("Etapa", "42%", False),
                    ("⏱ Tempo Médio", "20%", "right"),
                    ("Σ Tempo Total", "20%", "right"),
                    ("# Qtd.", "10%", "right"),
                    ("% Tempo", "8%", "right"),
                ]
                linhas_ind = []
                for _, row in tempo_por_etapa.iterrows():
                    etapa_nome = str(row["Etapa"])
                    linhas_ind.append([
                        (f"<span class='hist-badge {classe_etapa_historico(etapa_nome)}'>{icone_etapa_historico(etapa_nome)} {escape(etapa_nome)}</span>", False),
                        (f"<span class='hist-time hist-time-ok'>⏱ {escape(str(row['Tempo Médio']))}</span>", "right"),
                        (f"<strong>{escape(str(row['Tempo Total']))}</strong>", "right"),
                        (f"<strong>{int(row['Quantidade'])}</strong>", "right"),
                        (f"<strong>{escape(str(row['Percentual Texto']))}</strong>", "right"),
                    ])
                st.markdown(renderizar_tabela_premium(headers_ind, linhas_ind), unsafe_allow_html=True)

                altura_grafico = 500 if st.session_state.get("hist_ind_expandido", False) else 360
                chart_col1, chart_col2 = st.columns(2, gap="large")
                with chart_col1:
                    fig_media_etapa = px.bar(
                        tempo_por_etapa,
                        x="Etapa",
                        y="tempo_medio",
                        color="Etapa",
                        text="Tempo Médio",
                        title="Tempo médio por etapa",
                        color_discrete_map=mapa_cores_etapas,
                        hover_data={"Tempo Médio": True, "Quantidade": True, "tempo_medio": False}
                    )
                    fig_media_etapa.update_yaxes(title="Tempo médio (s)")
                    aplicar_tema_grafico_historico(fig_media_etapa, altura=altura_grafico)
                    st.plotly_chart(fig_media_etapa, use_container_width=True)

                with chart_col2:
                    fig_qtd_etapa = px.bar(
                        tempo_por_etapa,
                        x="Etapa",
                        y="Quantidade",
                        color="Etapa",
                        text="Quantidade",
                        title="Quantidade de ocorrências por etapa",
                        color_discrete_map=mapa_cores_etapas,
                        hover_data={"Tempo Médio": True, "Tempo Total": True}
                    )
                    fig_qtd_etapa.update_yaxes(title="Ocorrências")
                    aplicar_tema_grafico_historico(fig_qtd_etapa, altura=altura_grafico)
                    st.plotly_chart(fig_qtd_etapa, use_container_width=True)

                chart_col3, chart_col4 = st.columns(2, gap="large")
                with chart_col3:
                    fig_percentual = px.bar(
                        tempo_por_etapa.sort_values("Percentual", ascending=True),
                        x="Percentual",
                        y="Etapa",
                        orientation="h",
                        color="Etapa",
                        text="Percentual Texto",
                        title="Percentual do tempo gasto em cada etapa",
                        color_discrete_map=mapa_cores_etapas,
                        hover_data={"Tempo Total": True, "Tempo Médio": True, "Percentual": ":.2f"}
                    )
                    fig_percentual.update_xaxes(title="% do tempo total")
                    fig_percentual.update_yaxes(title="")
                    aplicar_tema_grafico_historico(fig_percentual, altura=altura_grafico)
                    st.plotly_chart(fig_percentual, use_container_width=True)

                with chart_col4:
                    fig_media_operacao = px.bar(
                        tempo_por_operacao,
                        x="operacao",
                        y="tempo_medio",
                        color="operacao",
                        text="Tempo Médio",
                        title="Tempo médio por operação",
                        color_discrete_sequence=["#3B82F6", "#14B8A6", "#8B5CF6", "#EAB308"],
                        hover_data={"Tempo Médio": True, "quantidade": True, "tempo_medio": False}
                    )
                    fig_media_operacao.update_xaxes(title="")
                    fig_media_operacao.update_yaxes(title="Tempo médio (s)")
                    aplicar_tema_grafico_historico(fig_media_operacao, altura=altura_grafico)
                    st.plotly_chart(fig_media_operacao, use_container_width=True)

                chart_col5, chart_col6 = st.columns(2, gap="large")
                with chart_col5:
                    fig_qtd_operacao = px.bar(
                        viagens_por_operacao,
                        x="operacao",
                        y="viagens",
                        color="operacao",
                        text="viagens",
                        title="Quantidade de viagens por operação",
                        color_discrete_sequence=["#3B82F6", "#14B8A6", "#8B5CF6", "#EAB308"],
                        hover_data={"viagens": True}
                    )
                    fig_qtd_operacao.update_xaxes(title="")
                    fig_qtd_operacao.update_yaxes(title="Viagens")
                    aplicar_tema_grafico_historico(fig_qtd_operacao, altura=altura_grafico)
                    st.plotly_chart(fig_qtd_operacao, use_container_width=True)

                with chart_col6:
                    fig_lead_operacao = px.bar(
                        viagens_por_operacao,
                        x="operacao",
                        y="lead_time_medio",
                        color="operacao",
                        text="Lead Time Médio",
                        title="Lead Time médio por operação",
                        color_discrete_sequence=["#3B82F6", "#14B8A6", "#8B5CF6", "#EAB308"],
                        hover_data={"Lead Time Médio": True, "viagens": True, "lead_time_medio": False}
                    )
                    fig_lead_operacao.update_xaxes(title="")
                    fig_lead_operacao.update_yaxes(title="Lead Time médio (s)")
                    aplicar_tema_grafico_historico(fig_lead_operacao, altura=altura_grafico)
                    st.plotly_chart(fig_lead_operacao, use_container_width=True)

        with tab_unidades:
            st.markdown("<div class='hist-section-title'>Indicadores por Unidade</div>", unsafe_allow_html=True)
            st.caption("Visão executiva das unidades sobre o histórico filtrado, separando carga e descarga para leitura operacional rápida.")

            df_unidades = df_filtrado[df_filtrado["tempo_segundos"].notna()].copy()

            if df_unidades.empty:
                st.info("Ainda não há tempos finalizados para gerar indicadores por unidade.")
            else:
                unidades_carga = ["Aralco", "Figueira"]
                unidades_descarga = ["Alcoazul", "Generalco"]
                etapas_lead_unidade = [
                    "Deslocamento vazio",
                    "Ag. carregamento",
                    "Carregando",
                    "Deslocamento carregado",
                    "Ag. descarregamento",
                    "Descarregando",
                ]

                df_carga_eventos = df_unidades[df_unidades["unidade_carregamento"].isin(unidades_carga)].copy()
                df_carga_eventos["unidade"] = df_carga_eventos["unidade_carregamento"]
                df_carga_eventos["grupo"] = "Carga"

                df_descarga_eventos = df_unidades[df_unidades["unidade_descarregamento"].isin(unidades_descarga)].copy()
                df_descarga_eventos["unidade"] = df_descarga_eventos["unidade_descarregamento"]
                df_descarga_eventos["grupo"] = "Descarga"

                df_eventos_unidade = pd.concat([df_carga_eventos, df_descarga_eventos], ignore_index=True)

                if not df_eventos_unidade.empty:
                    resumo_unidades = (
                        df_eventos_unidade.groupby(["grupo", "unidade"], as_index=False)
                        .agg(
                            tempo_total=("tempo_segundos", "sum"),
                            tempo_medio=("tempo_segundos", "mean"),
                            registros=("id", "count"),
                            frotas=("frota_numero", "nunique")
                        )
                    )
                else:
                    resumo_unidades = pd.DataFrame(columns=["grupo", "unidade", "tempo_total", "tempo_medio", "registros", "frotas"])

                total_eventos_unidade = float(resumo_unidades["tempo_total"].sum()) if not resumo_unidades.empty else 0
                resumo_unidades["participacao"] = resumo_unidades["tempo_total"].apply(
                    lambda valor: (valor / total_eventos_unidade * 100) if total_eventos_unidade else 0
                )
                resumo_unidades["Tempo Total"] = resumo_unidades["tempo_total"].apply(lambda valor: formatar_tempo(int(valor)))
                resumo_unidades["Tempo Médio"] = resumo_unidades["tempo_medio"].apply(lambda valor: formatar_tempo(int(valor)) if pd.notna(valor) else "—")
                resumo_unidades["Participação"] = resumo_unidades["participacao"].apply(lambda valor: f"{valor:.1f}%")

                viagens_unidade = pd.DataFrame(columns=["grupo", "unidade", "viagens", "lead_time_medio", "Lead Time Médio"])
                df_lead_unidade = df_unidades[
                    df_unidades["etapa"].isin(etapas_lead_unidade) &
                    df_unidades["viagem_id"].notna()
                ].copy()
                if not df_lead_unidade.empty:
                    df_lead_unidade["viagem_id"] = df_lead_unidade["viagem_id"].astype(int)
                    pivot_unidade = pd.pivot_table(
                        df_lead_unidade,
                        index=["viagem_id", "frota_numero", "operacao", "unidade_carregamento", "unidade_descarregamento"],
                        columns="etapa",
                        values="tempo_segundos",
                        aggfunc="sum",
                        fill_value=0
                    ).reset_index()
                    for etapa in etapas_lead_unidade:
                        if etapa not in pivot_unidade.columns:
                            pivot_unidade[etapa] = 0
                    pivot_unidade["Lead Time"] = pivot_unidade[etapas_lead_unidade].sum(axis=1)

                    viagens_carga = pivot_unidade[pivot_unidade["unidade_carregamento"].isin(unidades_carga)].copy()
                    viagens_carga["unidade"] = viagens_carga["unidade_carregamento"]
                    viagens_carga["grupo"] = "Carga"

                    viagens_descarga = pivot_unidade[pivot_unidade["unidade_descarregamento"].isin(unidades_descarga)].copy()
                    viagens_descarga["unidade"] = viagens_descarga["unidade_descarregamento"]
                    viagens_descarga["grupo"] = "Descarga"

                    viagens_eventos = pd.concat([viagens_carga, viagens_descarga], ignore_index=True)
                    if not viagens_eventos.empty:
                        viagens_unidade = (
                            viagens_eventos.groupby(["grupo", "unidade"], as_index=False)
                            .agg(viagens=("frota_numero", "count"), lead_time_medio=("Lead Time", "mean"))
                        )
                        viagens_unidade["Lead Time Médio"] = viagens_unidade["lead_time_medio"].apply(
                            lambda valor: formatar_tempo(int(valor)) if pd.notna(valor) else "—"
                        )

                resumo_unidades = resumo_unidades.merge(
                    viagens_unidade[["grupo", "unidade", "viagens", "lead_time_medio", "Lead Time Médio"]],
                    how="left",
                    on=["grupo", "unidade"]
                )
                resumo_unidades["viagens"] = resumo_unidades["viagens"].fillna(0).astype(int)
                resumo_unidades["lead_time_medio"] = resumo_unidades["lead_time_medio"].fillna(0)
                resumo_unidades["Lead Time Médio"] = resumo_unidades["Lead Time Médio"].fillna("—")

                maior_tempo = resumo_unidades.sort_values("tempo_total", ascending=False).iloc[0]
                maior_volume = resumo_unidades.sort_values("registros", ascending=False).iloc[0]
                mais_frotas = resumo_unidades.sort_values("frotas", ascending=False).iloc[0]
                melhor_media = resumo_unidades[resumo_unidades["registros"] > 0].sort_values("tempo_medio", ascending=True).iloc[0]

                st.markdown("<div class='hist-section-title'>Visão Executiva</div>", unsafe_allow_html=True)
                ex1, ex2, ex3, ex4 = st.columns(4)
                insights = [
                    (ex1, "Maior tempo acumulado", maior_tempo["unidade"], maior_tempo["Tempo Total"]),
                    (ex2, "Maior volume", maior_volume["unidade"], f"{int(maior_volume['registros'])} registros"),
                    (ex3, "Mais frotas", mais_frotas["unidade"], f"{int(mais_frotas['frotas'])} frotas"),
                    (ex4, "Melhor média", melhor_media["unidade"], melhor_media["Tempo Médio"]),
                ]
                for coluna, titulo, valor, desc in insights:
                    with coluna:
                        st.markdown(
                            f"""
                            <div class="hist-insight-card">
                                <div class="hist-insight-title">{escape(titulo)}</div>
                                <div class="hist-insight-value">{escape(str(valor))}</div>
                                <div class="hist-insight-desc">{escape(str(desc))}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                st.markdown("<div class='hist-section-title'>Cards por Unidade</div>", unsafe_allow_html=True)
                renderizar_cards_unidade(
                    df_unidades,
                    [
                        ("Aralco", "Carga", "unidade_carregamento"),
                        ("Figueira", "Carga", "unidade_carregamento"),
                        ("Alcoazul", "Descarga", "unidade_descarregamento"),
                        ("Generalco", "Descarga", "unidade_descarregamento"),
                    ]
                )

                st.markdown("<div class='hist-section-title'>Comparação Operacional</div>", unsafe_allow_html=True)
                comp_col1, comp_col2 = st.columns(2, gap="large")

                def renderizar_comparativo(titulo, unidade_a, unidade_b, grupo):
                    linhas = resumo_unidades[resumo_unidades["grupo"] == grupo].set_index("unidade")

                    def valor_unidade(unidade, campo, vazio="—"):
                        if unidade not in linhas.index:
                            return vazio
                        valor = linhas.loc[unidade, campo]
                        return valor

                    return f"""
                    <div class="hist-compare-card">
                        <div class="hist-compare-title">{escape(titulo)}</div>
                        <div class="hist-compare-grid">
                            <div class="hist-compare-side">
                                <div class="hist-unit-name">{escape(unidade_a)}</div>
                                <div class="hist-card-desc">Tempo médio: <strong>{escape(str(valor_unidade(unidade_a, 'Tempo Médio')))}</strong></div>
                                <div class="hist-card-desc">Viagens: <strong>{int(valor_unidade(unidade_a, 'viagens', 0))}</strong></div>
                                <div class="hist-card-desc">Frotas: <strong>{int(valor_unidade(unidade_a, 'frotas', 0))}</strong></div>
                                <div class="hist-card-desc">Lead Time: <strong>{escape(str(valor_unidade(unidade_a, 'Lead Time Médio')))}</strong></div>
                            </div>
                            <div class="hist-compare-vs">VS</div>
                            <div class="hist-compare-side">
                                <div class="hist-unit-name">{escape(unidade_b)}</div>
                                <div class="hist-card-desc">Tempo médio: <strong>{escape(str(valor_unidade(unidade_b, 'Tempo Médio')))}</strong></div>
                                <div class="hist-card-desc">Viagens: <strong>{int(valor_unidade(unidade_b, 'viagens', 0))}</strong></div>
                                <div class="hist-card-desc">Frotas: <strong>{int(valor_unidade(unidade_b, 'frotas', 0))}</strong></div>
                                <div class="hist-card-desc">Lead Time: <strong>{escape(str(valor_unidade(unidade_b, 'Lead Time Médio')))}</strong></div>
                            </div>
                        </div>
                    </div>
                    """

                with comp_col1:
                    st.markdown(renderizar_comparativo("Carga: Aralco vs Figueira", "Aralco", "Figueira", "Carga"), unsafe_allow_html=True)
                with comp_col2:
                    st.markdown(renderizar_comparativo("Descarga: Alcoazul vs Generalco", "Alcoazul", "Generalco", "Descarga"), unsafe_allow_html=True)
