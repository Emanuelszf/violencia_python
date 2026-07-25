"""Reconstrói o notebook acadêmico de exploração de CVLI."""

from pathlib import Path
from textwrap import dedent

import nbformat as nbf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "investigando_cvli.ipynb"


def md(source):
    return nbf.v4.new_markdown_cell(dedent(source).strip())


def code(source):
    return nbf.v4.new_code_cell(dedent(source).strip())


cells = [
    md(
        """
        # Investigando os Crimes Violentos Letais Intencionais no Ceará (2009–2025)

        ## Uma análise exploratória territorial para o TCC

        Este notebook descreve a evolução temporal, a distribuição territorial e o perfil das vítimas de **Crimes Violentos Letais Intencionais (CVLI)** no Ceará. A métrica principal é a **taxa de registros por 100 mil habitantes**; números absolutos são mantidos quando respondem melhor à pergunta analítica.

        > **Escopo:** análise descritiva da aba `CVLI`. As abas “Intervenção Policial” e “Unidade Prisional” não entram nesta etapa. Os resultados não estabelecem causalidade nem avaliam políticas públicas.
        """
    ),
    code(
        """
        from pathlib import Path
        import sys
        from textwrap import dedent
        import warnings

        import matplotlib.pyplot as plt
        import numpy as np
        import pandas as pd
        import seaborn as sns
        from IPython.display import HTML, Markdown as IPythonMarkdown, display

        PROJECT_ROOT = Path.cwd().resolve()
        if not (PROJECT_ROOT / "src").exists():
            PROJECT_ROOT = PROJECT_ROOT.parent
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))

        from src.data.clean_data import clean_column_names
        from src.data.load_data import (
            load_cvli_data,
            load_municipality_geodata,
            load_planning_regions,
            load_population_data,
        )
        from src.features.build_features import (
            add_fixed_periods,
            add_population_rates,
            build_municipality_year_panel,
            categorize_rmf_vs_interior,
            create_age_groups,
            extract_temporal_features,
            validate_cvli_data,
        )
        from src.visualization import (
            plot_age_distribution,
            plot_crime_nature_bar,
            plot_education_distribution,
            plot_monthly_heatmap,
            plot_municipality_period_maps,
            plot_race_distribution,
            plot_rmf_vs_interior_boxplot,
            plot_seasonality_bars,
            plot_temporal_trend,
            plot_top_municipality_rates,
            set_chart_style,
        )

        warnings.filterwarnings("ignore", category=FutureWarning)
        pd.set_option("display.max_columns", 30)
        pd.set_option("display.float_format", lambda value: f"{value:,.2f}")
        set_chart_style()

        def Markdown(text):
            return IPythonMarkdown(dedent(text).strip())

        PERIODOS = ["2009–2012", "2013–2016", "2017–2020", "2021–2025"]
        """
    ),
    md(
        r"""
        ## Quais dados sustentam esta análise?

        Cada linha da aba `CVLI` é tratada como um **registro de ocorrência/vítima**, conforme disponibilizado pela SSPDS/CE. Como a base não contém um identificador único de ocorrência, linhas integralmente iguais são diagnosticadas, mas **não são removidas automaticamente**.

        A taxa municipal anual é calculada por:

        \[
        \text{taxa de CVLI}_{m,t} =
        \frac{\text{registros de CVLI}_{m,t}}{\text{população}_{m,t}}
        \times 100.000
        \]

        Para o Ceará ou grupos de municípios, o numerador e o denominador são somados antes do cálculo. Isso evita atribuir o mesmo peso a municípios de tamanhos populacionais muito diferentes.

        **Denominadores populacionais**

        - 2009, 2011–2021 e 2024–2025: estimativas do IBGE;
        - 2010 e 2022: Censos Demográficos;
        - 2023: valor imputado pela média aritmética das populações municipais de 2020, 2021 e 2022.

        A malha municipal de 2020 é obtida pelo pacote `geobr` e serve somente como camada geográfica. A execução requer `pandas`, `openpyxl`, `matplotlib`, `seaborn`, `geopandas`, `geobr`, `nbformat` e `nbclient`.
        """
    ),
    code(
        """
        cvli = clean_column_names(load_cvli_data(sheet_name=0))
        planejamento_bruto = load_planning_regions()
        populacao = load_population_data()

        print(f"Base de CVLI: {len(cvli):,} registros e {cvli.shape[1]} variáveis")
        print(f"População: {len(populacao):,} combinações município–ano")
        display(cvli.head())

        estrutura = pd.DataFrame(
            {
                "variavel": cvli.columns,
                "tipo": cvli.dtypes.astype(str).values,
                "nao_nulos": cvli.notna().sum().values,
                "valores_unicos": cvli.nunique(dropna=False).values,
            }
        )
        display(estrutura)
        """
    ),
    md(
        """
        ## Os dados são consistentes e completos?

        A validação abaixo verifica datas, período, municípios, duplicidades, valores ausentes, cobertura populacional e a chave do painel. Os registros duplicados são reportados para auditoria, sem deduplicação.
        """
    ),
    code(
        """
        diagnostico = validate_cvli_data(cvli, planejamento_bruto)

        resumo_base = pd.DataFrame(
            {
                "verificação": [
                    "Registros brutos",
                    "Municípios observados",
                    "Primeiro ano",
                    "Último ano",
                    "Datas inválidas",
                    "Divergências entre Data e ano",
                    "Linhas integralmente duplicadas",
                    "Municípios sem vínculo regional",
                ],
                "resultado": [
                    diagnostico["rows"],
                    diagnostico["municipalities"],
                    min(diagnostico["years"]),
                    max(diagnostico["years"]),
                    diagnostico["date_invalid_count"],
                    diagnostico["year_date_mismatch_count"],
                    diagnostico["duplicate_rows"],
                    len(diagnostico["municipalities_not_in_planning"]),
                ],
            }
        )
        display(resumo_base)
        display(diagnostico["missing"])

        duplicados_exemplo = cvli[cvli.duplicated(keep=False)].head(10)
        if not duplicados_exemplo.empty:
            display(Markdown("**Exemplo de linhas integralmente duplicadas — mantidas na análise:**"))
            display(duplicados_exemplo)

        assert diagnostico["rows"] == 59_340
        assert diagnostico["municipalities"] == 184
        assert diagnostico["years"] == list(range(2009, 2026))
        assert diagnostico["date_invalid_count"] == 0
        assert diagnostico["year_date_mismatch_count"] == 0
        assert not diagnostico["municipalities_not_in_planning"]
        """
    ),
    code(
        """
        painel_cvli = build_municipality_year_panel(cvli, planejamento_bruto)
        painel_cvli = add_fixed_periods(painel_cvli)
        painel_cvli = add_population_rates(painel_cvli, populacao)
        painel_cvli = categorize_rmf_vs_interior(painel_cvli)

        colunas_painel = [
            "code_muni",
            "municipio",
            "regiao_planejamento",
            "grupo",
            "ano",
            "periodo",
            "total_cvli",
            "tem_registro",
            "populacao",
            "tipo_populacao",
            "fonte_populacao",
            "taxa_cvli_100k",
        ]
        painel_cvli = painel_cvli[colunas_painel].sort_values(
            ["code_muni", "ano"]
        ).reset_index(drop=True)

        validacao_painel = pd.DataFrame(
            {
                "verificação": [
                    "Combinações município–ano",
                    "Municípios no painel",
                    "Anos no painel",
                    "Chaves município–ano duplicadas",
                    "Registros recuperados pelo painel",
                    "Populações ausentes ou não positivas",
                    "Regiões de planejamento",
                ],
                "resultado": [
                    len(painel_cvli),
                    painel_cvli["code_muni"].nunique(),
                    painel_cvli["ano"].nunique(),
                    painel_cvli.duplicated(["code_muni", "ano"]).sum(),
                    painel_cvli["total_cvli"].sum(),
                    (
                        painel_cvli["populacao"].isna()
                        | painel_cvli["populacao"].le(0)
                    ).sum(),
                    painel_cvli["regiao_planejamento"].nunique(),
                ],
            }
        )
        display(validacao_painel)
        display(painel_cvli.head())

        assert len(painel_cvli) == 184 * 17 == 3_128
        assert painel_cvli["total_cvli"].sum() == len(cvli) == 59_340
        assert not painel_cvli.duplicated(["code_muni", "ano"]).any()
        assert painel_cvli["populacao"].notna().all()
        assert painel_cvli["populacao"].gt(0).all()
        assert painel_cvli["regiao_planejamento"].notna().all()
        assert painel_cvli["regiao_planejamento"].nunique() == 14
        """
    ),
    code(
        """
        proveniencia_populacao = (
            populacao.groupby(
                ["tipo_populacao", "fonte_populacao"], as_index=False
            )
            .agg(
                anos=("ano", lambda values: ", ".join(map(str, sorted(values.unique())))),
                municipios_ano=("ano", "size"),
            )
        )
        display(proveniencia_populacao)

        pop_2020_2023 = populacao[
            populacao["ano"].isin([2020, 2021, 2022, 2023])
        ].pivot(
            index="code_muni", columns="ano", values="populacao"
        )
        media_3_anos_anteriores = pop_2020_2023[[2020, 2021, 2022]].mean(axis=1)
        imputacao_2023_confere = bool(
            np.allclose(
                pop_2020_2023[2023],
                media_3_anos_anteriores,
                rtol=0,
                atol=1e-9,
            )
        )
        municipios_diferentes_de_2022 = int(
            (~np.isclose(pop_2020_2023[2023], pop_2020_2023[2022])).sum()
        )
        display(
            Markdown(
                f"**Imputação de 2023:** foi aplicada, em cada município, a média aritmética "
                f"das populações de 2020, 2021 e 2022. O cálculo "
                f"{'foi reproduzido corretamente' if imputacao_2023_confere else 'não foi reproduzido corretamente'} "
                f"e gera valor diferente do Censo 2022 em **{municipios_diferentes_de_2022} municípios**. "
                "O arquivo TCU de 2023 não participa do cálculo."
            )
        )
        assert imputacao_2023_confere
        """
    ),
    code(
        """
        idade_numerica = pd.to_numeric(cvli["idade_da_vítima"], errors="coerce")
        idade_valida = idade_numerica.between(0, 120)

        def mascara_informacao_valida(serie):
            texto = serie.astype("string").str.strip().str.casefold()
            categorias_ausentes = {
                "não informada",
                "não informado",
                "ignorado",
                "",
            }
            return texto.notna() & ~texto.isin(categorias_ausentes)

        escolaridade_valida = mascara_informacao_valida(
            cvli["escolaridade_da_vítima"]
        )
        raca_valida = mascara_informacao_valida(cvli["raça_da_vítima"])

        cobertura_demografica = pd.DataFrame(
            {
                "campo": ["Idade", "Escolaridade", "Raça/cor"],
                "registros_validos": [
                    idade_valida.sum(),
                    escolaridade_valida.sum(),
                    raca_valida.sum(),
                ],
            }
        )
        cobertura_demografica["total_registros"] = len(cvli)
        cobertura_demografica["cobertura_pct"] = (
            cobertura_demografica["registros_validos"]
            / cobertura_demografica["total_registros"]
            * 100
        )
        display(cobertura_demografica.round({"cobertura_pct": 2}))
        """
    ),
    code(
        """
        df_plot_temporal = (
            painel_cvli.groupby("ano", as_index=False)
            .agg(
                total_cvli=("total_cvli", "sum"),
                populacao=("populacao", "sum"),
            )
        )
        df_plot_temporal["taxa_cvli_100k"] = (
            df_plot_temporal["total_cvli"]
            / df_plot_temporal["populacao"]
            * 100_000
        )
        df_plot_temporal["variacao_pct"] = (
            df_plot_temporal["taxa_cvli_100k"].pct_change() * 100
        )

        pico_serie = df_plot_temporal.loc[
            df_plot_temporal["taxa_cvli_100k"].idxmax()
        ]
        natureza_principal = cvli["natureza"].value_counts().index[0]
        natureza_principal_total = cvli["natureza"].value_counts().iloc[0]

        display(
            Markdown(
                f'''
                ## Em poucas linhas

                - A base reúne **{len(cvli):,} registros**, **184 municípios** e **17 anos**, sem lacunas no painel município–ano.
                - O pico estadual ocorreu em **{int(pico_serie['ano'])}**, com **{pico_serie['taxa_cvli_100k']:.1f} registros por 100 mil habitantes** e **{int(pico_serie['total_cvli']):,} registros**.
                - **{natureza_principal.title()}** representa **{natureza_principal_total / len(cvli) * 100:.1f}%** dos registros.
                - A cobertura de raça/cor é de apenas **{raca_valida.mean() * 100:.1f}%**; resultados desse campo devem ser interpretados com cautela.
                '''
            )
        )
        """
    ),
    md(
        """
        ## Como o CVLI evoluiu ao longo do tempo?

        A taxa estadual usa o total anual de registros dividido pela soma da população dos 184 municípios. O painel inferior mostra a variação percentual da própria taxa em relação ao ano anterior.
        """
    ),
    code(
        """
        display(
            df_plot_temporal.assign(
                taxa_cvli_100k=df_plot_temporal["taxa_cvli_100k"].round(2),
                variacao_pct=df_plot_temporal["variacao_pct"].round(2),
            )
        )

        fig_temporal, _ = plot_temporal_trend(df_plot_temporal)
        plt.show()

        minimo_serie = df_plot_temporal.loc[
            df_plot_temporal["taxa_cvli_100k"].idxmin()
        ]
        display(
            Markdown(
                f'''
                **Leitura:** a maior taxa da série foi observada em **{int(pico_serie['ano'])}**
                ({pico_serie['taxa_cvli_100k']:.1f} por 100 mil), enquanto a menor ocorreu em
                **{int(minimo_serie['ano'])}** ({minimo_serie['taxa_cvli_100k']:.1f}).
                As oscilações são descritivas e, isoladamente, não identificam seus determinantes.
                '''
            )
        )
        """
    ),
    md(
        """
        ## Quais municípios apresentaram as maiores taxas médias de CVLI?

        A comparação utiliza a média simples das 17 taxas anuais de cada município, incluindo anos com zero registro. Não há supressão por tamanho populacional; por isso, o volume acumulado e a população média aparecem como contexto.
        """
    ),
    code(
        """
        painel_com_rank = painel_cvli.copy()
        painel_com_rank["posicao_anual"] = painel_com_rank.groupby("ano")[
            "taxa_cvli_100k"
        ].rank(method="min", ascending=False)

        persistencia_top10 = (
            painel_com_rank[painel_com_rank["posicao_anual"] <= 10]
            .groupby(["code_muni", "municipio"], as_index=False)
            .agg(
                anos_no_top10=("ano", "nunique"),
                melhor_posicao=("posicao_anual", "min"),
                primeiro_ano_top10=("ano", "min"),
                ultimo_ano_top10=("ano", "max"),
            )
        )

        ranking_taxas = (
            painel_cvli.groupby(
                ["code_muni", "municipio", "regiao_planejamento"], as_index=False
            )
            .agg(
                taxa_media_cvli_100k=("taxa_cvli_100k", "mean"),
                total_cvli=("total_cvli", "sum"),
                populacao_media=("populacao", "mean"),
                anos_com_registro=("tem_registro", "sum"),
            )
            .merge(
                persistencia_top10,
                on=["code_muni", "municipio"],
                how="left",
                validate="one_to_one",
            )
            .sort_values("taxa_media_cvli_100k", ascending=False)
            .reset_index(drop=True)
        )
        ranking_taxas["posicao_geral"] = np.arange(1, len(ranking_taxas) + 1)
        ranking_taxas["anos_no_top10"] = (
            ranking_taxas["anos_no_top10"].fillna(0).astype(int)
        )

        colunas_ranking = [
            "posicao_geral",
            "municipio",
            "regiao_planejamento",
            "taxa_media_cvli_100k",
            "total_cvli",
            "populacao_media",
            "anos_com_registro",
            "anos_no_top10",
        ]
        display(ranking_taxas[colunas_ranking].head(20).round(2))

        fig_ranking, _ = plot_top_municipality_rates(ranking_taxas, top_n=20)
        plt.show()

        tabela_completa = ranking_taxas[colunas_ranking].round(2).to_html(
            index=False,
            classes="dataframe",
            border=0,
        )
        display(
            HTML(
                "<details><summary><strong>Abrir ranking completo dos 184 municípios</strong></summary>"
                + tabela_completa
                + "</details>"
            )
        )

        lider_taxa = ranking_taxas.iloc[0]
        lider_persistente = ranking_taxas.sort_values(
            ["anos_no_top10", "melhor_posicao"],
            ascending=[False, True],
        ).iloc[0]
        display(
            Markdown(
                f'''
                **Leitura:** **{lider_taxa['municipio']}** apresenta a maior taxa média anual
                ({lider_taxa['taxa_media_cvli_100k']:.1f} por 100 mil). Em persistência,
                **{lider_persistente['municipio']}** aparece entre as dez maiores taxas em
                **{int(lider_persistente['anos_no_top10'])} dos 17 anos**.
                '''
            )
        )
        """
    ),
    md(
        """
        ## Como a taxa de CVLI se distribui espacialmente?

        Os mapas comparam a média das taxas municipais anuais em quatro blocos. A escala é comum entre os painéis, permitindo comparação visual direta. O volume acumulado continua disponível para medir concentração de registros.
        """
    ),
    code(
        """
        metricas_periodo = (
            painel_cvli.groupby(
                [
                    "periodo",
                    "code_muni",
                    "municipio",
                    "regiao_planejamento",
                ],
                as_index=False,
                observed=False,
            )
            .agg(
                taxa_media_cvli_100k=("taxa_cvli_100k", "mean"),
                total_cvli=("total_cvli", "sum"),
                media_anual_registros=("total_cvli", "mean"),
                anos_com_registro=("tem_registro", "sum"),
            )
        )
        metricas_periodo["posicao_taxa"] = metricas_periodo.groupby("periodo")[
            "taxa_media_cvli_100k"
        ].rank(method="min", ascending=False)
        metricas_periodo["participacao_registros_pct"] = (
            metricas_periodo["total_cvli"]
            / metricas_periodo.groupby("periodo")["total_cvli"].transform("sum")
            * 100
        )

        lideres_periodo = (
            metricas_periodo.sort_values(
                ["periodo", "taxa_media_cvli_100k"],
                ascending=[True, False],
            )
            .groupby("periodo", sort=False, observed=False)
            .head(5)
        )
        display(
            lideres_periodo[
                [
                    "periodo",
                    "posicao_taxa",
                    "municipio",
                    "taxa_media_cvli_100k",
                    "total_cvli",
                ]
            ].round(2)
        )

        concentracao_periodo = []
        for periodo, grupo_periodo in metricas_periodo.groupby(
            "periodo", sort=False, observed=False
        ):
            ordenado = grupo_periodo.sort_values("total_cvli", ascending=False)
            total_periodo = ordenado["total_cvli"].sum()
            concentracao_periodo.append(
                {
                    "periodo": periodo,
                    "total_cvli": int(total_periodo),
                    "municipios_com_registro": int(
                        (ordenado["total_cvli"] > 0).sum()
                    ),
                    "participacao_top5_pct": (
                        ordenado.head(5)["total_cvli"].sum() / total_periodo * 100
                    ),
                    "participacao_top10_pct": (
                        ordenado.head(10)["total_cvli"].sum() / total_periodo * 100
                    ),
                }
            )
        concentracao_periodo = pd.DataFrame(concentracao_periodo)
        display(concentracao_periodo.round(2))

        posicoes_periodo = metricas_periodo.pivot(
            index=["code_muni", "municipio"],
            columns="periodo",
            values="posicao_taxa",
        ).reset_index()
        posicoes_periodo["mudanca_2009_2012_para_2021_2025"] = (
            posicoes_periodo["2009–2012"] - posicoes_periodo["2021–2025"]
        )
        maiores_subidas = posicoes_periodo.nlargest(
            10, "mudanca_2009_2012_para_2021_2025"
        )
        display(
            Markdown(
                "**Maiores avanços no ranking de taxa média entre o primeiro e o último bloco:**"
            )
        )
        display(maiores_subidas.round(0))
        """
    ),
    code(
        """
        geo_ce = load_municipality_geodata(state="CE", year=2020)
        geo_ce["code_muni"] = geo_ce["code_muni"].astype("Int64")

        cobertura_mapa = (
            metricas_periodo.groupby("periodo", observed=False)["code_muni"]
            .nunique()
            .rename("municipios_nos_dados")
            .reset_index()
        )
        cobertura_mapa["municipios_na_malha"] = geo_ce["code_muni"].nunique()
        cobertura_mapa["diferenca"] = (
            cobertura_mapa["municipios_na_malha"]
            - cobertura_mapa["municipios_nos_dados"]
        )
        display(cobertura_mapa)

        assert geo_ce["code_muni"].nunique() == 184
        assert cobertura_mapa["municipios_nos_dados"].eq(184).all()
        assert cobertura_mapa["diferenca"].eq(0).all()

        fig_mapas, _ = plot_municipality_period_maps(
            geo_ce,
            metricas_periodo,
            periods=PERIODOS,
            value_column="taxa_media_cvli_100k",
        )
        plt.show()
        """
    ),
    code(
        """
        resumo_regional = (
            painel_cvli.groupby(
                ["periodo", "regiao_planejamento"],
                as_index=False,
                observed=False,
            )
            .agg(
                total_cvli=("total_cvli", "sum"),
                populacao=("populacao", "sum"),
            )
        )
        resumo_regional["taxa_agregada_cvli_100k"] = (
            resumo_regional["total_cvli"]
            / resumo_regional["populacao"]
            * 100_000
        )
        resumo_regional["participacao_periodo_pct"] = (
            resumo_regional["total_cvli"]
            / resumo_regional.groupby("periodo")["total_cvli"].transform("sum")
            * 100
        )
        display(
            HTML(
                "<details><summary><strong>Abrir resultados das 14 regiões por período</strong></summary>"
                + resumo_regional.round(2).to_html(index=False, border=0)
                + "</details>"
            )
        )
        """
    ),
    md(
        """
        ## Qual é a natureza de crime mais proeminente?

        Como a variável descreve categorias de crime dentro do próprio conjunto de CVLI, esta comparação usa **números absolutos**, acompanhados das respectivas participações.
        """
    ),
    code(
        """
        distribuicao_natureza = (
            cvli["natureza"]
            .value_counts(dropna=False)
            .rename_axis("natureza")
            .reset_index(name="total")
        )
        distribuicao_natureza["pct"] = (
            distribuicao_natureza["total"]
            / distribuicao_natureza["total"].sum()
            * 100
        )
        display(distribuicao_natureza.round({"pct": 2}))

        fig_natureza, _ = plot_crime_nature_bar(distribuicao_natureza)
        plt.show()

        natureza_lider = distribuicao_natureza.iloc[0]
        display(
            Markdown(
                f"**Leitura:** {natureza_lider['natureza'].title()} concentra "
                f"**{int(natureza_lider['total']):,} registros "
                f"({natureza_lider['pct']:.1f}%)** no período."
            )
        )
        """
    ),
    md(
        """
        ## Qual é o perfil das vítimas?

        Os percentuais são calculados somente entre registros com informação válida. A cobertura de cada campo aparece no rodapé do respectivo gráfico e deve orientar a força da interpretação.
        """
    ),
    code(
        """
        cvli_perfil = create_age_groups(cvli)

        distribuicao_idade = (
            cvli_perfil.loc[cvli_perfil["faixa_etaria"].notna(), "faixa_etaria"]
            .value_counts(sort=False)
            .rename_axis("faixa_etaria")
            .reset_index(name="total")
        )
        distribuicao_idade["pct"] = (
            distribuicao_idade["total"] / distribuicao_idade["total"].sum() * 100
        )

        distribuicao_raca = (
            cvli.loc[raca_valida, "raça_da_vítima"]
            .value_counts()
            .rename_axis("raca")
            .reset_index(name="total")
        )
        distribuicao_raca["pct"] = (
            distribuicao_raca["total"] / distribuicao_raca["total"].sum() * 100
        )

        ordem_escolaridade = [
            "Não Alfabetizado",
            "Alfabetizado",
            "Ensino Fundamental Incompleto",
            "Ensino Fundamental Completo",
            "Ensino Médio Incompleto",
            "Ensino Médio Completo",
            "Superior Incompleto",
            "Superior Completo",
        ]
        distribuicao_escolaridade = (
            cvli.loc[escolaridade_valida, "escolaridade_da_vítima"]
            .value_counts()
            .reindex(ordem_escolaridade, fill_value=0)
            .rename_axis("escolaridade")
            .reset_index(name="total")
        )
        distribuicao_escolaridade["pct"] = (
            distribuicao_escolaridade["total"]
            / distribuicao_escolaridade["total"].sum()
            * 100
        )

        display(distribuicao_idade.round({"pct": 2}))
        display(distribuicao_raca.round({"pct": 2}))
        display(distribuicao_escolaridade.round({"pct": 2}))
        """
    ),
    code(
        """
        fig_idade, _ = plot_age_distribution(
            distribuicao_idade,
            valid_count=int(idade_valida.sum()),
            total_count=len(cvli),
        )
        plt.show()
        """
    ),
    code(
        """
        fig_raca, _ = plot_race_distribution(
            distribuicao_raca,
            valid_count=int(raca_valida.sum()),
            total_count=len(cvli),
        )
        plt.show()
        """
    ),
    code(
        """
        fig_escolaridade, _ = plot_education_distribution(
            distribuicao_escolaridade,
            valid_count=int(escolaridade_valida.sum()),
            total_count=len(cvli),
        )
        plt.show()
        """
    ),
    code(
        """
        faixa_lider = distribuicao_idade.loc[distribuicao_idade["total"].idxmax()]
        raca_lider = distribuicao_raca.iloc[0]
        escolaridade_lider = distribuicao_escolaridade.loc[
            distribuicao_escolaridade["total"].idxmax()
        ]
        display(
            Markdown(
                f'''
                **Leitura conjunta:** entre idades válidas, a faixa **{faixa_lider['faixa_etaria']}**
                concentra {faixa_lider['pct']:.1f}% dos registros. Entre os registros válidos
                de raça/cor, **{raca_lider['raca']}** representa {raca_lider['pct']:.1f}%.
                Em escolaridade válida, a categoria mais frequente é
                **{escolaridade_lider['escolaridade']}** ({escolaridade_lider['pct']:.1f}%).

                **Limitação central:** raça/cor tem somente {raca_valida.mean() * 100:.1f}% de
                cobertura; sua distribuição não deve ser generalizada automaticamente para todas
                as vítimas.
                '''
            )
        )
        """
    ),
    md(
        """
        ## Como as taxas se distribuem entre a Grande Fortaleza e o Interior?

        “RMF” corresponde à Região de Planejamento **Grande Fortaleza**, composta por 19 municípios. O Interior reúne os outros 165. Cada ponto no gráfico representa uma observação município–ano; todos os valores são mantidos.
        """
    ),
    code(
        """
        resumo_rmf_interior = (
            painel_cvli.groupby(
                ["periodo", "grupo"], as_index=False, observed=False
            )
            .agg(
                total_cvli=("total_cvli", "sum"),
                populacao=("populacao", "sum"),
                taxa_mediana_municipio_ano=("taxa_cvli_100k", "median"),
                taxa_media_municipio_ano=("taxa_cvli_100k", "mean"),
                observacoes_municipio_ano=("code_muni", "size"),
            )
        )
        resumo_rmf_interior["taxa_agregada_cvli_100k"] = (
            resumo_rmf_interior["total_cvli"]
            / resumo_rmf_interior["populacao"]
            * 100_000
        )
        display(resumo_rmf_interior.round(2))

        fig_boxplot, _ = plot_rmf_vs_interior_boxplot(painel_cvli)
        plt.show()

        diferenca_mediana = resumo_rmf_interior.pivot(
            index="periodo",
            columns="grupo",
            values="taxa_mediana_municipio_ano",
        )
        diferenca_mediana["diferenca_rmf_menos_interior"] = (
            diferenca_mediana["RMF (Grande Fortaleza)"]
            - diferenca_mediana["Interior"]
        )
        display(
            Markdown(
                "As caixas comparam distribuições municipais, enquanto a coluna "
                "`taxa_agregada_cvli_100k` pondera cada conjunto por sua população. "
                "As duas medidas respondem a perguntas diferentes e não devem ser confundidas."
            )
        )
        display(diferenca_mediana.round(2))
        """
    ),
    md(
        """
        ## Existe sazonalidade nos registros de CVLI?

        Esta seção usa números absolutos por mês e dia da semana. O objetivo é descrever regularidades de calendário, não atribuir causas. Todos os anos, inclusive 2025, possuem registros nos 12 meses.
        """
    ),
    code(
        """
        cvli_temporal = extract_temporal_features(cvli)
        meses_por_ano = cvli_temporal.groupby("ano")["mes"].nunique()
        assert meses_por_ano.eq(12).all()

        registros_mes_ano = (
            cvli_temporal.groupby(["mes", "ano"])
            .size()
            .rename("total")
            .reset_index()
        )
        heatmap_mensal = registros_mes_ano.pivot(
            index="mes", columns="ano", values="total"
        ).fillna(0)
        heatmap_mensal = heatmap_mensal.reindex(range(1, 13))
        heatmap_mensal.index = [
            "Jan",
            "Fev",
            "Mar",
            "Abr",
            "Mai",
            "Jun",
            "Jul",
            "Ago",
            "Set",
            "Out",
            "Nov",
            "Dez",
        ]

        fig_heatmap, _ = plot_monthly_heatmap(heatmap_mensal)
        plt.show()
        """
    ),
    code(
        """
        distribuicao_mes = (
            cvli_temporal.groupby(["mes", "mes_nome"], as_index=False)
            .size()
            .rename(columns={"size": "total"})
            .sort_values("mes")
        )
        distribuicao_dia = (
            cvli_temporal.groupby(
                ["dia_semana", "dia_nome"], as_index=False
            )
            .size()
            .rename(columns={"size": "total"})
            .sort_values("dia_semana")
        )

        fig_calendario, _ = plot_seasonality_bars(
            distribuicao_mes, distribuicao_dia
        )
        plt.show()

        pico_mes_ano = registros_mes_ano.loc[registros_mes_ano["total"].idxmax()]
        mes_lider = distribuicao_mes.loc[distribuicao_mes["total"].idxmax()]
        dia_lider = distribuicao_dia.loc[distribuicao_dia["total"].idxmax()]
        display(
            Markdown(
                f'''
                **Leitura:** o maior número mensal da série ocorreu no mês
                **{int(pico_mes_ano['mes']):02d}/{int(pico_mes_ano['ano'])}**,
                com **{int(pico_mes_ano['total']):,} registros**. No acumulado,
                **{mes_lider['mes_nome']}** é o mês com mais registros e
                **{dia_lider['dia_nome']}** é o dia da semana mais frequente.

                A comparação mensal não corrige o número de dias de cada mês nem mudanças
                populacionais; serve apenas como exploração inicial.
                '''
            )
        )
        """
    ),
    md(
        """
        ## O que esta exploração permite concluir — e o que ainda não permite?

        A síntese abaixo é produzida a partir dos objetos efetivamente calculados no notebook.
        """
    ),
    code(
        """
        display(
            Markdown(
                f'''
                ### Síntese descritiva

                1. A série estadual é fortemente oscilante: o pico foi
                   **{int(pico_serie['ano'])} ({pico_serie['taxa_cvli_100k']:.1f} por 100 mil)**,
                   e o menor valor ocorreu em **{int(minimo_serie['ano'])}
                   ({minimo_serie['taxa_cvli_100k']:.1f})**.
                2. **{lider_taxa['municipio']}** lidera a taxa média municipal do período,
                   enquanto **{lider_persistente['municipio']}** apresenta a maior persistência
                   entre as dez taxas anuais mais altas.
                3. **{natureza_lider['natureza'].title()}** corresponde a
                   **{natureza_lider['pct']:.1f}%** dos registros de CVLI.
                4. O perfil etário se concentra em **{faixa_lider['faixa_etaria']}**, mas
                   comparações de raça/cor são limitadas pela cobertura de
                   **{raca_valida.mean() * 100:.1f}%**.
                5. Os mapas e box-plots revelam heterogeneidade territorial relevante,
                   justificando a investigação posterior de autocorrelação e dependência espacial.
                '''
            )
        )
        """
    ),
    md(
        """
        ### Limitações metodológicas

        - A unidade bruta é um registro de ocorrência/vítima; sem identificador único, 1.418 linhas integralmente iguais foram mantidas.
        - A taxa reduz o problema de comparar populações de tamanhos distintos, mas pode oscilar mais em municípios pequenos.
        - O denominador de 2023 é imputado pela média aritmética das populações municipais de 2020, 2021 e 2022; portanto, não é uma estimativa oficial publicada para 2023.
        - A baixa cobertura de raça/cor limita inferências sobre o conjunto das vítimas.
        - A análise é ecológica e descritiva: não controla composição demográfica, dinâmica econômica, políticas públicas ou dependência espacial.
        - Associação temporal ou espacial não implica causalidade.

        ### Próxima etapa econométrica

        O objeto `painel_cvli` está pronto para ser associado a uma matriz de vizinhança municipal. Uma sequência coerente para o TCC é:

        1. testar autocorrelação espacial global com **Moran’s I**;
        2. localizar agrupamentos com **LISA**;
        3. formular variáveis explicativas e efeitos temporais;
        4. comparar modelos em painel e modelos espaciais **SAR, SEM e SDM**;
        5. executar em Python (`libpysal`, `esda`, `spreg`) ou R (`sf`, `spdep`, `spatialreg`), documentando a escolha da matriz de pesos.
        """
    ),
    md(
        """
        ## Todas as validações finais foram atendidas?

        A célula final interrompe a execução se qualquer requisito estrutural deixar de ser satisfeito.
        """
    ),
    code(
        """
        validacoes_finais = {
            "59.340 registros brutos": len(cvli) == 59_340,
            "184 municípios": painel_cvli["code_muni"].nunique() == 184,
            "17 anos completos": painel_cvli["ano"].nunique() == 17,
            "3.128 combinações município–ano": len(painel_cvli) == 3_128,
            "soma do painel igual à base": (
                painel_cvli["total_cvli"].sum() == len(cvli)
            ),
            "chave município–ano única": (
                not painel_cvli.duplicated(["code_muni", "ano"]).any()
            ),
            "população válida em todo o painel": (
                painel_cvli["populacao"].notna().all()
                and painel_cvli["populacao"].gt(0).all()
            ),
            "população de 2023 = média de 2020–2022": imputacao_2023_confere,
            "14 regiões vinculadas": (
                painel_cvli["regiao_planejamento"].notna().all()
                and painel_cvli["regiao_planejamento"].nunique() == 14
            ),
            "184 municípios em cada mapa": (
                cobertura_mapa["municipios_nos_dados"].eq(184).all()
            ),
            "12 meses em todos os anos": meses_por_ano.eq(12).all(),
            "taxa estadual calculada por agregação": np.allclose(
                df_plot_temporal["taxa_cvli_100k"],
                (
                    df_plot_temporal["total_cvli"]
                    / df_plot_temporal["populacao"]
                    * 100_000
                ),
            ),
        }

        tabela_validacoes_finais = pd.DataFrame(
            {
                "verificação": validacoes_finais.keys(),
                "status": [
                    "OK" if resultado else "FALHOU"
                    for resultado in validacoes_finais.values()
                ],
            }
        )
        display(tabela_validacoes_finais)

        assert all(validacoes_finais.values())
        display(
            Markdown(
                "### ✅ Notebook executado integralmente: todas as validações foram aprovadas."
            )
        )
        """
    ),
]


notebook = nbf.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.12",
            "mimetype": "text/x-python",
            "codemirror_mode": {"name": "ipython", "version": 3},
            "pygments_lexer": "ipython3",
            "nbconvert_exporter": "python",
            "file_extension": ".py",
        },
    },
)

nbf.write(notebook, NOTEBOOK_PATH)
print(f"Notebook reconstruído em: {NOTEBOOK_PATH}")
