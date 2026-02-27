import argparse
import logging
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import numpy as np
import consensus_decentralization.helper as hlp
import colorcet as cc
import pandas as pd


def plot_animated_lines(df, x_label, y_label, filename, path, colors):
    df.index = pd.to_datetime(df.timeframe)
    df.drop(['timeframe'], axis=1, inplace=True)
    num_time_steps = df.shape[0]
    num_lines = df.shape[1]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    ax.set_xticks(range(num_time_steps))
    ax.set_xticklabels(df.index, rotation=45, ha="right", rotation_mode="anchor")
    plt.subplots_adjust(bottom=0.2, top=0.9)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    def animate(i):
        ax.clear()
        sns.lineplot(data=df[:i], palette=colors, ax=ax)
        ax.legend(df.columns, frameon=False)

    ani = animation.FuncAnimation(fig, animate, interval=100, frames=num_time_steps, repeat=False)
    filename += ".gif"
    ani.save(f'{str(path)}/{filename}', writer=animation.PillowWriter())
    plt.close(fig)


def plot_lines(data, x_label, y_label, filename, path, xtick_labels, colors, title=''):
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=data, palette=colors, ax=ax)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    sns.move_legend(ax, "best", frameon=False)
    ax.set_xticks(xtick_labels.index)
    ax.set_xticklabels(xtick_labels, rotation=45)
    locs, x_labels = plt.xticks()
    for i, label in enumerate(x_labels):
        if i % 5 == 0:
            continue
        label.set_visible(False)
    filename += ".png"
    plt.savefig(path / filename, bbox_inches='tight')


def plot_stack_area_chart(values, execution_id, path, ylabel, legend_labels, tick_labels, legend):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.set_theme(style="whitegrid")
    num_entities = values.shape[0]
    col = sns.color_palette(cc.glasbey, n_colors=num_entities)

    # Simulate stackplot using cumulative sums
    cumulative_values = np.cumsum(values, axis=0)
    for i in range(num_entities):
        sns.lineplot(x=range(values.shape[1]), y=cumulative_values[i], color=col[i], ax=ax, label=legend_labels[i])

    ax.margins(0)
    ax.set_xlabel("Time")
    ax.set_ylabel(ylabel)
    ax.set_xticks(range(values.shape[1]))
    ax.set_xticklabels(tick_labels, rotation=45)
    locs, x_labels = plt.xticks()
    for i, label in enumerate(x_labels):
        if i % 5 == 0:
            continue
        label.set_visible(False)
    if legend:
        sns.move_legend(ax, "upper right", bbox_to_anchor=(1.1, 1), frameon=False)
    filename = "poolDynamics-" + execution_id + ".png"
    plt.savefig(path / filename, bbox_inches='tight')
    plt.close(fig)


def plot_animated_stack_area_chart(values, execution_id, path, ylabel, legend_labels, tick_labels, legend):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.set_theme(style="whitegrid")
    num_entities = values.shape[0]
    col = sns.color_palette(cc.glasbey, n_colors=num_entities)
    plt.margins(0)
    plt.xlabel("Time")
    plt.ylabel(ylabel)
    plt.xticks(ticks=range(num_time_steps), labels=tick_labels, rotation=45)
    plt.subplots_adjust(bottom=0.2, top=0.9)  # ensure the dates (on the x-axis) fit in the screen
    locs, x_labels = plt.xticks()
    for i, label in enumerate(x_labels):
        if i % 5 == 0:  # only keep every 5th xtick label
            continue
        label.set_visible(False)

    ims = []
    cumulative_values = np.cumsum(values, axis=0)
    for n in range(1, values.shape[1] + 1):
        ax.clear()
        for i in range(num_entities):
            sns.lineplot(x=range(n), y=cumulative_values[i, :n], color=col[i], ax=ax, label=legend_labels[i])
        ax.margins(0)
        ax.set_xlabel("Time")
        ax.set_ylabel(ylabel)
        ax.set_xticks(range(values.shape[1]))
        ax.set_xticklabels(tick_labels, rotation=45)
        locs, x_labels = plt.xticks()
        for i, label in enumerate(x_labels):
            if i % 5 == 0:
                continue
            label.set_visible(False)
        if legend:
            sns.move_legend(ax, "upper right", bbox_to_anchor=(1.1, 1), frameon=False)
        ims.append(ax.get_children())

    ani = animation.ArtistAnimation(fig, ims, interval=100, repeat_delay=10000)
    filename = "poolDynamics-" + execution_id + ".gif"
    ani.save(f'{str(path)}/{filename}', writer=animation.PillowWriter())
    plt.close(fig)


# The rest of the code remains unchanged
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
# ...