import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sympy.printing.pretty.pretty_symbology import line_width

from libmig_eval.paper.paper_data import load_per_mig_results
from libmig_eval.util import Paths


class ChartPlotter:
    def __init__(self):
        self.per_mig_result = load_per_mig_results()

    def ablation_violins_overlapping(self):
        df = self.per_mig_result
        # drop negative values
        df = df[df["llmmig_correctness"] >= 0]

        df = df[["llmmig_correctness", "merge_skipped_correctness", "async_transform_correctness"]].copy()
        # rename columns for clarity
        df.rename(columns={
            "llmmig_correctness": "llm",
            "merge_skipped_correctness": "merge",
            "async_transform_correctness": "async"
        }, inplace=True)

        fig = go.Figure()

        llm_line_color = "#00008B"  # Dark Blue
        llm_fill_color = "rgba(70, 130, 180, .8)"  # Steel Blue
        merge_line_color = "#39FF14"  # Dark Red
        merge_fill_color = "rgba(255, 99, 71, .0)"  # Tomato
        async_line_color = "#FFFF00"  # Dark Cyan
        async_fill_color = "rgba(0, 255, 255, .0)"  # Cyan

        def __add_violin(y_col, name, line_color, fill_color):
            fig.add_trace(go.Violin(
                y=df[y_col],
                name=name,
                line_color=line_color,
                fillcolor=fill_color,
                box_visible=False,
                meanline_visible=True,
                spanmode="hard",
                x=[""] * len(df),
                points=False,
            ))

        def __add_median_line(y_col, line_color):
            median_value = df[y_col].median()
            fig.add_hline(
                y=median_value,
                line_color=line_color,
                line_width=2,
            )

        __add_violin("llm", "LLM Only", llm_line_color, llm_fill_color)
        __add_violin("merge", "LLM+Merge", merge_line_color, merge_fill_color)
        __add_violin("async", "LLM+Merge+Async", async_line_color, async_fill_color)
        __add_median_line("llm", llm_line_color)
        __add_median_line("merge", merge_line_color)
        __add_median_line("async", async_line_color)

        # Update layout
        fig.update_layout(
            title="",
            yaxis_title="Correctness",
            violingap=0,
            violinmode="overlay",
            width=300,
            height=450,
            legend=dict(
                orientation="h",  # Horizontal layout
                yanchor="bottom",  # Anchor to bottom of legend box
                y=1.02,  # Position above the plot
                xanchor="center",
                x=0.5,
                font=dict(size=10),
                itemwidth=30,
            ),
            font=dict(family="Times New Roman", ),
            margin=dict(l=0, r=0, t=0, b=0),
        )
        fig.update_yaxes(title_text="Correctness", tickformat=".0%")
        return fig, f"ablation-violin.pdf", df

    def mig_correctness_violin(self):
        df = self.per_mig_result
        df = df[df["llmmig_has_result"] == True]

        fig = px.violin(
            df, y="overall_correctness",
            range_y=[0, 1],
            box=True,
        )
        fig.update_xaxes(title_text="Number of migrations")
        fig.update_yaxes(title_text="Correctness", tickformat=".0%")

        return fig, "mig-correctness-violin.pdf", df

    def dev_effort_save_violin(self):
        df = self.per_mig_result
        df = df[df["dev_effort_saving"].notnull()]

        fig = px.violin(
            df, y="dev_effort_saving",
            range_y=[0, 1.01],
            box=False,
            width=500,
            height=800,
            points=False,
        )
        fig.update_xaxes(title_text="Number of migrations")
        fig.update_yaxes(title_text="Development Effort Saving", tickformat=".0%")

        for percentile in [25, 50, 75, 90]:
            fig.add_hline(
                y=df["dev_effort_saving"].quantile(percentile / 100),
                line_dash="dash",
                line_width=1,
                annotation_text=f"{percentile}th",
                annotation_position="bottom left",
                line_color="red"
            )

        return fig, "dev-effort-saving-violin.pdf", df

    def dev_effort_save_stacked_bar(self):
        df = self.per_mig_result
        df = df[df["manual_edit_correctness"] == 1.0]
        df = pd.DataFrame({
            "id": df["id"],
            "auto": df["premig_to_best_migloc"].fillna(0.0),
            "manual": df["best_to_manual_edit_migloc"].fillna(0.0),
        })

        df["total"] = df["auto"] + df["manual"]
        auto_label = "MigLOC<sup>′</sup><sub>auto</sub>"
        manual_label = "MigLOC<sup>′</sup><sub>manual</sub>"
        df[auto_label] = df["auto"] / df["total"]
        df[manual_label] = df["manual"] / df["total"]
        df = df.sort_values(auto_label, ascending=False).reset_index(drop=True)

        df_long = df.melt(id_vars="id", value_vars=[auto_label, manual_label],
                          var_name="type", value_name="proportion")

        fig = px.bar(
            df_long,
            x="id",
            y="proportion",
            color="type",
            color_discrete_map={
                auto_label: "steelblue",
                manual_label: "tomato",
            },
            labels={"id": "Migrations", "proportion": "Migration lines of code"},
            width=600,
            height=300,
        )

        for percentile in [50]:
            fig.add_hline(
                y=df[auto_label].quantile(percentile / 100),
                line_dash="dash",
                line_width=1,
                # annotation_text=f"{percentile}th",
                # annotation_position="bottom left",
                line_color="yellow"
            )

        fig.update_yaxes(tickformat=".0%")
        fig.update_layout(
            barmode="stack",
            bargap=0,
            bargroupgap=0,
            legend=dict(
                orientation="h",  # horizontal
                yanchor="bottom",
                y=1.02,  # a bit above the plot
                xanchor="center",
                x=0.5
            ),
            legend_title_text='',
            font=dict(family="Times New Roman"),
            margin=dict(l=10, r=10, t=10, b=10),
        )

        # Optional: remove x-axis labels if not meaningful
        fig.update_layout(xaxis=dict(showticklabels=False))

        for i, row in df.iterrows():
            fig.add_annotation(
                x=row["id"],
                y=1.02,
                text=f"{row['total']:.0f}",
                showarrow=False,
                font=dict(size=10, color="black"),
                xanchor="center"
            )

        return fig, "dev-effort-saving-stacked-bar.pdf", df


def export_charts():
    plotter = ChartPlotter()
    charts_root = Paths().paper_root / "charts"
    if not charts_root.exists():
        charts_root.mkdir(exist_ok=True, parents=True)

    for fig, img_file, data in [
        #plotter.ablation_violins_overlapping(),
        # plotter.ablation_histogram(),
        # plotter.mig_correctness_violin(),
        plotter.dev_effort_save_stacked_bar(),
    ]:
        fig.show()
        fig.write_image(charts_root.joinpath(img_file).as_posix())
        # latex_chart_data = charts_root / img_file.replace(".pdf", "") / "data.csv"
        # if not latex_chart_data.parent.exists():
        # latex_chart_data.parent.mkdir(parents=True, exist_ok=True)
        # data.to_csv(latex_chart_data, index=False)


if __name__ == '__main__':
    export_charts()
