#!/usr/bin/python
import argparse
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate static Plotly graphs.')
    parser.add_argument('--round_file', type=str, required=True, help='Round dropdown file name')
    parser.add_argument('--count_out_input', type=int, default=0, help='Count out input')
    parser.add_argument('--freq_out_input', type=float, default=0.0, help='Freq out input')
    parser.add_argument('--count_in_input', type=int, default=0, help='Count in input')
    parser.add_argument('--freq_in_input', type=float, default=0.0, help='Freq in input')
    parser.add_argument('--count_neg_input', type=int, default=0, help='Count neg input')
    parser.add_argument('--freq_neg_input', type=float, default=0.0, help='Freq neg input')
    parser.add_argument('--enr_neg_input', type=float, default=0, help='Enr neg input')
    parser.add_argument('--enr_out_input', type=float, default=0, help='Enr out input')

    args = parser.parse_args()

    # Load and preprocess data
    print(args.round_file)
    df = pd.read_csv(f"{args.round_file}", skiprows=6)
    df = df.fillna(0)
    for coln in df.columns:
        if coln.lower().startswith('freq'):
            df[coln] = df[coln].str.rstrip('%').astype('float')
    if 'Enr_neg_upper' in df.columns:
        df['Enr_neg_error_pos'] = df['Enr_neg_upper'] - df['Enr_neg']
        df['Enr_neg_error_neg'] = df['Enr_neg'] - df['Enr_neg_lower']
    else:
        df['Enr_neg_error_pos'] = 0
        df['Enr_neg_error_neg'] = 0

    df['Enr_out_error_pos'] = df['Enr_out_upper'] - df['Enr_out']
    df['Enr_out_error_neg'] = df['Enr_out'] - df['Enr_out_lower']
    
    if 'Enr_neg_upper' in df.columns:
        filtered_df = df[
            (df['Count_out'] > args.count_out_input) &
            (df['Freq_out'] > args.freq_out_input) &
            (df['Count_in'] > args.count_in_input) &
            (df['Freq_in'] > args.freq_in_input) &
            (df['Count_neg'] > args.count_neg_input) &
            (df['Freq_neg'] > args.freq_neg_input) &
            (df['Enr_neg'] > args.enr_neg_input) &
            (df['Enr_out'] > args.enr_out_input)
        ]
    else:
        filtered_df = df[
            (df['Count_out'] > args.count_out_input) &
            (df['Freq_out'] > args.freq_out_input) &
            (df['Count_in'] > args.count_in_input) &
            (df['Freq_in'] > args.freq_in_input) &
            (df['Enr_out'] > args.enr_out_input)
        ]
    # Create a subplot layout
    fig = make_subplots(
        rows=1, cols=2
    )

    if 'Enr_neg_upper' in df.columns:

        # Add y=x line to scatter plot
        fig.add_trace(go.Scatter(
            x=[0, df['Enr_out'].max() + 1000],
            y=[0, df['Enr_out'].max() + 1000],
            mode='lines',
            marker=dict(color='orange'),
            name='y=x',
            legendgroup='group2'
        ), row=1, col=2)

        # Add scatter plot with asymmetric error bars
        fig.add_trace(go.Scatter(
            x=filtered_df['Enr_neg'],
            y=filtered_df['Enr_out'],
            mode='markers',
            marker=dict(color='black'),
            error_x=dict(
                type='data',
                array=filtered_df['Enr_neg_error_pos'],
                arrayminus=filtered_df['Enr_neg_error_neg'],
                width=1,
                color='rgba(0, 0, 0, 0.2)'
            ),
            error_y=dict(
                type='data',
                array=filtered_df['Enr_out_error_pos'],
                arrayminus=filtered_df['Enr_out_error_neg'],
                width=1,
                color='rgba(0, 0, 0, 0.2)'
            ),
            name='Unique Sequence Name',
            text=filtered_df['Unique_Sequence_Name'],
            hovertemplate=
            '<b>%{text}</b><br>' +
            'Enrichment in negative selection: %{x}<br>' +
            'Enrichment in post-selection: %{y}<br>',
            legendgroup='group2'
        ), row=1, col=2)

        # Add marker plot for Enrichment_Negative
        fig.add_trace(go.Scatter(
            x=filtered_df['Unique_Sequence_Name'],
            y=filtered_df['Enr_neg'],
            mode='markers',
            marker=dict(color='red', symbol='square'),
            name='Enrichment_Negative',
            error_y=dict(
                type='data',
                array=filtered_df['Enr_neg_error_pos'],
                arrayminus=filtered_df['Enr_neg_error_neg'],
                width=1,
                color='rgba(255, 0, 0, 0.2)'
            ),
            text=filtered_df['Unique_Sequence_Name'],
            hovertemplate=
            '<b>%{text}</b><br>' +
            'Enrichment_Negative: %{y}<br>',
            legendgroup='group1'
            ), row=1, col=1)
    
    # Add marker plot for Enrichment_Out
    fig.add_trace(go.Scatter(
        x=filtered_df['Unique_Sequence_Name'],
        y=filtered_df['Enr_out'],
        mode='markers',
        marker=dict(color='blue', symbol='star'),
        name='Enrichment_Out',
        error_y=dict(
            type='data',
            array=filtered_df['Enr_out_error_pos'],
            arrayminus=filtered_df['Enr_out_error_neg'],
            width=1,
            color='rgba(0, 0, 255, 0.2)'
        ),
        text=filtered_df['Unique_Sequence_Name'],
        hovertemplate=
        '<b>%{text}</b><br>' +
        'Enrichment_Out: %{y}<br>',
            legendgroup='group1'
    ), row=1, col=1)

    # Update layout for the entire subplot
    fig.update_layout(
    title_text=f'Round {args.round_file.split("round_")[1].split("_")[0]} Enrichment Results',
    showlegend=True,
    plot_bgcolor='white',  # Set the plot background color to white
    xaxis=dict(
        showline=True,
        linewidth=1,
        linecolor='black',
        mirror=True,
        gridcolor='rgba(0, 0, 0, 0.1)'  # Black grid with 10% opacity
    ),
    yaxis=dict(
        showline=True,
        linewidth=1,
        linecolor='black',
        mirror=True,
        gridcolor='rgba(0, 0, 0, 0.1)'  # Black grid with 10% opacity
    )
    )

    fig.update_xaxes(range=[0, None], row=1, col=2)
    fig.update_yaxes(range=[0, None])

    # Apply the same settings to all subplots
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True, gridcolor='rgba(0, 0, 0, 0.1)')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True, gridcolor='rgba(0, 0, 0, 0.1)')

    # Update individual subplot axis titles
    fig.update_xaxes(title_text='Enrichment in negative selection (log scale)', type='log', row=1, col=2)
    fig.update_yaxes(title_text='Enrichment in post-selection (log scale)', type='log', row=1, col=2)
    fig.update_xaxes(title_text='Unique Sequence Name', row=1, col=1)
    fig.update_yaxes(title_text='Enrichment (log scale)', type='log', row=1, col=1)
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1,
            traceorder="grouped"
        )
    )
    # Show combined plot
    fig.show()
if __name__ == "__main__":
    main()
