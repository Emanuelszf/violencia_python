"""
Módulo para geração e controle estético de visualizações gráficas de alta qualidade.
Garante cumprimento rigoroso das diretrizes de design e storytelling visual.
Paleta adotada: azul e laranja, com neutros de alto contraste.
"""
from textwrap import fill

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Paleta funcional: dois matizes principais e neutros.
COLOR_PRIMARY = '#174A7E'       # Azul profundo
COLOR_SECONDARY = '#4C78A8'     # Azul médio
COLOR_LIGHT_BLUE = '#A7C6DA'    # Azul de apoio
COLOR_ACCENT = '#F28E2B'        # Laranja
COLOR_ACCENT_DARK = '#C75D05'   # Laranja escuro
COLOR_MUTED = '#6B7280'         # Cinza médio
COLOR_TEXT = '#1F2937'          # Grafite
COLOR_GRID = '#D8DEE9'          # Grade discreta
COLOR_BG = '#FFFFFF'
COLOR_PALETTE = [
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_ACCENT,
    COLOR_LIGHT_BLUE,
    COLOR_ACCENT_DARK,
]

def set_chart_style():
    """
    Define a estética moderna, limpa e profissional para todas as figuras.
    """
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
    plt.rcParams['figure.dpi'] = 130
    plt.rcParams['axes.titlesize'] = 12.5
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.titlepad'] = 12
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['xtick.labelsize'] = 9.5
    plt.rcParams['ytick.labelsize'] = 9.5
    plt.rcParams['text.color'] = COLOR_TEXT
    plt.rcParams['axes.labelcolor'] = COLOR_TEXT
    plt.rcParams['xtick.color'] = COLOR_MUTED
    plt.rcParams['ytick.color'] = COLOR_MUTED
    plt.rcParams['figure.facecolor'] = COLOR_BG
    plt.rcParams['axes.facecolor'] = COLOR_BG
    plt.rcParams['grid.color'] = COLOR_GRID
    plt.rcParams['grid.alpha'] = 0.55


