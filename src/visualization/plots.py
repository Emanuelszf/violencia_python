"""
Módulo para geração e controle estético de visualizações gráficas de alta qualidade.
Garante cumprimento rigoroso das diretrizes de design e storytelling visual.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Paleta de cores institucional e funcional
COLOR_PRIMARY = '#1b4f72'     # Azul Marinho Principal (Destaque/Contexto)
COLOR_ACCENT = '#d35400'      # Laranja/Coral (Alerta/Pico/Máximo)
COLOR_SECONDARY = '#2e86c1'   # Azul Médio
COLOR_MUTED = '#95a5a6'       # Cinza Neutro
COLOR_LIGHT_GRAY = '#ecf0f1'  # Fundo leve
COLOR_PALETTE = ['#1b4f72', '#e67e22', '#27ae60', '#8e44ad', '#c0392b', '#2980b9', '#7f8c8d']

def set_chart_style():
    """
    Define a estética moderna, limpa e profissional para todas as figuras.
    """
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
    plt.rcParams['figure.dpi'] = 120
    plt.rcParams['axes.titlesize'] = 13
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['xtick.labelsize'] = 9.5
    plt.rcParams['ytick.labelsize'] = 9.5

def plot_temporal_trend(df_temporal):
    """
    Gráfico 1: Evolução Histórica Anual dos CVLI no Ceará (2009-2025).
    """
    set_chart_style()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [2.5, 1]}, sharex=True)

    # Gráfico Superior: Linha com pontos e anotações
    ax1.plot(
        df_temporal['ano'], df_temporal['total_cvli'],
        color=COLOR_PRIMARY, linewidth=2.8, marker='o', markersize=6, zorder=4, label='Total Anual'
    )
    
    # Destacar os pontos de máximo e mínimo
    max_row = df_temporal.loc[df_temporal['total_cvli'].idxmax()]
    min_row = df_temporal.loc[df_temporal['total_cvli'].idxmin()]
    
    ax1.scatter([max_row['ano']], [max_row['total_cvli']], color=COLOR_ACCENT, s=90, zorder=5)
    ax1.annotate(
        f"Pico Histórico: {int(max_row['total_cvli']):,}\n({int(max_row['ano'])})",
        (max_row['ano'], max_row['total_cvli']),
        xytext=(max_row['ano'] - 1.5, max_row['total_cvli'] + 250),
        arrowprops=dict(facecolor=COLOR_ACCENT, shrink=0.08, width=1, headwidth=6),
        fontweight='bold', color=COLOR_ACCENT, fontsize=9.5
    )

    for _, row in df_temporal.iterrows():
        if row['ano'] not in [max_row['ano']]:
            ax1.annotate(
                f"{int(row['total_cvli']):,}",
                (row['ano'], row['total_cvli']),
                textcoords="offset points", xytext=(0, 9),
                ha='center', fontsize=8, color='#2c3e50'
            )

    ax1.set_title("Como a violência letal evoluiu no Ceará entre 2009 e 2025?", loc="left", pad=15)
    ax1.set_ylabel("Total de CVLI")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.grid(axis="y", alpha=0.3, linestyle="--")

    # Gráfico Inferior: Variação Percentual Anual (%)
    colors_bar = [COLOR_ACCENT if val > 0 else '#27ae60' for val in df_temporal['variacao_pct'].fillna(0)]
    ax2.bar(df_temporal['ano'], df_temporal['variacao_pct'].fillna(0), color=colors_bar, alpha=0.85, width=0.6)
    ax2.axhline(0, color='black', linewidth=0.8, linestyle='-')
    ax2.set_ylabel("Variação %")
    ax2.set_xlabel("Ano")
    ax2.set_xticks(df_temporal['ano'])
    ax2.set_xticklabels(df_temporal['ano'].astype(int), rotation=45)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(axis="y", alpha=0.3, linestyle="--")

    plt.figtext(
        0.01, -0.02,
        "Fonte: SSPDS/CE. Elaboração própria. CVLI = Crimes Violentos Letais Intencionais.",
        ha="left", fontsize=8.5, style='italic', color='#7f8c8d'
    )
    plt.tight_layout()
    return fig, (ax1, ax2)

def plot_top_municipalities(ranking_muni, top_n=20):
    """
    Gráfico 2: Ranking dos Municípios com Maior Volume de CVLI.
    """
    set_chart_style()
    df_plot_top = ranking_muni.head(top_n).copy()

    fig, ax = plt.subplots(figsize=(11, 8))
    colors = [COLOR_PRIMARY if i == 0 else (COLOR_ACCENT if i < 5 else COLOR_MUTED) for i in range(len(df_plot_top))]

    bars = ax.barh(
        df_plot_top['município'], df_plot_top['total_cvli'],
        color=colors, edgecolor='white', linewidth=0.8, height=0.75
    )

    for i, (val, pct) in enumerate(zip(df_plot_top['total_cvli'], df_plot_top['pct_total'])):
        ax.text(val + 300, i, f"{val:,} ({pct:.1f}%)", va='center', fontsize=9, fontweight='bold' if i == 0 else 'normal')

    ax.invert_yaxis()
    ax.set_title(f"Quais os {top_n} municípios que concentram o maior volume de homicídios?", loc="left", pad=15)
    ax.set_xlabel("Total Acumulado de CVLI (2009–2025)")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    ax.grid(axis="y", visible=False)

    plt.figtext(
        0.01, -0.02,
        f"Fonte: SSPDS/CE. O município de Fortaleza lidera isoladamente com mais de 35% de todos os casos estaduais.",
        ha="left", fontsize=8.5, style='italic', color='#7f8c8d'
    )
    plt.tight_layout()
    return fig, ax

def plot_planning_regions(ranking_regiao):
    """
    Gráfico 3: Comparativo entre todas as 14 Regiões de Planejamento do Ceará.
    """
    set_chart_style()
    df_plot = ranking_regiao.sort_values('total_cvli', ascending=True).copy()

    fig, ax = plt.subplots(figsize=(11, 7))
    colors = [COLOR_PRIMARY if reg == 'Grande Fortaleza' else COLOR_SECONDARY for reg in df_plot['regiao_planejamento']]

    ax.barh(df_plot['regiao_planejamento'], df_plot['total_cvli'], color=colors, height=0.7)

    for i, (val, pct) in enumerate(zip(df_plot['total_cvli'], df_plot['pct_total'])):
        ax.text(val + 400, i, f"{val:,} ({pct:.1f}%)", va='center', fontsize=9)

    ax.set_title("Como a violência se distribui entre as 14 Regiões de Planejamento do Ceará?", loc="left", pad=15)
    ax.set_xlabel("Total Acumulado de CVLI (2009–2025)")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    ax.grid(axis="y", visible=False)

    plt.figtext(
        0.01, -0.02,
        "Fonte: Secretaria do Planejamento e Gestão do Ceará (SEPLAG) / SSPDS. Elaboração própria.",
        ha="left", fontsize=8.5, style='italic', color='#7f8c8d'
    )
    plt.tight_layout()
    return fig, ax

def plot_regional_facet_trends(evolucao_regiao):
    """
    Gráfico 4: Painel de Tendências Anuais por Região de Planejamento.
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

