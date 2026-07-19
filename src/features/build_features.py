"""
Módulo para engenharia de atributos (features) do projeto de CVLI.
"""
import pandas as pd

from src.data.clean_data import (
    normalize_municipality_name,
    prepare_planning_regions,
)

def extract_temporal_features(df, date_column='data'):
    """
    Extrai mês, dia da semana, trimestre e rótulos formatados a partir da coluna de data.
    """
    df_feat = df.copy()
    if date_column in df_feat.columns:
        df_feat[date_column] = pd.to_datetime(df_feat[date_column], errors='coerce')
        df_feat['mes'] = df_feat[date_column].dt.month
        df_feat['dia_semana'] = df_feat[date_column].dt.dayofweek
        df_feat['trimestre'] = df_feat[date_column].dt.quarter

        meses_nome = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun',
                      7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}
        dias_nome = {0:'Seg', 1:'Ter', 2:'Qua', 3:'Qui', 4:'Sex', 5:'Sáb', 6:'Dom'}

        df_feat['mes_nome'] = df_feat['mes'].map(meses_nome)
        df_feat['dia_nome'] = df_feat['dia_semana'].map(dias_nome)

    return df_feat

def create_age_groups(df, age_column='idade_da_vítima'):
    """
    Cria a variável categórica de faixas etárias padronizadas.
    """
    df_feat = df.copy()
    if age_column in df_feat.columns:
        idade_num = pd.to_numeric(df_feat[age_column], errors='coerce')
        bins = [0, 14, 17, 24, 29, 39, 49, 59, 120]
        labels = ['0-14', '15-17', '18-24', '25-29', '30-39', '40-49', '50-59', '60+']
        df_feat['faixa_etaria'] = pd.cut(idade_num, bins=bins, labels=labels, right=True)
        
    return df_feat

def categorize_rmf_vs_interior(df, region_column='regiao_planejamento'):
    """
    Categoriza observações entre RMF (Grande Fortaleza) e Interior do Ceará.
    """
    df_feat = df.copy()
    if region_column in df_feat.columns:
        rmf_regioes = ['Grande Fortaleza']
        df_feat['grupo'] = df_feat[region_column].apply(
            lambda x: 'RMF (Grande Fortaleza)' if str(x).strip() in rmf_regioes else 'Interior'
        )
    return df_feat

def calculate_regional_metrics(df, region_column='regiao_planejamento'):
    """
    Calcula métricas comparativas agregadas por Região de Planejamento do Ceará.
    """
    if region_column not in df.columns:
        raise KeyError(f"Coluna {region_column} não encontrada no DataFrame.")
        
    resumo = df.groupby(region_column).size().reset_index(name='total_cvli')
    resumo['pct_total'] = (resumo['total_cvli'] / resumo['total_cvli'].sum() * 100).round(2)
    resumo = resumo.sort_values('total_cvli', ascending=False).reset_index(drop=True)
    return resumo


def validate_cvli_data(df, planning_regions, year_column='ano', date_column='data'):
    """Retorna diagnósticos auditáveis da base bruta de CVLI."""
    if year_column not in df.columns or date_column not in df.columns:
        raise KeyError(f"A base precisa conter '{year_column}' e '{date_column}'.")

    date_values = pd.to_datetime(df[date_column], errors='coerce')
    mismatch = (
        date_values.notna()
        & df[year_column].notna()
        & (date_values.dt.year.astype('Int64') != df[year_column].astype('Int64'))
    )
    missing = df.isna().sum().rename('missing_count').to_frame()
    missing['missing_pct'] = (missing['missing_count'] / len(df) * 100).round(2)

    planning = prepare_planning_regions(planning_regions)
    observed_municipalities = set(df['município'].map(normalize_municipality_name))
    mapped_municipalities = set(planning['municipio_key'])

    return {
        'rows': len(df),
        'columns': len(df.columns),
        'years': sorted(df[year_column].dropna().astype(int).unique().tolist()),
        'municipalities': int(df['município'].map(normalize_municipality_name).nunique()),
        'date_invalid_count': int(date_values.isna().sum()),
        'year_date_mismatch_count': int(mismatch.sum()),
        'duplicate_rows': int(df.duplicated().sum()),
        'missing': missing.sort_values('missing_pct', ascending=False),
        'municipalities_not_in_planning': sorted(observed_municipalities - mapped_municipalities),
        'planning_municipalities_not_observed': sorted(mapped_municipalities - observed_municipalities),
    }


