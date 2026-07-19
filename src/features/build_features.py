"""
Módulo para engenharia de atributos (features) do projeto de CVLI.
"""
import pandas as pd

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
        df_idade = df_feat[df_feat[age_column] != 'Não Informada'].copy()
        df_idade['idade_num'] = pd.to_numeric(df_idade[age_column], errors='coerce')
        
        bins = [0, 14, 17, 24, 29, 39, 49, 59, 120]
        labels = ['0-14', '15-17', '18-24', '25-29', '30-39', '40-49', '50-59', '60+']
        df_feat['faixa_etaria'] = pd.cut(df_idade['idade_num'], bins=bins, labels=labels, right=True)
        
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
