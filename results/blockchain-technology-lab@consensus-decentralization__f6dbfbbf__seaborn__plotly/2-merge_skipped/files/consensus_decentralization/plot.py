import argparse
import logging
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import consensus_decentralization.helper as hlp
import colorcet as cc
import pandas as pd
from plotly.colors import qualitative


def plot_animated_lines(df, x_label, y_label, filename, path, colors):
    df.index = pd.to_datetime(df.timeframe)
    df.drop(['timeframe'], axis=1, inplace=True)
    num_time_steps = df.shape[0]
    num_lines = df.shape[1]

    # Create traces for each line
    fig = go.Figure()
    for i, col in enumerate(df.columns):
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col, line=dict(color=colors[i])))

    # Add animation frames
    frames = []
    for i in range(1, num_time_steps + 1):
        frame_data = []
        for j, col in enumerate(df.columns):
            frame_data.append(go.Scatter(x=df[:i].index, y=df[:i][col], mode='lines', line=dict(color=colors[j])))
        frames.append(go.Frame(data=frame_data, name=str(i)))

    fig.frames = frames

    # Add layout and animation settings
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        updatemenus=[{
            'buttons': [
                {'args': [None, {'frame': {'duration': 100, 'redraw': True}, 'fromcurrent': True}],
                 'label': 'Play', 'method': 'animate'},
                {'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                 'label': 'Pause', 'method': 'animate'}
            ],
            'direction': 'left',
            'pad': {'r': 10, 't': 87},
            'showactive': False,
            'type': 'buttons',
            'x': 0.1,
            'xanchor': 'right',
            'y': 0,
            'yanchor': 'top'
        }]
    )

    # Save as HTML
    filename += ".html"
    fig.write_html(f'{str(path)}/{filename}')


def plot_lines(data, x_label, y_label, filename, path, xtick_labels, colors, title=''):
    fig = px.line(data, x=data.index, y=data.columns, color_discrete_sequence=colors, title=title)
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        xaxis=dict(tickmode='array', tickvals=xtick_labels.index, ticktext=xtick_labels, tickangle=45)
    )
    filename += ".png"
    fig.write_image(path / filename)


def plot_stack_area_chart(values, execution_id, path, ylabel, legend_labels, tick_labels, legend):
    num_entities = values.shape[0]
    num_time_steps = values.shape[1]
    col = qualitative.Plotly[:num_entities]

    fig = go.Figure()
    for i in range(num_entities):
        fig.add_trace(go.Scatter(
            x=list(range(num_time_steps)),
            y=values[i],
            mode='lines',
            fill='tonexty',
            name=legend_labels[i],
            line=dict(color=col[i])
        ))

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title=ylabel,
        xaxis=dict(tickmode='array', tickvals=list(range(num_time_steps)), ticktext=tick_labels, tickangle=45),
        showlegend=legend
    )

    filename = "poolDynamics-" + execution_id + ".png"
    fig.write_image(path / filename)


def plot_animated_stack_area_chart(values, execution_id, path, ylabel, legend_labels, tick_labels, legend):
    num_entities = values.shape[0]
    num_time_steps = values.shape[1]
    col = qualitative.Plotly[:num_entities]

    fig = go.Figure()

    # Add initial traces
    for i in range(num_entities):
        fig.add_trace(go.Scatter(
            x=list(range(num_time_steps)),
            y=values[i][:1],
            mode='lines',
            fill='tonexty',
            name=legend_labels[i],
            line=dict(color=col[i])
        ))

    # Add animation frames
    frames = []
    for n in range(1, num_time_steps + 1):
        frame_data = []
        for i in range(num_entities):
            frame_data.append(go.Scatter(
                x=list(range(n)),
                y=values[i][:n],
                mode='lines',
                fill='tonexty',
                line=dict(color=col[i])
            ))
        frames.append(go.Frame(data=frame_data, name=str(n)))

    fig.frames = frames

    # Add layout and animation settings
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title=ylabel,
        xaxis=dict(tickmode='array', tickvals=list(range(num_time_steps)), ticktext=tick_labels, tickangle=45),
        updatemenus=[{
            'buttons': [
                {'args': [None, {'frame': {'duration': 100, 'redraw': True}, 'fromcurrent': True}],
                 'label': 'Play', 'method': 'animate'},
                {'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                 'label': 'Pause', 'method': 'animate'}
            ],
            'direction': 'left',
            'pad': {'r': 10, 't': 87},
            'showactive': False,
            'type': 'buttons',
            'x': 0.1,
            'xanchor': 'right',
            'y': 0,
            'yanchor': 'top'
        }]
    )

    filename = "poolDynamics-" + execution_id + ".html"