def plot_rmf_vs_interior_trend(evo_grupo):
    """
    Gráfico 5: Comparação Longitudinal RMF (Grande Fortaleza) vs Interior.
    """
    set_chart_style()
    fig, ax = plt.subplots(figsize=(11, 6))

    for grupo, cor in zip(['RMF (Grande Fortaleza)', 'Interior'], [COLOR_PRIMARY, COLOR_ACCENT]):
        dados = evo_grupo[evo_grupo['grupo'] == grupo]
        ax.plot(
            dados['ano'], dados['total_cvli'],
            color=cor, linewidth=2.8, marker='o', markersize=5, label=grupo
        )

    ax.set_title("A violência cresce mais rapidamente na Região Metropolitana de Fortaleza ou no Interior?", loc="left", pad=15)
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
        ha="left", fontsize=8.5, style='italic', color='#7f8c8d'
    )
    plt.tight_layout()
    return fig, ax

def plot_crime_nature_breakdown(dist_natureza, evo_natureza):
    """
    Gráfico 6: Distribuição e Evolução por Natureza do Crime.
    """
    set_chart_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={'width_ratios': [1, 1.6]})

    # Rosca/Donut das proporções
    wedges, texts, autotexts = ax1.pie(
        dist_natureza['total'],
        labels=dist_natureza['natureza'],
        autopct='%1.1f%%',
        pctdistance=0.75,
        colors=COLOR_PALETTE[:len(dist_natureza)],
        startangle=140,
        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
    )
    for t in autotexts:
        t.set_weight('bold')
        t.set_fontsize(9)
    ax1.set_title("Qual a proporção de cada tipo penal?", loc="left")

    # Linhas de evolução por natureza
    for i, nat in enumerate(dist_natureza['natureza']):
        sub = evo_natureza[evo_natureza['natureza'] == nat]
        ax2.plot(sub['ano'], sub['total'], marker='o', label=nat, color=COLOR_PALETTE[i], linewidth=2.2)

    ax2.set_title("Como cada natureza de crime oscilou ao longo do período?", loc="left")
    ax2.set_xlabel("Ano")
    ax2.set_ylabel("Total de Casos")
    ax2.legend(fontsize=8.5, frameon=True)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(axis="y", alpha=0.3)

    fig.suptitle("Qual é a composição jurídica/penal dos Crimes Violentos Letais Intencionais?", fontsize=14, fontweight='bold', x=0.01, ha='left', y=1.02)
    plt.tight_layout()
    return fig, (ax1, ax2)

