#!/usr/bin/python
import argparse
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import pandas as pd

# Use the 'browser' renderer to open plots in the default web browser
pio.renderers.default = 'browser'

def main(
        round_file: str,
        input_values: dict
    ):
    for input_val in input_values:
        vals = input_values.get(input_val)
        val_min, val_max = vals[0], vals[1]
        if input_val.lower().startswith('freq'):
            
            globals()[input_val.lower()+'_input_min'] = float(val_min)
            globals()[input_val.lower()+'_input_max'] = float(val_max)

        else:
            globals()[input_val.lower()+'_input_min'] = int(val_min)
            globals()[input_val.lower()+'_input_max'] = int(val_max)
    # Load and preprocess data
    print(round_file)
    df = pd.read_csv(f"{round_file}", skiprows=6)
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

    df['Enr_post_error_pos'] = df['Enr_post_upper'] - df['Enr_post']
    df['Enr_post_error_neg'] = df['Enr_post'] - df['Enr_post_lower']
    
    if 'Enr_neg_upper' in df.columns:
        filtered_df = df[
            (df['Count_post'] >= count_post_input_min) & (df['Count_post'] <= count_post_input_max) &
            (df['Freq_post'] >= freq_post_input_min) & (df['Freq_post'] <= freq_post_input_max) &
            (df['Count_pre'] >= count_pre_input_min) & (df['Count_pre'] <= count_pre_input_max) &
            (df['Freq_pre'] >= freq_pre_input_min) & (df['Freq_pre'] <= freq_pre_input_max) &
            (df['Count_neg'] >= count_neg_input_min) & (df['Count_neg'] <= count_neg_input_max) &
            (df['Freq_neg'] >= freq_neg_input_min) & (df['Freq_neg'] <= freq_neg_input_max) &
            (df['Enr_neg'] >= enr_neg_input_min) & (df['Enr_neg'] <= enr_neg_input_max) &
            (df['Enr_post'] >= enr_post_input_min) & (df['Enr_post'] <= enr_post_input_max)
        ]
    else:
        filtered_df = df[
            (df['Count_post'] >= count_post_input_min) & (df['Count_post'] <= count_post_input_max) &
            (df['Freq_post'] >= freq_post_input_min) & (df['Freq_post'] <= freq_post_input_max) &
            (df['Count_pre'] >= count_pre_input_min) & (df['Count_pre'] <= count_pre_input_max) &
            (df['Freq_pre'] >= freq_pre_input_min) & (df['Freq_pre'] <= freq_pre_input_max) &
            (df['Enr_post'] >= enr_post_input_min) & (df['Enr_post'] <= enr_post_input_max) 
        ]
    # Create a subplot layout
    fig = make_subplots(
        rows=1, cols=2
    )

    if 'Enr_neg_upper' in df.columns:

        # Add y=x line to scatter plot
        fig.add_trace(go.Scatter(
            x=[0, df['Enr_post'].max() + 1000],
            y=[0, df['Enr_post'].max() + 1000],
            mode='lines',
            marker=dict(color='orange'),
            name='y=x',
            legendrank=5
        ), row=1, col=2)

        # Add scatter plot with asymmetric error bars
        fig.add_trace(go.Scatter(
            x=filtered_df['Enr_neg'],
            y=filtered_df['Enr_post'],
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
                array=filtered_df['Enr_post_error_pos'],
                arrayminus=filtered_df['Enr_post_error_neg'],
                width=1,
                color='rgba(0, 0, 0, 0.2)'
            ),
            name='Unique Sequence Name            ',
            text=filtered_df['Unique_Sequence_Name'],
            hovertemplate=
            '<b>%{text}</b><br>' +
            'Enrichment in negative selection: %{x}<br>' +
            'Enrichment in post-selection: %{y}<br>',
            legendrank=4
        ), row=1, col=2)

        # Add marker plot for Enrichment_Negative
        fig.add_trace(go.Scatter(
            x=filtered_df['Unique_Sequence_Name'],
            y=filtered_df['Enr_neg'],
            mode='markers',
            marker=dict(color='red', symbol='square'),
            name='Enrichment_Negative            ',
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
            legendrank=2
            ), row=1, col=1)
    
    # Add marker plot for Enrichment_post
    fig.add_trace(go.Scatter(
        x=filtered_df['Unique_Sequence_Name'],
        y=filtered_df['Enr_post'],
        mode='markers',
        marker=dict(color='blue', symbol='star'),
        name='Enrichment_Post            ',
        error_y=dict(
            type='data',
            array=filtered_df['Enr_post_error_pos'],
            arrayminus=filtered_df['Enr_post_error_neg'],
            width=1,
            color='rgba(0, 0, 255, 0.2)'
        ),
        text=filtered_df['Unique_Sequence_Name'],
        hovertemplate=
        '<b>%{text}</b><br>' +
        'Enrichment_Post: %{y}<br>',
        legendrank=1
    ), row=1, col=1)

    # Update layout for the entire subplot
    fig.update_layout(
    title_text=f'Round {round_file.split("round_")[1].split("_")[0]} Enrichment Results',
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
            x=1
        )
    )
    # Show combined plot
    fig.show()
    return True
