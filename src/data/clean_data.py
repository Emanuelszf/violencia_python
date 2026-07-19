"""
Módulo de tratamento e limpeza de dados de CVLI.
"""

import re
import unicodedata

def clean_column_names(df):
    """
    Padroniza os nomes das colunas (minúsculas, sem espaços, com underscore).
    """
    df_clean = df.copy()
    df_clean.columns = df_clean.columns.str.strip().str.lower().str.replace(' ', '_')
    return df_clean


def normalize_municipality_name(value):
    """Normaliza nomes para chaves de junção sem alterar o texto exibido."""
    if value is None:
        return ""
    text = str(value).strip().casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text)


def prepare_planning_regions(df):
    """Padroniza o arquivo local de municípios e Regiões de Planejamento."""
    planning = clean_column_names(df)
    planning.columns = (
        planning.columns
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )
    rename_dict = {
        "código_do_município_ibge": "code_muni",
        "nome_do_município": "municipio",
        "região_de_planejamento": "regiao_planejamento",
    }
    planning = planning.rename(columns=rename_dict)
    required = {"code_muni", "municipio", "regiao_planejamento"}
    missing = required.difference(planning.columns)
    if missing:
        raise KeyError(f"Colunas ausentes no mapeamento regional: {sorted(missing)}")
    planning = planning[["code_muni", "municipio", "regiao_planejamento"]].copy()
    planning["code_muni"] = planning["code_muni"].astype("Int64")
    planning["municipio_key"] = planning["municipio"].map(normalize_municipality_name)
    if planning["municipio_key"].duplicated().any():
        raise ValueError("O mapeamento regional contém municípios duplicados.")
    return planning

def merge_geodata_and_regions(df_data, geo_ce, planejamento):
    """
    Realiza o merge dos dados (microdados ou agregados) com as coordenadas de geobr 
    e o mapeamento das 14 Regiões de Planejamento do Ceará.
    """
    data_copy = df_data.copy()
    geo_ce_copy = geo_ce.copy()
    planejamento_copy = planejamento.copy()

    # Preparar geobr
    geo_ce_copy['name_muni_upper'] = geo_ce_copy['name_muni'].str.upper().str.strip()
    df_muni_info = geo_ce_copy[['code_muni', 'name_muni_upper', 'geometry']].copy()
    df_muni_info['longitude'] = df_muni_info['geometry'].centroid.x
    df_muni_info['latitude'] = df_muni_info['geometry'].centroid.y
    df_coords = df_muni_info.drop(columns=['geometry'])

    # Merge com coordenadas
    data_copy['muni_upper'] = data_copy['município'].str.upper().str.strip()
    data_copy = data_copy.merge(df_coords, left_on='muni_upper', right_on='name_muni_upper', how='left')
    data_copy = data_copy.drop(columns=['muni_upper', 'name_muni_upper'])
    data_copy['code_muni'] = data_copy['code_muni'].astype('Int64')

    # Preparar regiões de planejamento
    planejamento_copy = prepare_planning_regions(planejamento)
    df_regioes = planejamento_copy[['code_muni', 'regiao_planejamento']].drop_duplicates()

    # Merge com regiões
    data_copy = data_copy.merge(df_regioes, on='code_muni', how='left')
    return data_copy