def plot_victim_demographics(dist_idade, dist_esc, dist_raca):
    """
    Gráfico 7: Perfil Demográfico das Vítimas (Subconjunto Com Registros Informados).
    """
    set_chart_style()
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))

    # 1. Faixa etária
    ax1 = axes[0]
    ax1.barh(dist_idade['faixa_etaria'].astype(str), dist_idade['total'], color=COLOR_PRIMARY)
    ax1.set_title("Por faixa etária?", loc="left")
    ax1.invert_yaxis()
    for i, (val, pct) in enumerate(zip(dist_idade['total'], dist_idade['pct'])):
        ax1.text(val + 50, i, f"{pct:.1f}%", va='center', fontsize=9)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # 2. Escolaridade
    ax2 = axes[1]
    ax2.barh(dist_esc['escolaridade'], dist_esc['total'], color=COLOR_SECONDARY)
    ax2.set_title("Por nível de escolaridade?", loc="left")
    ax2.invert_yaxis()
    for i, (val, pct) in enumerate(zip(dist_esc['total'], dist_esc['pct'])):
        ax2.text(val + 20, i, f"{pct:.1f}%", va='center', fontsize=9)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # 3. Raça
    ax3 = axes[2]
    ax3.barh(dist_raca['raca'], dist_raca['total'], color=COLOR_ACCENT)
    ax3.set_title("Por pertencimento racial?", loc="left")
    ax3.invert_yaxis()
    for i, (val, pct) in enumerate(zip(dist_raca['total'], dist_raca['pct'])):
        ax3.text(val + 20, i, f"{pct:.1f}%", va='center', fontsize=9)
    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)

    fig.suptitle(
        "Quem são as vítimas dos homicídios no Ceará? (Dados disponíveis)",
        fontsize=14, fontweight='bold', x=0.01, ha='left', y=1.02
    )
    plt.figtext(
        0.01, -0.03,
        "Nota: Análise restrita às ocorrências com dados válidos informados pelos órgãos de segurança.",
        ha="left", fontsize=8.5, style='italic', color='#7f8c8d'
    )
    plt.tight_layout()
    return fig, axes

def plot_monthly_heatmap(heatmap_pivot):
    """
    Gráfico 8: Heatmap Mensal de Sazonalidade dos Homicídios (Mês x Ano).
    """
    set_chart_style()
    fig, ax = plt.subplots(figsize=(15, 6))

    sns.heatmap(
        heatmap_pivot,
        cmap='YlOrRd',
        annot=True,
        fmt='.0f',
        linewidths=0.5,
        ax=ax,
        cbar_kws={'label': 'Total de CVLI'},
        annot_kws={'size': 8.5}
    )

    ax.set_title("Existe sazonalidade ou meses atípicos de pico na ocorrência dos crimes no Ceará?", loc="left", pad=15)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Mês")

    plt.figtext(
        0.01, -0.03,
        "Fonte: SSPDS/CE. Tons mais escuros representam meses de maior intensidade de ocorrências.",
        ha="left", fontsize=8.5, style='italic', color='#7f8c8d'
    )
    plt.tight_layout()
    return fig, ax

def plot_seasonality_bars(dist_mes, dist_dia):
    """
    Gráfico 9: Padrão Sazonal por Mês do Ano e por Dia da Semana.
    """
    set_chart_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Por mês
    ax1.bar(dist_mes['mes_nome'], dist_mes['total'], color=COLOR_PRIMARY, width=0.6)
    ax1.set_title("Distribuição total por mês do ano", loc="left")
    ax1.set_ylabel("Total de CVLI")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.grid(axis="y", alpha=0.3)

    # Por dia da semana
    ordem_dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    dist_dia_ord = dist_dia.set_index('dia_nome').loc[ordem_dias].reset_index()
    colors_dia = [COLOR_ACCENT if d in ['Sáb', 'Dom'] else COLOR_PRIMARY for d in dist_dia_ord['dia_nome']]

    ax2.bar(dist_dia_ord['dia_nome'], dist_dia_ord['total'], color=colors_dia, width=0.6)
    ax2.set_title("Distribuição por dia da semana (destaque: fins de semana)", loc="left")
    ax2.set_ylabel("Total de CVLI")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(axis="y", alpha=0.3)

    fig.suptitle("Em quais períodos temporais e dias da semana a violência se intensifica?", fontsize=14, fontweight='bold', x=0.01, ha='left', y=1.02)
    plt.tight_layout()
    return fig, (ax1, ax2)
