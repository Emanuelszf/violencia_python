"""
Módulo de tratamento e limpeza de dados de CVLI.
"""

def clean_column_names(df):
    """
    Padroniza os nomes das colunas (minúsculas, sem espaços, com underscore).
    """
    df_clean = df.copy()
    df_clean.columns = df_clean.columns.str.strip().str.lower().str.replace(' ', '_')
    return df_clean

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
    planejamento_copy.columns = (
        planejamento_copy.columns.str.strip()
        .str.lower()
        .str.replace(' ', '_')
        .str.replace('(', '')
        .str.replace(')', '')
    )
    rename_dict = {
        'código_do_município_ibge': 'code_muni',
        'nome_do_município': 'nome_muni_plan',
        'região_de_planejamento': 'regiao_planejamento'
    }
    planejamento_copy = planejamento_copy.rename(columns=rename_dict)
    planejamento_copy['code_muni'] = planejamento_copy['code_muni'].astype('Int64')
    
    # Mapeamento único code_muni -> regiao_planejamento
    df_regioes = planejamento_copy[['code_muni', 'regiao_planejamento']].drop_duplicates()

    # Merge com regiões
    data_copy = data_copy.merge(df_regioes, on='code_muni', how='left')
    return data_copy
