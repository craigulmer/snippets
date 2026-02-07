import click
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, time
import matplotlib.dates as mdates


def plot_single_day(ax, day_data, time_col, glucose_col, max_glucose, is_last=False, linewidth=1):
    times = day_data[time_col].values
    glucose_values = day_data[glucose_col].values
    
    for i in range(len(times) - 1):
        if 70 <= glucose_values[i] <= 140:
            ax.plot(times[i:i+2], glucose_values[i:i+2], color='green', linewidth=linewidth)
        else:
            ax.plot(times[i:i+2], glucose_values[i:i+2], color='red', linewidth=linewidth)
    
    ax.set_ylim(50, 200)
    
    day_date = day_data[time_col].iloc[0].date()
    start_time = datetime.combine(day_date, time(0, 0, 0))
    end_time = datetime.combine(day_date, time(23, 59, 59))
    ax.set_xlim(start_time, end_time)
    
    title = day_date.strftime("%A, %b ") + str(day_date.day)
    ax.text(0.02, 0.95, title, transform=ax.transAxes, verticalalignment='top', fontsize=10)
    
    ax.axhline(y=70, color='gray', linestyle='--')
    ax.axhline(y=140, color='gray', linestyle='--')
    
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    ax.tick_params(axis='x', which='major', direction='in')
    
    if not is_last:
        ax.set_xticklabels([])


@click.command()
@click.option('--input', required=True, help='Input CSV file path')
@click.option('--output', default=None, help='Output file path')
@click.option('--thumbnail', is_flag=True, help='Enable thumbnail mode with 600px width')
@click.option('--thick', is_flag=True, help='Use thick lines')
@click.option('--day', type=str, default=None, help='Plot specific days (comma-separated, e.g. "1,2,3")')
def main(input, output, thumbnail, thick, day):
    df = pd.read_csv(input)
    
    time_col = df.columns[0]
    glucose_col = df.columns[1]
    
    df[time_col] = pd.to_datetime(df[time_col])
    if df[time_col].dt.tz is not None:
        df[time_col] = df[time_col].dt.tz_localize(None)
    
    min_value = df[glucose_col].min()
    max_value = df[glucose_col].max()
    
    time_span = df[time_col].max() - df[time_col].min()
    num_days = time_span.total_seconds() / (24 * 3600)
    
    print(f"Min glucose value: {min_value}")
    print(f"Max glucose value: {max_value}")
    print(f"Number of days: {num_days:.2f}")
    
    df['date'] = df[time_col].dt.date
    unique_days = sorted(df['date'].unique())
    num_plots = len(unique_days)
    
    if day is not None:
        day_indices = [int(d.strip()) for d in day.split(',')]
        selected_days = []
        for idx in day_indices:
            if idx < 1 or idx > len(unique_days):
                print(f"Error: day {idx} is out of range (1-{len(unique_days)})")
                return
            selected_days.append(unique_days[idx - 1])
        unique_days = selected_days
        num_plots = len(unique_days)
    
    linewidth = 3 if thick else 1
    
    if thumbnail:
        dpi = 100
        figsize = (6.0, 1.5 * num_plots)
    else:
        dpi = 100
        figsize = (12, 3 * num_plots)
    
    fig, axes = plt.subplots(num_plots, 1, figsize=figsize, dpi=dpi)
    if num_plots == 1:
        axes = [axes]
    
    for idx, day_date in enumerate(unique_days):
        day_data = df[df['date'] == day_date]
        is_last = (idx == num_plots - 1)
        plot_single_day(axes[idx], day_data, time_col, glucose_col, max_value, is_last=is_last, linewidth=linewidth)
    
    plt.tight_layout()
    if output is not None:
        plt.savefig(output, bbox_inches='tight', dpi=dpi)
    plt.show()


if __name__ == '__main__':
    main()
