"""
Módulo para geração de gráficos e visualizações estáticas.
Garante cumprimento das diretrizes estabelecidas na skill gráfico.
"""
import matplotlib.pyplot as plt
import seaborn as sns

def set_chart_style():
    """
    Define o tema e parâmetros visuais padrão para os gráficos do projeto.
    """
    sns.set_theme(style="whitegrid")
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['font.size'] = 11

def plot_temporal_trend(df_temporal):
    """
    Plota a evolução anual histórica de CVLI no Ceará.
    """
    set_chart_style()
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(
        df_temporal['ano'],
        df_temporal['total_cvli'],
        linewidth=2.5,
        color='#1a5276',
        marker='o',
        markersize=6,
        zorder=3
    )

    for _, row in df_temporal.iterrows():
        ax.annotate(
            f"{int(row['total_cvli']):,}",
            (row['ano'], row['total_cvli']),
            textcoords="offset points",
            xytext=(0, 12),
            ha='center',
            fontsize=8,
            color='#1a5276'
        )

    ax.set_title(
        "Evolução dos Crimes Violentos Letais Intencionais no Ceará",
        loc="left", fontsize=16, fontweight="bold", pad=15
    )
    ax.set_xlabel("")
    ax.set_ylabel("Total de CVLI", fontsize=12)
    ax.set_xticks(df_temporal['ano'])
    ax.set_xticklabels(df_temporal['ano'].astype(int), rotation=45)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.grid(axis="x", visible=False)

    plt.figtext(
        0.01, -0.04,
        "Fonte: SSPDS/CE. Elaboração própria.",
        ha="left", fontsize=9, style='italic'
    )

    plt.tight_layout()
    return fig, ax

def plot_top_municipalities(ranking_muni, top_n=20):
    """
    Plota ranking horizontal dos municípios com maior volume de CVLI.
    """
    set_chart_style()
    df_plot_top = ranking_muni.head(top_n).copy()

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ['#1a5276' if i == 0 else '#aab7b8' for i in range(len(df_plot_top))]

    ax.barh(
        df_plot_top['município'],
        df_plot_top['total_cvli'],
        color=colors,
        edgecolor='white',
        linewidth=0.5
    )

    for i, (val, pct) in enumerate(zip(df_plot_top['total_cvli'], df_plot_top['pct_total'])):
        ax.text(val + 100, i, f"{val:,} ({pct:.1f}%)", va='center', fontsize=9)

    ax.invert_yaxis()
    ax.set_title(
        f"Top {top_n} municípios concentram a maioria dos CVLI do Ceará",
        loc="left", fontsize=14, fontweight="bold", pad=15
    )
    ax.set_xlabel("Total de CVLI (2009–2025)")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.25)
    ax.grid(axis="y", visible=False)

    plt.figtext(
        0.01, -0.02,
        f"Fonte: SSPDS/CE. Elaboração própria. Top {top_n} de 184 municípios.",
        ha="left", fontsize=9, style='italic'
    )

    plt.tight_layout()
    return fig, ax

def plot_monthly_heatmap(heatmap_pivot):
    """
    Plota mapa de calor (heatmap) para a distribuição de CVLI por mês e ano.
    """
    set_chart_style()
    fig, ax = plt.subplots(figsize=(16, 6))

    sns.heatmap(
        heatmap_pivot,
        cmap='YlOrRd',
        annot=True,
        fmt='.0f',
        linewidths=0.5,
        ax=ax,
        cbar_kws={'label': 'Total de CVLI'}
    )

    ax.set_title(
        "Distribuição mensal dos CVLI no Ceará (2009–2025)",
        loc="left", fontsize=14, fontweight="bold", pad=15
    )
    ax.set_xlabel("Ano")
    ax.set_ylabel("Mês")

    plt.figtext(
        0.01, -0.04,
        "Fonte: SSPDS/CE. Elaboração própria.",
        ha="left", fontsize=9, style='italic'
    )

    plt.tight_layout()
    return fig, ax