def _clean_axis(ax, grid_axis='y'):
    """Aplica acabamento visual consistente aos eixos."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLOR_GRID)
    ax.spines['bottom'].set_color(COLOR_GRID)
    ax.grid(axis=grid_axis, color=COLOR_GRID, linewidth=0.8, alpha=0.55)
    ax.grid(axis='x' if grid_axis == 'y' else 'y', visible=False)

def plot_temporal_trend(df_temporal):
    """
    Evolução da taxa anual de CVLI e sua variação percentual.

    Espera as colunas: ano, taxa_cvli_100k, variacao_pct e total_cvli.
    """
    set_chart_style()
    required = {'ano', 'taxa_cvli_100k', 'variacao_pct'}
    missing = required.difference(df_temporal.columns)
    if missing:
        raise KeyError(f"Colunas ausentes para o gráfico temporal: {sorted(missing)}")

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(12, 8.2),
        gridspec_kw={'height_ratios': [2.7, 1]},
        sharex=True,
    )

    ax1.plot(
        df_temporal['ano'],
        df_temporal['taxa_cvli_100k'],
        color=COLOR_PRIMARY,
        linewidth=3,
        marker='o',
        markerfacecolor=COLOR_BG,
        markeredgecolor=COLOR_PRIMARY,
        markeredgewidth=1.7,
        markersize=6.5,
        zorder=4,
    )

    peak = df_temporal.loc[df_temporal['taxa_cvli_100k'].idxmax()]
    peak_rate = float(peak['taxa_cvli_100k'])
    ax1.scatter(
        [peak['ano']],
        [peak_rate],
        color=COLOR_ACCENT,
        edgecolor=COLOR_BG,
        linewidth=1.5,
        s=115,
        zorder=6,
    )

    peak_cases = (
        f"\n{int(peak['total_cvli']):,} registros"
        if 'total_cvli' in df_temporal.columns
        else ''
    )
    ax1.text(
        0.98,
        0.88,
        f"Pico da série\n{int(peak['ano'])} · {peak_rate:.1f} por 100 mil{peak_cases}",
        transform=ax1.transAxes,
        ha='right',
        va='top',
        fontsize=10,
        color=COLOR_TEXT,
        linespacing=1.35,
        bbox={
            'boxstyle': 'round,pad=0.65',
            'facecolor': '#FFF4E8',
            'edgecolor': COLOR_ACCENT,
            'linewidth': 1.2,
        },
    )

    for row, horizontal_alignment in [
        (df_temporal.iloc[0], 'left'),
        (df_temporal.iloc[-1], 'right'),
    ]:
        ax1.annotate(
            f"{row['taxa_cvli_100k']:.1f}",
            (row['ano'], row['taxa_cvli_100k']),
            xytext=(0, 10),
            textcoords='offset points',
            ha=horizontal_alignment,
            fontsize=9,
            color=COLOR_PRIMARY,
            fontweight='bold',
        )

    ax1.set_title("Taxa anual de CVLI por 100 mil habitantes", loc='left')
    ax1.set_ylabel("Taxa por 100 mil")
    ax1.set_ylim(bottom=0, top=max(peak_rate * 1.18, peak_rate + 5))
    _clean_axis(ax1, grid_axis='y')

    variation = df_temporal['variacao_pct'].fillna(0)
    bar_colors = [
        COLOR_ACCENT if value > 0 else COLOR_LIGHT_BLUE if value < 0 else COLOR_MUTED
        for value in variation
    ]
    ax2.bar(
        df_temporal['ano'],
        variation,
        color=bar_colors,
        edgecolor=COLOR_BG,
        linewidth=0.7,
        width=0.72,
    )
    ax2.axhline(0, color=COLOR_TEXT, linewidth=0.9)
    ax2.set_title("Variação anual da taxa", loc='left', fontsize=11)
    ax2.set_ylabel("Variação (%)")
    ax2.set_xlabel("Ano")
    ax2.set_xticks(df_temporal['ano'])
    ax2.set_xticklabels(df_temporal['ano'].astype(int), rotation=45)
    _clean_axis(ax2, grid_axis='y')

    fig.suptitle(
        "Como o CVLI evoluiu ao longo do tempo?",
        x=0.08,
        y=0.995,
        ha='left',
        fontsize=16,
        fontweight='bold',
        color=COLOR_TEXT,
    )
    fig.text(
        0.08,
        0.01,
        "Fonte: SSPDS/CE e IBGE. A taxa estadual usa a soma da população municipal em cada ano.",
        ha='left',
        fontsize=8.8,
        color=COLOR_MUTED,
    )
    plt.tight_layout(rect=[0.05, 0.04, 0.99, 0.96])
    return fig, (ax1, ax2)

def plot_rmf_vs_interior_boxplot(panel):
    """
    Compara a distribuição das taxas município-ano entre Grande Fortaleza e
    Interior em quatro períodos.
    """
    set_chart_style()
    required = {'taxa_cvli_100k', 'regiao_planejamento', 'periodo'}
    missing = required.difference(panel.columns)
    if missing:
        raise KeyError(f"Colunas ausentes para o boxplot: {sorted(missing)}")

    df_box = panel.copy()
    if 'grupo' not in df_box.columns:
        df_box['grupo'] = df_box['regiao_planejamento'].apply(
            lambda x: 'RMF (Grande Fortaleza)' if str(x).strip() == 'Grande Fortaleza' else 'Interior'
        )

    periods = ['2009–2012', '2013–2016', '2017–2020', '2021–2025']
    order = ['RMF (Grande Fortaleza)', 'Interior']
    palette = {
        'RMF (Grande Fortaleza)': COLOR_PRIMARY,
        'Interior': COLOR_ACCENT,
    }
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.5), sharey=True)
    axes = axes.ravel()

    for ax, period in zip(axes, periods):
        subset = df_box[df_box['periodo'] == period]
        sns.boxplot(
            data=subset,
            x='grupo',
            y='taxa_cvli_100k',
            hue='grupo',
            order=order,
            palette=palette,
            legend=False,
            showfliers=False,
            width=0.52,
            linewidth=1.3,
            medianprops={'color': COLOR_BG, 'linewidth': 2.3},
            whiskerprops={'linewidth': 1.2},
            capprops={'linewidth': 1.2},
            ax=ax,
        )
        sns.stripplot(
            data=subset,
            x='grupo',
            y='taxa_cvli_100k',
            order=order,
            color=COLOR_TEXT,
            alpha=0.20,
            jitter=0.22,
            size=2.4,
            ax=ax,
            zorder=1,
        )
        medians = subset.groupby('grupo')['taxa_cvli_100k'].median()
        for position, group in enumerate(order):
            if group in medians:
                ax.text(
                    position,
                    medians[group],
                    f"{medians[group]:.1f}",
                    ha='center',
                    va='center',
                    fontsize=8.5,
                    color=COLOR_BG,
                    fontweight='bold',
                )
        ax.set_title(period, loc='left')
        ax.set_xlabel("")
        ax.set_ylabel("Taxa por 100 mil" if ax in (axes[0], axes[2]) else "")
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels(['Grande Fortaleza', 'Interior'])
        _clean_axis(ax, grid_axis='y')

    fig.suptitle(
        "Como as taxas de CVLI se distribuem entre a Grande Fortaleza e o Interior?",
        x=0.06,
        y=0.99,
        ha='left',
        fontsize=15.5,
        fontweight='bold',
        color=COLOR_TEXT,
    )
    fig.text(
        0.06,
        0.02,
        "Cada ponto representa um município-ano. As caixas mostram mediana e intervalo interquartil; todos os valores foram mantidos.",
        ha='left',
        fontsize=8.8,
        color=COLOR_MUTED,
    )
    plt.tight_layout(rect=[0.04, 0.05, 0.99, 0.95])
    return fig, axes
def plot_rmf_vs_interior_trend(evo_grupo):
    """
    Gráfico Comparativo Longitudinal RMF vs Interior (Volume absoluto).
    """
    set_chart_style()
    fig, ax = plt.subplots(figsize=(11, 5.5))

    for grupo, cor in zip(['RMF (Grande Fortaleza)', 'Interior'], [COLOR_PRIMARY, COLOR_ACCENT]):
        dados = evo_grupo[evo_grupo['grupo'] == grupo]
        ax.plot(
            dados['ano'], dados['total_cvli'],
            color=cor, linewidth=2.8, marker='o', markersize=5, label=grupo
        )

    ax.set_title("Qual a trajetória do volume total de homicídios entre a RMF e o Interior?", loc="left", pad=15)
    ax.set_ylabel("Total de CVLI")
    ax.set_xlabel("Ano")
    ax.legend(frameon=True, facecolor='white', edgecolor='none')

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_xticks(sorted(evo_grupo['ano'].unique()))
    ax.set_xticklabels(sorted(evo_grupo['ano'].unique()), rotation=45)

    plt.figtext(
        0.01, -0.03,
        "Fonte: SSPDS/CE. RMF compreende a Região de Planejamento da Grande Fortaleza.",
        ha="left", fontsize=8.5, style='italic', color=COLOR_MUTED
    )
    plt.tight_layout()
    return fig, ax

def plot_top_municipalities(ranking_muni, top_n=20):
    """
    Gráfico 3: Ranking dos Municípios com Maior Volume de CVLI.
    """
    set_chart_style()
    df_plot_top = ranking_muni.head(top_n).copy()

    fig, ax = plt.subplots(figsize=(11, 8))
    colors = [COLOR_PRIMARY if i == 0 else (COLOR_ACCENT if i < 5 else COLOR_MUTED) for i in range(len(df_plot_top))]

    muni_col = 'municipio' if 'municipio' in df_plot_top.columns else 'município'
    bars = ax.barh(
        df_plot_top[muni_col], df_plot_top['total_cvli'],
        color=colors, edgecolor='white', linewidth=0.8, height=0.75
    )


    for i, (val, pct) in enumerate(zip(df_plot_top['total_cvli'], df_plot_top['pct_total'])):
        ax.text(val + (df_plot_top['total_cvli'].max() * 0.01), i, f"{val:,} ({pct:.1f}%)", va='center', fontsize=9, fontweight='bold' if i == 0 else 'normal')

    ax.invert_yaxis()
    ax.set_title(f"Quais os {top_n} municípios que concentram o maior volume de homicídios?", loc="left", pad=15)
    ax.set_xlabel("Total Acumulado de CVLI (2009–2025)")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    ax.grid(axis="y", visible=False)

    plt.figtext(
        0.01, -0.02,
        "Fonte: SSPDS/CE. O município de Fortaleza lidera isoladamente o volume total acumulado.",
        ha="left", fontsize=8.5, style='italic', color=COLOR_MUTED
    )
    plt.tight_layout()
    return fig, ax


def plot_top_municipality_rates(ranking_rates, top_n=20):
    """Mostra os municípios com maior taxa média anual de CVLI."""
    set_chart_style()
    required = {'municipio', 'taxa_media_cvli_100k'}
    missing = required.difference(ranking_rates.columns)
    if missing:
        raise KeyError(f"Colunas ausentes para o ranking de taxas: {sorted(missing)}")

    data = (
        ranking_rates.nlargest(top_n, 'taxa_media_cvli_100k')
        .sort_values('taxa_media_cvli_100k')
        .copy()
    )
    colors = [
        COLOR_ACCENT if value == data['taxa_media_cvli_100k'].max() else COLOR_SECONDARY
        for value in data['taxa_media_cvli_100k']
    ]
    fig, ax = plt.subplots(figsize=(11, 8))
    ax.barh(
        data['municipio'],
        data['taxa_media_cvli_100k'],
        color=colors,
        edgecolor=COLOR_BG,
        linewidth=0.8,
        height=0.72,
    )
    max_value = data['taxa_media_cvli_100k'].max()
    ax.set_xlim(0, max_value * 1.18)
    for position, value in enumerate(data['taxa_media_cvli_100k']):
        ax.text(
            value + max_value * 0.015,
            position,
            f"{value:.1f}",
            va='center',
            fontsize=9,
            color=COLOR_TEXT,
            fontweight='bold' if value == max_value else 'normal',
        )

    ax.set_title("Taxa média anual por município · 2009–2025", loc='left')
    ax.set_xlabel("CVLI por 100 mil habitantes")
    ax.set_ylabel("")
    _clean_axis(ax, grid_axis='x')
    fig.suptitle(
        f"Quais municípios apresentaram as {top_n} maiores taxas médias de CVLI?",
        x=0.07,
        y=0.99,
        ha='left',
        fontsize=15.5,
        fontweight='bold',
    )
    fig.text(
        0.07,
        0.01,
        "Fonte: SSPDS/CE e IBGE. Média simples das taxas anuais municipais; todos os municípios foram mantidos.",
        fontsize=8.8,
        color=COLOR_MUTED,
    )
    plt.tight_layout(rect=[0.05, 0.04, 0.99, 0.95])
    return fig, ax


def plot_crime_nature_bar(distribution):
    """Mostra o número absoluto e a participação por natureza do crime."""
    set_chart_style()
    required = {'natureza', 'total', 'pct'}
    missing = required.difference(distribution.columns)
    if missing:
        raise KeyError(f"Colunas ausentes para o gráfico de natureza: {sorted(missing)}")

    data = distribution.sort_values('total').copy()
    colors = [
        COLOR_ACCENT if value == data['total'].max() else COLOR_SECONDARY
        for value in data['total']
    ]
    fig, ax = plt.subplots(figsize=(11.5, 6.5))
    ax.barh(
        data['natureza'],
        data['total'],
        color=colors,
        edgecolor=COLOR_BG,
        linewidth=0.8,
        height=0.68,
    )
    max_value = data['total'].max()
    ax.set_xlim(0, max_value * 1.23)
    for position, row in enumerate(data.itertuples(index=False)):
        ax.text(
            row.total + max_value * 0.015,
            position,
            f"{int(row.total):,}  ·  {row.pct:.1f}%",
            va='center',
            fontsize=9.5,
            color=COLOR_TEXT,
            fontweight='bold' if row.total == max_value else 'normal',
        )
    ax.set_title("Número de registros e participação no total · 2009–2025", loc='left')
    ax.set_xlabel("Número de registros")
    ax.set_ylabel("")
    _clean_axis(ax, grid_axis='x')
    fig.suptitle(
        "Qual é a natureza de crime mais proeminente?",
        x=0.07,
        y=0.99,
        ha='left',
        fontsize=15.5,
        fontweight='bold',
    )
    fig.text(
        0.07,
        0.01,
        "Fonte: SSPDS/CE. Esta comparação usa números absolutos, não taxas populacionais.",
        fontsize=8.8,
        color=COLOR_MUTED,
    )
    plt.tight_layout(rect=[0.05, 0.04, 0.99, 0.94])
    return fig, ax


def _plot_vertical_profile(
    distribution,
    category_column,
    question,
    subtitle,
    xlabel,
    valid_count,
    total_count,
    wrap_width=16,
    figsize=(11.5, 6.3),
):
    """Base visual para gráficos verticais do perfil das vítimas."""
    set_chart_style()
    required = {category_column, 'total', 'pct'}
    missing = required.difference(distribution.columns)
    if missing:
        raise KeyError(f"Colunas ausentes para o perfil: {sorted(missing)}")

    data = distribution.copy()
    labels = [fill(str(value), width=wrap_width) for value in data[category_column]]
    max_value = data['total'].max()
    colors = [
        COLOR_ACCENT if value == max_value else COLOR_SECONDARY
        for value in data['total']
    ]
    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.bar(
        labels,
        data['total'],
        color=colors,
        edgecolor=COLOR_BG,
        linewidth=0.8,
        width=0.68,
    )
    ax.set_ylim(0, max_value * 1.22)
    for bar, row in zip(bars, data.itertuples(index=False)):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max_value * 0.025,
            f"{int(row.total):,}\n{row.pct:.1f}%",
            ha='center',
            va='bottom',
            fontsize=8.7,
            color=COLOR_TEXT,
            fontweight='bold' if row.total == max_value else 'normal',
        )
    ax.set_title(subtitle, loc='left')
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Número de vítimas com informação válida")
    _clean_axis(ax, grid_axis='y')
    fig.suptitle(
        question,
        x=0.07,
        y=0.99,
        ha='left',
        fontsize=15.5,
        fontweight='bold',
    )
    coverage = valid_count / total_count * 100 if total_count else np.nan
    fig.text(
        0.07,
        0.01,
        f"Fonte: SSPDS/CE. Cobertura do campo: {valid_count:,} de {total_count:,} registros ({coverage:.1f}%).",
        fontsize=8.8,
        color=COLOR_MUTED,
    )
    plt.tight_layout(rect=[0.05, 0.05, 0.99, 0.94])
    return fig, ax


def plot_age_distribution(distribution, valid_count, total_count):
    """Gráfico vertical de vítimas por faixa etária."""
    return _plot_vertical_profile(
        distribution=distribution,
        category_column='faixa_etaria',
        question="Qual é a distribuição etária das vítimas?",
        subtitle="Vítimas por faixa etária · registros com idade válida",
        xlabel="Faixa etária",
        valid_count=valid_count,
        total_count=total_count,
        wrap_width=10,
    )


def plot_race_distribution(distribution, valid_count, total_count):
    """Gráfico vertical de vítimas por raça/cor."""
    return _plot_vertical_profile(
        distribution=distribution,
        category_column='raca',
        question="Como as vítimas se distribuem por raça/cor?",
        subtitle="Vítimas por raça/cor · registros com informação válida",
        xlabel="Raça/cor",
        valid_count=valid_count,
        total_count=total_count,
        wrap_width=12,
        figsize=(10.5, 6.2),
    )


def plot_education_distribution(distribution, valid_count, total_count):
    """Gráfico vertical de vítimas por escolaridade."""
    return _plot_vertical_profile(
        distribution=distribution,
        category_column='escolaridade',
        question="Qual é o perfil de escolaridade das vítimas?",
        subtitle="Vítimas por escolaridade · registros com informação válida",
        xlabel="Escolaridade",
        valid_count=valid_count,
        total_count=total_count,
        wrap_width=14,
        figsize=(13, 6.8),
    )


def plot_planning_regions(ranking_regiao):
    """
    Gráfico 4: Comparativo entre todas as 14 Regiões de Planejamento do Ceará.
    """
    set_chart_style()
    df_plot = ranking_regiao.sort_values('total_cvli', ascending=True).copy()

    fig, ax = plt.subplots(figsize=(11, 7))
    colors = [COLOR_PRIMARY if reg == 'Grande Fortaleza' else COLOR_SECONDARY for reg in df_plot['regiao_planejamento']]

    ax.barh(df_plot['regiao_planejamento'], df_plot['total_cvli'], color=colors, height=0.7)

    for i, (val, pct) in enumerate(zip(df_plot['total_cvli'], df_plot['pct_total'])):
        ax.text(val + (df_plot['total_cvli'].max() * 0.01), i, f"{val:,} ({pct:.1f}%)", va='center', fontsize=9)

    ax.set_title("Como a violência se distribui entre as 14 Regiões de Planejamento do Ceará?", loc="left", pad=15)
    ax.set_xlabel("Total Acumulado de CVLI (2009–2025)")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    ax.grid(axis="y", visible=False)

    plt.figtext(
        0.01, -0.02,
        "Fonte: SEPLAG/CE e SSPDS. Elaboração própria.",
        ha="left", fontsize=8.5, style='italic', color=COLOR_MUTED
    )
    plt.tight_layout()
    return fig, ax

def plot_regional_facet_trends(evolucao_regiao):
    """
    Painel de Tendências Anuais por Região de Planejamento.
    """
    set_chart_style()
    g = sns.FacetGrid(
        evolucao_regiao, col="regiao_planejamento", col_wrap=4,
        height=3.2, aspect=1.3, sharey=False
    )

    g.map_dataframe(
        sns.lineplot, x="ano", y="total_cvli_ano",
        color=COLOR_PRIMARY, linewidth=2, marker="o", markersize=3
    )

    g.set_titles("{col_name}", size=10.5, fontweight="bold")
    g.set_axis_labels("Ano", "CVLI")

    for ax in g.axes.flat:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", alpha=0.3)

    g.fig.suptitle(
        "Qual a trajetória anual da violência letal em cada uma das 14 regiões do estado?",
        fontsize=14, fontweight='bold', x=0.01, ha='left', y=1.03
    )
    plt.tight_layout()
    return g

def plot_crime_nature_breakdown(dist_natureza, evo_natureza):
    """
    Gráfico de Distribuição e Evolução por Natureza do Crime.
    Substituído por Gráfico de Barras no painel esquerdo para destacar o tipo penal proeminente.
    """
    set_chart_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={'width_ratios': [1.1, 1.5]})

    # Eixo 1: Gráfico de Barras da Natureza do Crime (Ordenado)
    df_nat = dist_natureza.sort_values('total', ascending=True).copy()
    colors_nat = [COLOR_PRIMARY if i == len(df_nat) - 1 else COLOR_SECONDARY for i in range(len(df_nat))]

    bars = ax1.barh(df_nat['natureza'], df_nat['total'], color=colors_nat, height=0.65)
    max_val = df_nat['total'].max()
    ax1.set_xlim(right=max_val * 1.18)

    for i, (val, pct) in enumerate(zip(df_nat['total'], df_nat['pct'])):
        ax1.text(val + (max_val * 0.015), i, f"{val:,} ({pct:.1f}%)", va='center', fontsize=9, fontweight='bold' if i == len(df_nat)-1 else 'normal')

    ax1.set_title("Qual a natureza do crime mais proeminente?", loc="left")
    ax1.set_xlabel("Total de Casos (2009–2025)")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.grid(axis="x", alpha=0.3, linestyle="--")

    # Eixo 2: Linhas de evolução temporal por natureza
    for i, nat in enumerate(dist_natureza['natureza']):
        sub = evo_natureza[evo_natureza['natureza'] == nat]
        ax2.plot(sub['ano'], sub['total'], marker='o', label=nat, color=COLOR_PALETTE[i % len(COLOR_PALETTE)], linewidth=2.2)

    ax2.set_title("Como cada tipo penal oscilou ao longo do período?", loc="left")
    ax2.set_xlabel("Ano")
    ax2.set_ylabel("Total de Casos")
    ax2.legend(fontsize=8.5, frameon=True, facecolor='white', edgecolor='none')
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(axis="y", alpha=0.3)

    fig.suptitle("Qual é a composição jurídica/penal dos Crimes Violentos Letais Intencionais?", fontsize=14, fontweight='bold', x=0.01, ha='left', y=1.02)
    plt.tight_layout()
    return fig, (ax1, ax2)

def plot_victim_demographics(dist_idade, dist_esc, dist_raca):
    """
    Gráfico de Perfil Demográfico das Vítimas.
    Eixo 1 reformulado para Gráfico de Colunas Verticais por Faixa Etária.
    """
    set_chart_style()
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.8))

    # 1. Faixa etária (Gráfico de Colunas Verticais)
    ax1 = axes[0]
    bars1 = ax1.bar(dist_idade['faixa_etaria'].astype(str), dist_idade['total'], color=COLOR_PRIMARY, width=0.65)
    ax1.set_title("Qual a faixa etária mais afetada?", loc="left")
    ax1.set_ylabel("Total de Vítimas")
    ax1.set_xlabel("Faixa Etária (anos)")
    max_age_val = dist_idade['total'].max()
    ax1.set_ylim(top=max_age_val * 1.15)

    for i, (val, pct) in enumerate(zip(dist_idade['total'], dist_idade['pct'])):
        ax1.text(i, val + (max_age_val * 0.02), f"{pct:.1f}%\n({val:,})", ha='center', va='bottom', fontsize=8, fontweight='bold' if val == max_age_val else 'normal')

    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.grid(axis="y", alpha=0.3, linestyle="--")

    # 2. Escolaridade (Barras Horizontais)
    ax2 = axes[1]
    ax2.barh(dist_esc['escolaridade'], dist_esc['total'], color=COLOR_SECONDARY, height=0.65)
    ax2.set_title("Por nível de escolaridade?", loc="left")
    ax2.invert_yaxis()
    max_esc_val = dist_esc['total'].max()
    ax2.set_xlim(right=max_esc_val * 1.25)
    for i, (val, pct) in enumerate(zip(dist_esc['total'], dist_esc['pct'])):
        ax2.text(val + (max_esc_val * 0.02), i, f"{pct:.1f}%", va='center', fontsize=8.5)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(axis="x", alpha=0.3, linestyle="--")

    # 3. Raça (Barras Horizontais)
    ax3 = axes[2]
    ax3.barh(dist_raca['raca'], dist_raca['total'], color=COLOR_ACCENT, height=0.65)
    ax3.set_title("Por pertencimento racial?", loc="left")
    ax3.invert_yaxis()
    max_raca_val = dist_raca['total'].max()
    ax3.set_xlim(right=max_raca_val * 1.25)
    for i, (val, pct) in enumerate(zip(dist_raca['total'], dist_raca['pct'])):
        ax3.text(val + (max_raca_val * 0.02), i, f"{pct:.1f}%", va='center', fontsize=8.5)
    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)
    ax3.grid(axis="x", alpha=0.3, linestyle="--")

    fig.suptitle(
        "Quem são as vítimas dos homicídios no Ceará?",
        fontsize=14, fontweight='bold', x=0.01, ha='left', y=1.02
    )
    plt.figtext(
        0.01, -0.03,
        "Nota: Análise restrita às ocorrências com dados válidos informados pelos órgãos de segurança da SSPDS/CE.",
        ha="left", fontsize=8.5, style='italic', color=COLOR_MUTED
    )
    plt.tight_layout()
    return fig, axes

def plot_monthly_heatmap(heatmap_pivot):
    """Mapa de calor do número mensal de registros de CVLI."""
    set_chart_style()
    fig, ax = plt.subplots(figsize=(15, 6))
    cmap = sns.blend_palette(
        ['#F3F7FA', COLOR_LIGHT_BLUE, COLOR_SECONDARY, COLOR_PRIMARY],
        as_cmap=True,
    )

    sns.heatmap(
        heatmap_pivot,
        cmap=cmap,
        annot=True,
        fmt='.0f',
        linewidths=0.5,
        linecolor=COLOR_BG,
        ax=ax,
        cbar_kws={'label': 'Número mensal de registros de CVLI'},
        annot_kws={'size': 8.5}
    )

    max_position = np.unravel_index(
        np.nanargmax(heatmap_pivot.to_numpy(dtype=float)),
        heatmap_pivot.shape,
    )
    ax.add_patch(
        plt.Rectangle(
            (max_position[1], max_position[0]),
            1,
            1,
            fill=False,
            edgecolor=COLOR_ACCENT,
            linewidth=2.5,
        )
    )

    ax.set_title("Número de registros por mês e ano", loc="left", pad=15)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Mês")

    fig.suptitle(
        "Existe sazonalidade nos registros de CVLI?",
        x=0.05,
        y=0.995,
        ha='left',
        fontsize=15.5,
        fontweight='bold',
    )
    fig.text(
        0.05,
        0.01,
        "Fonte: SSPDS/CE. O contorno laranja marca o maior número mensal observado; os valores são absolutos.",
        ha="left",
        fontsize=8.8,
        color=COLOR_MUTED,
    )
    plt.tight_layout(rect=[0.03, 0.04, 0.99, 0.94])
    return fig, ax

def plot_seasonality_bars(dist_mes, dist_dia):
    """Resume os números absolutos de CVLI por mês e dia da semana."""
    set_chart_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    month_colors = [
        COLOR_ACCENT if value == dist_mes['total'].max() else COLOR_SECONDARY
        for value in dist_mes['total']
    ]
    month_bars = ax1.bar(
        dist_mes['mes_nome'],
        dist_mes['total'],
        color=month_colors,
        width=0.66,
    )
    ax1.bar_label(month_bars, fmt='%.0f', padding=3, fontsize=8)
    ax1.set_ylim(0, dist_mes['total'].max() * 1.16)
    ax1.set_title("Em quais meses há mais registros?", loc="left")
    ax1.set_ylabel("Número de registros")
    _clean_axis(ax1, grid_axis='y')

    ordem_dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    dist_dia_ord = dist_dia.set_index('dia_nome').loc[ordem_dias].reset_index()
    day_colors = [
        COLOR_ACCENT if value == dist_dia_ord['total'].max() else COLOR_SECONDARY
        for value in dist_dia_ord['total']
    ]
    day_bars = ax2.bar(
        dist_dia_ord['dia_nome'],
        dist_dia_ord['total'],
        color=day_colors,
        width=0.66,
    )
    ax2.bar_label(day_bars, fmt='%.0f', padding=3, fontsize=8)
    ax2.set_ylim(0, dist_dia_ord['total'].max() * 1.16)
    ax2.set_title("Em quais dias da semana há mais registros?", loc="left")
    ax2.set_ylabel("Número de registros")
    _clean_axis(ax2, grid_axis='y')

    fig.suptitle(
        "Como os registros se distribuem no calendário?",
        fontsize=15.5,
        fontweight='bold',
        x=0.04,
        ha='left',
        y=0.995,
    )
    fig.text(
        0.04,
        0.01,
        "Fonte: SSPDS/CE. Totais acumulados de 2009 a 2025; a distribuição não identifica causalidade.",
        fontsize=8.8,
        color=COLOR_MUTED,
    )
    plt.tight_layout(rect=[0.02, 0.04, 0.99, 0.94])
    return fig, (ax1, ax2)

def plot_municipality_period_maps(
    geo_ce,
    period_metrics,
    periods=None,
    value_column='taxa_media_cvli_100k',
):
    """Mapeia a taxa média anual de CVLI por município em cada período."""
    required_geo = {'code_muni', 'geometry'}
    required_data = {'code_muni', 'periodo', value_column}
    if not required_geo.issubset(geo_ce.columns):
        raise KeyError(f"A geometria precisa conter: {sorted(required_geo)}")
    if not required_data.issubset(period_metrics.columns):
        raise KeyError(f"Os dados precisam conter: {sorted(required_data)}")

    periods = periods or ['2009–2012', '2013–2016', '2017–2020', '2021–2025']
    geo = geo_ce[['code_muni', 'geometry']].copy()
    geo['code_muni'] = geo['code_muni'].astype('Int64')
    data = period_metrics.copy()
    data['code_muni'] = data['code_muni'].astype('Int64')
    vmax = float(data[value_column].max())
    cmap = sns.blend_palette(
        ['#EAF2F8', COLOR_LIGHT_BLUE, COLOR_SECONDARY, COLOR_PRIMARY],
        as_cmap=True,
    )

    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    axes = axes.ravel()
    for ax, period in zip(axes, periods):
        subset = data[data['periodo'] == period]
        if subset['code_muni'].duplicated().any():
            raise ValueError(f"Há municípios duplicados no período {period}.")
        map_data = geo.merge(
            subset[['code_muni', value_column]],
            on='code_muni',
            how='left',
            validate='one_to_one',
        )
        if map_data[value_column].isna().any():
            missing_codes = map_data.loc[
                map_data[value_column].isna(), 'code_muni'
            ].astype(str).tolist()
            raise ValueError(
                f"O mapa de {period} perdeu {len(missing_codes)} municípios: "
                f"{missing_codes[:5]}"
            )
        map_data.plot(
            column=value_column,
            ax=ax,
            cmap=cmap,
            vmin=0,
            vmax=vmax,
            linewidth=0.25,
            edgecolor='white',
            legend=True,
            missing_kwds={'color': '#eeeeee', 'label': 'Sem correspondência'},
            legend_kwds={'label': 'Taxa média anual por 100 mil', 'shrink': 0.65},
        )
        ax.set_title(period, loc='left', fontweight='bold')
        ax.set_axis_off()

    for ax in axes[len(periods):]:
        ax.set_visible(False)
    fig.suptitle(
        'Como a taxa de CVLI se distribui espacialmente entre os municípios?',
        fontsize=15,
        fontweight='bold',
        x=0.03,
        ha='left',
    )
    fig.text(
        0.03,
        0.01,
        'Nota: média simples das taxas anuais municipais; a escala de cores é comum aos quatro períodos.',
        fontsize=9,
        style='italic',
        color='#666666',
    )
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    return fig, axes