def plot_dynamics_per_ledger(ledgers, aggregated_data_filename, top_k=-1, unit='relative', animated=False, legend=False):
    """
    Plots the dynamics of pools for each ledger in terms of produced blocks
    :param ledgers: list of strings representing the ledgers whose data will be plotted
    :param aggregated_data_filename: string that corresponds to the name of the file that contains the aggregated
        data for the relevant timeframe, estimation window and frequency
    :param top_k: if > 0, then only the evolution of the top k pools will be shown in the graph. Otherwise,
    all pools will be plotted.
    :param unit: string that specifies whether the plots to be generated will be in absolute or relative values (i.e.
        number of blocks or share of blocks). It can be one of: absolute, relative
    :param animated: bool that specifies whether the plots to be generated will be animated or not
    :param legend: bool that specifies whether the plots to be generated will include a legend or not
    """
    for ledger in ledgers:
        ledger_path = hlp.OUTPUT_DIR / ledger
        figures_path = ledger_path / 'figures'
        if not figures_path.is_dir():
            figures_path.mkdir()

        time_chunks, blocks_per_entity = hlp.get_blocks_per_entity_from_file(
            filepath=ledger_path / "blocks_per_entity" / aggregated_data_filename
        )

        total_blocks_per_time_chunk = [0] * len(time_chunks)
        for entity, block_values in blocks_per_entity.items():
            for time_chunk, nblocks in block_values.items():
                total_blocks_per_time_chunk[time_chunks.index(time_chunk)] += nblocks

        total_blocks_per_time_chunk = np.array(total_blocks_per_time_chunk)
        nonzero_idx = total_blocks_per_time_chunk.nonzero()[0]  # only keep time chunks with at least one block
        total_blocks_per_time_chunk = total_blocks_per_time_chunk[nonzero_idx]
        time_chunks = [time_chunks[i] for i in nonzero_idx]

        blocks_array = []
        for entity, block_values in blocks_per_entity.items():
            entity_array = []
            for time_chunk in time_chunks:
                try:
                    entity_array.append(block_values[time_chunk])
                except KeyError:
                    entity_array.append(0)
            blocks_array.append(entity_array)

        blocks_array = np.array(blocks_array)

        if unit == 'relative':
            block_shares_array = blocks_array / total_blocks_per_time_chunk * 100
            values = block_shares_array
            ylabel = 'Share of produced blocks (%)'
            legend_threshold = 0 * total_blocks_per_time_chunk + 5  # only show in the legend pools that have a
            # contribution of at least 5% in some time chunk
        else:
            values = blocks_array
            ylabel = 'Number of produced blocks'
            legend_threshold = 0.05 * total_blocks_per_time_chunk  # only show in the legend pools that have a contribution of at least 5% in some time chunk
        max_values_per_pool = values.max(axis=1)
        labels = [
            f"{entity_name if len(entity_name) <= 15 else entity_name[:15] + '..'}"
            f"({round(max_values_per_pool[i], 1)}{'%' if unit == 'relative' else ''})"
            if any(values[i] > legend_threshold) else f'_{entity_name}'
            for i, entity_name in enumerate(blocks_per_entity.keys())
        ]
        if top_k > 0:  # only keep the top k pools (i.e. the pools that produced the most blocks in total)
            total_value_per_pool = values.sum(axis=1)
            top_k_idx = total_value_per_pool.argpartition(-top_k)[-top_k:]
            values = values[top_k_idx]
            labels = [labels[i] for i in top_k_idx]

        if animated:
            plot_animated_stack_area_chart(
                values=values,
                execution_id=f'{ledger}_{unit}_values_top_{top_k}' if top_k > 0 else f'{ledger}_{unit}_values_all',
                path=figures_path,
                ylabel=ylabel,
                legend_labels=labels,
                tick_labels=time_chunks,
                legend=legend
            )
        else:
            plot_stack_area_chart(
                values=values,
                execution_id=f'{ledger}_{unit}_values_top_{top_k}' if top_k > 0 else f'{ledger}_{unit}_values_all',
                path=figures_path,
                ylabel=ylabel,
                legend_labels=labels,
                tick_labels=time_chunks,
                legend=legend
            )