def build_municipality_year_panel(
    df,
    planning_regions,
    year_column='ano',
    municipality_column='município',
):
    """Cria o painel completo município–ano, incluindo zeros observados."""
    required = {year_column, municipality_column}
    missing = required.difference(df.columns)
    if missing:
        raise KeyError(f"Colunas ausentes na base de CVLI: {sorted(missing)}")

    planning = prepare_planning_regions(planning_regions)
    years = list(range(int(df[year_column].min()), int(df[year_column].max()) + 1))

    cvli = df[[municipality_column, year_column]].copy()
    cvli['municipio_key'] = cvli[municipality_column].map(normalize_municipality_name)
    observed = (
        cvli.groupby(['municipio_key', year_column], as_index=False)
        .size()
        .rename(columns={'size': 'total_cvli'})
    )

    universe = pd.MultiIndex.from_product(
        [planning['municipio_key'].tolist(), years],
        names=['municipio_key', year_column],
    ).to_frame(index=False)
    panel = universe.merge(
        planning[['code_muni', 'municipio', 'regiao_planejamento', 'municipio_key']],
        on='municipio_key',
        how='left',
        validate='many_to_one',
    )
    panel = panel.merge(
        observed,
        on=['municipio_key', year_column],
        how='left',
        validate='one_to_one',
    )
    panel['total_cvli'] = panel['total_cvli'].fillna(0).astype(int)
    panel['tem_registro'] = panel['total_cvli'].gt(0)
    panel = panel[
        ['code_muni', 'municipio', 'regiao_planejamento', year_column, 'total_cvli', 'tem_registro']
    ].sort_values(['code_muni', year_column]).reset_index(drop=True)

    if panel.duplicated(['code_muni', year_column]).any():
        raise AssertionError('O painel possui duplicidade na chave município–ano.')
    return panel


def add_fixed_periods(df, year_column='ano', period_column='periodo'):
    """Adiciona os quatro blocos temporais definidos para o notebook."""
    if year_column not in df.columns:
        raise KeyError(f"Coluna temporal ausente: {year_column}")
    periods = pd.Series(pd.NA, index=df.index, dtype='object')
    periods.loc[df[year_column].between(2009, 2012)] = '2009–2012'
    periods.loc[df[year_column].between(2013, 2016)] = '2013–2016'
    periods.loc[df[year_column].between(2017, 2020)] = '2017–2020'
    periods.loc[df[year_column].between(2021, 2025)] = '2021–2025'
    if periods.isna().any():
        raise ValueError('Há anos fora dos quatro blocos temporais definidos.')
    result = df.copy()
    result[period_column] = periods
    return result


def calculate_period_metrics(panel, period_column='periodo'):
    """Calcula volume acumulado, média anual e participação por município/período."""
    required = {'code_muni', 'municipio', 'regiao_planejamento', 'ano', 'total_cvli', period_column}
    missing = required.difference(panel.columns)
    if missing:
        raise KeyError(f"Colunas ausentes no painel: {sorted(missing)}")

    period = (
        panel.groupby(
            [period_column, 'code_muni', 'municipio', 'regiao_planejamento'],
            as_index=False,
        )
        .agg(
            total_cvli=('total_cvli', 'sum'),
            media_anual_cvli=('total_cvli', 'mean'),
            anos_com_registro=('tem_registro', 'sum'),
        )
    )
    period['media_anual_cvli'] = period['media_anual_cvli'].round(2)
    period['participacao_periodo_pct'] = (
        period['total_cvli']
        / period.groupby(period_column)['total_cvli'].transform('sum')
        * 100
    ).round(2)
    return period.sort_values([period_column, 'total_cvli'], ascending=[True, False]).reset_index(drop=True)


def calculate_concentration_metrics(period_metrics, period_column='periodo'):
    """Resume concentração por período, preservando volume e participação."""
    rows = []
    for period, group in period_metrics.groupby(period_column, sort=False):
        ordered = group.sort_values('total_cvli', ascending=False)
        total = ordered['total_cvli'].sum()
        shares = ordered['total_cvli'] / total if total else ordered['total_cvli']
        rows.append({
            period_column: period,
            'total_cvli': int(total),
            'municipios_com_registro': int((ordered['total_cvli'] > 0).sum()),
            'top_1_pct': round(shares.head(1).sum() * 100, 2),
            'top_5_pct': round(shares.head(5).sum() * 100, 2),
            'top_10_pct': round(shares.head(10).sum() * 100, 2),
            'hhi': round((shares.pow(2).sum() * 10000), 2),
        })
    return pd.DataFrame(rows)


def add_population_rates(panel, population_df, population_column='populacao'):
    """Anexa população município–ano e calcula taxa por 100 mil habitantes."""
    required = {'code_muni', 'ano', population_column}
    missing = required.difference(population_df.columns)
    if missing:
        raise KeyError(f"Colunas ausentes no arquivo de população: {sorted(missing)}")
    if population_df.duplicated(['code_muni', 'ano']).any():
        raise ValueError('O arquivo de população possui duplicidade em code_muni–ano.')

    result = panel.merge(
        population_df[['code_muni', 'ano', population_column]],
        on=['code_muni', 'ano'],
        how='left',
        validate='one_to_one',
    )
    result['taxa_cvli_100k'] = (
        result['total_cvli'] / result[population_column] * 100_000
    ).where(result[population_column].gt(0))
    return result
