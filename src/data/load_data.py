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


def load_population_data(
    filename_sem_censos="pop_sem_censos.xlsx",
    filename_2010="pop_2010.xlsx",
    filename_2022="pop_2022.xlsx",
    filename_tcu_2023="POP_TCU_2023_Municipios_POP2022_Malha2023.xls",
    filename_planning="Lista_Regioes_Planejamento_Ceara (1).xlsx",
):
    """
    Carrega e consolida os dados de população de todos os municípios do Ceará (2009-2025).
    Retorna um painel município-ano com população e proveniência.

    Observação metodológica:
    a população de 2023 é imputada pela média aritmética das populações
    municipais de 2020, 2021 e 2022. O parâmetro ``filename_tcu_2023`` é
    mantido apenas por compatibilidade e não participa do cálculo.
    """
    from src.data.clean_data import normalize_municipality_name, prepare_planning_regions

    # Carregar regiões de planejamento para mapeamento dos códigos IBGE (code_muni)
    planning_raw = load_planning_regions(filename_planning)
    planning = prepare_planning_regions(planning_raw)
    muni_map = dict(zip(planning['municipio_key'], planning['code_muni']))

    def _clean_muni_str(val):
        if pd.isna(val):
            return ""
        s = str(val).strip()
        if s.endswith("(CE)"):
            s = s[:-4].strip()
        return normalize_municipality_name(s)

    records = []

    # 1. pop_sem_censos.xlsx (2009, 2011-2021, 2024-2025)
    path_sem = _find_file(filename_sem_censos)
    df_sem = pd.read_excel(path_sem)
    years_row = df_sem.iloc[2].values[1:]
    for _, row in df_sem.iloc[3:].iterrows():
        muni_key = _clean_muni_str(row.iloc[0])
        if muni_key in muni_map:
            c_muni = muni_map[muni_key]
            for col_idx, yr in enumerate(years_row):
                if pd.notna(yr):
                    val = row.iloc[col_idx + 1]
                    if pd.notna(val):
                        records.append({
                            'code_muni': c_muni,
                            'ano': int(float(yr)),
                            'populacao': float(val),
                            'tipo_populacao': 'estimativa',
                            'fonte_populacao': 'IBGE - Estimativas da População',
                        })

    # 2. pop_2010.xlsx (2010)
    path_2010 = _find_file(filename_2010)
    df_2010 = pd.read_excel(path_2010)
    for _, row in df_2010.iloc[4:].iterrows():
        muni_key = _clean_muni_str(row.iloc[0])
        if muni_key in muni_map and pd.notna(row.iloc[1]):
            records.append({
                'code_muni': muni_map[muni_key],
                'ano': 2010,
                'populacao': float(row.iloc[1]),
                'tipo_populacao': 'censo',
                'fonte_populacao': 'IBGE - Censo Demográfico 2010',
            })

    # 3. pop_2022.xlsx (2022)
    path_2022 = _find_file(filename_2022)
    df_2022 = pd.read_excel(path_2022)
    for _, row in df_2022.iloc[4:].iterrows():
        muni_key = _clean_muni_str(row.iloc[0])
        if muni_key in muni_map and pd.notna(row.iloc[3]):
            records.append({
                'code_muni': muni_map[muni_key],
                'ano': 2022,
                'populacao': float(row.iloc[3]),
                'tipo_populacao': 'censo',
                'fonte_populacao': 'IBGE - Censo Demográfico 2022',
            })

    # 4. Imputação de 2023 pela média dos três anos anteriores (2020–2022)
    population_history = pd.DataFrame(records)
    previous_three_years = population_history[
        population_history['ano'].isin([2020, 2021, 2022])
    ]
    observations_per_municipality = previous_three_years.groupby(
        'code_muni'
    )['ano'].nunique()
    if (
        len(observations_per_municipality) != len(planning)
        or not observations_per_municipality.eq(3).all()
    ):
        raise ValueError(
            "Não foi possível imputar 2023: os anos de 2020 a 2022 "
            "não cobrem integralmente os 184 municípios."
        )
    population_2023 = (
        previous_three_years.groupby('code_muni', as_index=False)['populacao']
        .mean()
    )
    for record in population_2023.to_dict('records'):
        records.append({
            'code_muni': record['code_muni'],
            'ano': 2023,
            'populacao': record['populacao'],
            'tipo_populacao': 'imputada_media_3_anos',
            'fonte_populacao': 'Imputação pela média de 2020, 2021 e 2022',
        })

    pop_df = pd.DataFrame(records)
    duplicate_keys = pop_df.duplicated(subset=['code_muni', 'ano'], keep=False)
    if duplicate_keys.any():
        duplicate_sample = pop_df.loc[duplicate_keys, ['code_muni', 'ano']].head().to_dict('records')
        raise ValueError(f"Há chaves município-ano duplicadas na população: {duplicate_sample}")

    pop_df = pop_df.sort_values(['code_muni', 'ano']).reset_index(drop=True)
    pop_df['code_muni'] = pop_df['code_muni'].astype('Int64')
    pop_df['ano'] = pop_df['ano'].astype(int)

    expected_keys = pd.MultiIndex.from_product(
        [planning['code_muni'].astype('Int64').tolist(), range(2009, 2026)],
        names=['code_muni', 'ano'],
    )
    observed_keys = pd.MultiIndex.from_frame(pop_df[['code_muni', 'ano']])
    missing_keys = expected_keys.difference(observed_keys)
    extra_keys = observed_keys.difference(expected_keys)
    if len(missing_keys) or len(extra_keys):
        raise ValueError(
            "Cobertura populacional inválida: "
            f"{len(missing_keys)} chaves ausentes e {len(extra_keys)} chaves excedentes."
        )
    if pop_df['populacao'].isna().any() or pop_df['populacao'].le(0).any():
        raise ValueError("A população contém valores ausentes, nulos ou negativos.")

    return pop_df