def plot_comparative_metrics(ledgers, metrics, animated=False):
    for metric in metrics:
        figures_path = hlp.OUTPUT_DIR / 'figures'
        if not figures_path.is_dir():
            figures_path.mkdir()
        filename = f'{metric}.csv'
        metric_df = pd.read_csv(hlp.OUTPUT_DIR / filename)
        # only keep rows that contain at least one (non-nan) value in the columns that correspond to the ledgers
        metric_df = metric_df[metric_df.iloc[:, 1:].notna().any(axis=1)]
        ledger_columns_to_keep = [col for col in metric_df.columns if col in ledgers]
        num_lines = metric_df.shape[1]
        colors = sns.color_palette(cc.glasbey, n_colors=num_lines)
        if len(ledger_columns_to_keep) > 0:
            metric_df = metric_df[['timeframe'] + ledger_columns_to_keep]
            if animated:
                plot_animated_lines(
                    df=metric_df,
                    x_label='Time',
                    y_label=metric,
                    filename=f"{metric}_{'_'.join(ledger_columns_to_keep)}",
                    path=figures_path,
                    colors=colors
                )
            else:
                plot_lines(
                    data=metric_df,
                    x_label='Time',
                    y_label=metric,
                    filename=f"{metric}_{'_'.join(ledger_columns_to_keep)}",
                    path=figures_path,
                    xtick_labels=metric_df['timeframe'],
                    colors=colors
                )


def plot(ledgers, metrics, aggregated_data_filename, animated):
    logging.info("Creating plots..")
    plot_dynamics_per_ledger(ledgers=ledgers, aggregated_data_filename=aggregated_data_filename, animated=False, legend=True)
    plot_comparative_metrics(ledgers=ledgers, metrics=metrics, animated=False)
    if animated:
        plot_dynamics_per_ledger(ledgers=ledgers, aggregated_data_filename=aggregated_data_filename, animated=True)
        plot_comparative_metrics(ledgers=ledgers, metrics=metrics, animated=True)


if __name__ == '__main__':
    ledgers = hlp.get_ledgers()
    default_metrics = hlp.get_metrics_config().keys()

    default_start_date, default_end_date = hlp.get_start_end_dates()
    timeframe_start = hlp.get_timeframe_beginning(default_start_date)
    timeframe_end = hlp.get_timeframe_end(default_end_date)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--ledgers',
        nargs="*",
        type=str.lower,
        default=ledgers,
        choices=ledgers,
        help='The ledgers whose data will be plotted.'
    )
    parser.add_argument(
        '--metrics',
        nargs="*",
        type=str.lower,
        default=default_metrics,
        choices=default_metrics,
        help='The metrics to plot.'
    )
    parser.add_argument(
        '--filename',
        type=str,
        default=hlp.get_blocks_per_entity_filename(timeframe=(timeframe_start, timeframe_end), estimation_window=30,
                                                   frequency=30),
        help='The name of the file that contains the aggregated data.'
    )
    parser.add_argument(
        '--animated',
        action='store_true',
        help='Flag to specify whether to also generate animated plots.'
    )
    args = parser.parse_args()
    plot(ledgers=args.ledgers, metrics=args.metrics, aggregated_data_filename=args.filename, animated=args.animated)
    fig.write_html(f'{str(path)}/{filename}')