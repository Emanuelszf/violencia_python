"""
Módulo para carregamento de dados do projeto de CVLI.
"""
import os
import pandas as pd

def _find_file(filename):
    """
    Busca o arquivo no caminho relativo ao diretório atual ou raiz do projeto.
    """
    candidates = [
        os.path.join("data", filename),
        os.path.join("..", "data", filename),
        filename
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"Arquivo não encontrado: {filename}. Buscado em: {candidates}")

def load_cvli_data(filename="CVLI_2009-a-2025.xlsx", sheet_name=0):
    """
    Carrega o arquivo bruto de dados de CVLI.
    """
    path = _find_file(filename)
    # A análise usa explicitamente a primeira aba (CVLI). As demais abas
    # possuem outras unidades/fenômenos e não entram neste notebook.
    df = pd.read_excel(path, sheet_name=sheet_name)
    return df

def load_planning_regions(filename="Lista_Regioes_Planejamento_Ceara (1).xlsx"):
    """
    Carrega o arquivo com o mapeamento das Regiões de Planejamento do Ceará.
    """
    try:
        path = _find_file(filename)
    except FileNotFoundError:
        # Tenta sem o ' (1)' no nome se tiver sido renomeado
        path = _find_file("Lista_Regioes_Planejamento_Ceara.xlsx")
    planejamento = pd.read_excel(path)
    return planejamento

def load_municipality_geodata(state="CE", year=2020):
    """
    Carrega os dados geográficos e malha municipal do IBGE via geobr.
    """
    try:
        import geobr
    except ImportError as exc:
        raise ImportError(
            "A camada municipal exige o pacote 'geobr'. "
            "Instale-o para executar os mapas: pip install geobr geopandas."
        ) from exc

    geo_ce = geobr.read_municipality(code_muni=state, year=year)
    return geo_ce
