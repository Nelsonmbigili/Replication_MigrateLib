import argparse
import logging
import altair as alt
import numpy as np
import consensus_decentralization.helper as hlp
import colorcet as cc
import pandas as pd


def plot_animated_lines(df, x_label, y_label, filename, path, colors):
    df.index = pd.to_datetime(df.timeframe)
    df.drop(['timeframe'], axis=1, inplace=True)
    num_time_steps = df.shape[0]
    num_lines = df.shape[1]

    # Prepare data for Altair
    df_melted = df.reset_index().melt(id_vars='index', var_name='line', value_name='value')
    df_melted.columns = ['time', 'line', 'value']

    # Create the chart
    chart = alt.Chart(df_melted).mark_line().encode(
        x='time:T',
        y='value:Q',
        color='line:N'
    ).properties(
        width=600,
        height=400
    ).interactive()

    # Save the chart as a PNG
    filename += ".png"
    chart.save(f'{str(path)}/{filename}')


def plot_lines(data, x_label, y_label, filename, path, xtick_labels, colors, title=''):
    data.index = pd.to_datetime(data.timeframe)
    data.drop(['timeframe'], axis=1, inplace=True)
    data_melted = data.reset_index().melt(id_vars='index', var_name='line', value_name='value')
    data_melted.columns = ['time', 'line', 'value']

    chart = alt.Chart(data_melted).mark_line().encode(
        x='time:T',
        y='value:Q',
        color='line:N'
    ).properties(
        title=title,
        width=600,
        height=400
    ).interactive()

    filename += ".png"
    chart.save(f'{str(path)}/{filename}')


def plot_stack_area_chart(values, execution_id, path, ylabel, legend_labels, tick_labels, legend):
    num_entities = values.shape[0]
    num_time_steps = values.shape[1]
    data = pd.DataFrame(values.T, columns=legend_labels)
    data['time'] = tick_labels
    data = data.melt(id_vars='time', var_name='entity', value_name='value')

    chart = alt.Chart(data).mark_area().encode(
        x='time:T',
        y='value:Q',
        color='entity:N'
    ).properties(
        width=600,
        height=400
    ).interactive()

    filename = "poolDynamics-" + execution_id + ".png"
    chart.save(f'{str(path)}/{filename}')


def plot_animated_stack_area_chart(values, execution_id, path, ylabel, legend_labels, tick_labels, legend):
    num_entities = values.shape[0]
    num_time_steps = values.shape[1]
    data = pd.DataFrame(values.T, columns=legend_labels)
    data['time'] = tick_labels
    data = data.melt(id_vars='time', var_name='entity', value_name='value')

    chart = alt.Chart(data).mark_area().encode(
        x='time:T',
        y='value:Q',
        color='entity:N'
    ).properties(
        width=600,
        height=400
    ).interactive()

    filename = "poolDynamics-" + execution_id + ".png"
    chart.save(f'{str(path)}/{filename}')


def plot_dynamics_per_ledger(ledgers, aggregated_data_filename, top_k=-1, unit='relative', animated=False, legend=False):
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
        nonzero_idx = total_blocks_per_time_chunk.nonzero()[0]
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
            legend_threshold = 0 * total_blocks_per_time_chunk + 5
        else:
            values = blocks_array
            ylabel = 'Number of produced blocks'
            legend_threshold = 0.05 * total_blocks_per_time_chunk
        max_values_per_pool = values.max(axis=1)
        labels = [
            f"{entity_name if len(entity_name) <= 15 else entity_name[:15] + '..'}"
            f"({round(max_values_per_pool[i], 1)}{'%' if unit == 'relative' else ''})"
            if any(values[i] > legend_threshold) else f'_{entity_name}'
            for i, entity_name in enumerate(blocks_per_entity.keys())
        ]
        if top_k > 0:
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
        metric_df = metric_df[metric_df.iloc[:, 1:].notna().any(axis=1)]
        ledger_columns_to_keep = [col for col in metric_df.columns if col in ledgers]
        num_lines = metric_df.shape[1]
        colors = cc.glasbey[:num_lines]  # Use colorcet directly for colors
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
