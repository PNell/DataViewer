"""
Chart generation using Plotly Graph Objects.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Optional, Any
from app.models.schemas import ChartType


class ChartGenerator:
    """Generate Plotly charts from data"""

    @staticmethod
    def create_line_chart(data: pd.DataFrame, x: str, y: str,
                         color: Optional[str] = None,
                         title: Optional[str] = None,
                         x_label: Optional[str] = None,
                         y_label: Optional[str] = None,
                         **options) -> dict:
        """Create a line chart"""
        fig = go.Figure()

        if color and color in data.columns:
            # Multiple lines grouped by color column
            for group_name in data[color].unique():
                group_data = data[data[color] == group_name]
                fig.add_trace(go.Scatter(
                    x=group_data[x],
                    y=group_data[y],
                    mode='lines+markers',
                    name=str(group_name),
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
        else:
            # Single line
            fig.add_trace(go.Scatter(
                x=data[x],
                y=data[y],
                mode='lines+markers',
                name=y,
                line=dict(width=2),
                marker=dict(size=6)
            ))

        fig.update_layout(
            title=title or f"{y} vs {x}",
            xaxis_title=x_label or x,
            yaxis_title=y_label or y,
            hovermode='closest',
            template='plotly_white'
        )

        return fig.to_dict()

    @staticmethod
    def create_bar_chart(data: pd.DataFrame, x: str, y: Optional[str] = None,
                        orientation: str = 'v',
                        color: Optional[str] = None,
                        title: Optional[str] = None,
                        x_label: Optional[str] = None,
                        y_label: Optional[str] = None,
                        **options) -> dict:
        """Create a bar chart"""
        fig = go.Figure()

        if y is None:
            # Count frequency
            counts = data[x].value_counts().sort_index()
            if orientation == 'v':
                fig.add_trace(go.Bar(x=counts.index, y=counts.values))
            else:
                fig.add_trace(go.Bar(y=counts.index, x=counts.values, orientation='h'))
        else:
            # Use y values
            if color and color in data.columns:
                for group_name in data[color].unique():
                    group_data = data[data[color] == group_name]
                    if orientation == 'v':
                        fig.add_trace(go.Bar(
                            x=group_data[x],
                            y=group_data[y],
                            name=str(group_name)
                        ))
                    else:
                        fig.add_trace(go.Bar(
                            y=group_data[x],
                            x=group_data[y],
                            name=str(group_name),
                            orientation='h'
                        ))
            else:
                if orientation == 'v':
                    fig.add_trace(go.Bar(x=data[x], y=data[y]))
                else:
                    fig.add_trace(go.Bar(y=data[x], x=data[y], orientation='h'))

        fig.update_layout(
            title=title or f"Bar Chart",
            xaxis_title=x_label or x,
            yaxis_title=y_label or (y if y else "Count"),
            template='plotly_white',
            barmode='group'
        )

        return fig.to_dict()

    @staticmethod
    def create_scatter_chart(data: pd.DataFrame, x: str, y: str,
                           color: Optional[str] = None,
                           size: Optional[str] = None,
                           title: Optional[str] = None,
                           x_label: Optional[str] = None,
                           y_label: Optional[str] = None,
                           **options) -> dict:
        """Create a scatter plot"""
        fig = go.Figure()

        hover_template = f"<b>{x}</b>: %{{x}}<br><b>{y}</b>: %{{y}}"
        if color:
            hover_template += f"<br><b>{color}</b>: %{{marker.color}}"
        if size:
            hover_template += f"<br><b>{size}</b>: %{{marker.size}}"

        if color and color in data.columns:
            for group_name in data[color].unique():
                group_data = data[data[color] == group_name]
                marker_size = group_data[size] if (size and size in data.columns) else 8

                fig.add_trace(go.Scatter(
                    x=group_data[x],
                    y=group_data[y],
                    mode='markers',
                    name=str(group_name),
                    marker=dict(size=marker_size),
                    text=group_name,
                    hovertemplate=hover_template
                ))
        else:
            marker_size = data[size] if (size and size in data.columns) else 8
            fig.add_trace(go.Scatter(
                x=data[x],
                y=data[y],
                mode='markers',
                marker=dict(size=marker_size),
                hovertemplate=hover_template
            ))

        fig.update_layout(
            title=title or f"{y} vs {x}",
            xaxis_title=x_label or x,
            yaxis_title=y_label or y,
            hovermode='closest',
            template='plotly_white'
        )

        return fig.to_dict()

    @staticmethod
    def create_histogram(data: pd.DataFrame, column: str,
                        bins: int = 30,
                        color: Optional[str] = None,
                        title: Optional[str] = None,
                        x_label: Optional[str] = None,
                        **options) -> dict:
        """Create a histogram"""
        fig = go.Figure()

        if color and color in data.columns:
            for group_name in data[color].unique():
                group_data = data[data[color] == group_name]
                fig.add_trace(go.Histogram(
                    x=group_data[column],
                    name=str(group_name),
                    nbinsx=bins,
                    opacity=0.7
                ))
            fig.update_layout(barmode='overlay')
        else:
            fig.add_trace(go.Histogram(
                x=data[column],
                nbinsx=bins
            ))

        fig.update_layout(
            title=title or f"Distribution of {column}",
            xaxis_title=x_label or column,
            yaxis_title="Frequency",
            template='plotly_white'
        )

        return fig.to_dict()

    @staticmethod
    def create_box_plot(data: pd.DataFrame, x: Optional[str] = None,
                       y: str = None,
                       color: Optional[str] = None,
                       title: Optional[str] = None,
                       **options) -> dict:
        """Create a box plot"""
        fig = go.Figure()

        if x and x in data.columns:
            # Box plot grouped by x
            for group_name in sorted(data[x].unique()):
                group_data = data[data[x] == group_name]
                fig.add_trace(go.Box(
                    y=group_data[y],
                    name=str(group_name),
                    boxmean='sd'
                ))
        else:
            # Single box plot
            fig.add_trace(go.Box(
                y=data[y],
                name=y,
                boxmean='sd'
            ))

        fig.update_layout(
            title=title or f"Box Plot of {y}",
            yaxis_title=y,
            xaxis_title=x if x else "",
            template='plotly_white'
        )

        return fig.to_dict()

    @staticmethod
    def create_violin_plot(data: pd.DataFrame, x: Optional[str] = None,
                          y: str = None,
                          color: Optional[str] = None,
                          title: Optional[str] = None,
                          **options) -> dict:
        """Create a violin plot"""
        fig = go.Figure()

        if x and x in data.columns:
            for group_name in sorted(data[x].unique()):
                group_data = data[data[x] == group_name]
                fig.add_trace(go.Violin(
                    y=group_data[y],
                    name=str(group_name),
                    box_visible=True,
                    meanline_visible=True
                ))
        else:
            fig.add_trace(go.Violin(
                y=data[y],
                name=y,
                box_visible=True,
                meanline_visible=True
            ))

        fig.update_layout(
            title=title or f"Violin Plot of {y}",
            yaxis_title=y,
            xaxis_title=x if x else "",
            template='plotly_white'
        )

        return fig.to_dict()

    @staticmethod
    def create_heatmap(data: pd.DataFrame,
                      title: Optional[str] = None,
                      **options) -> dict:
        """Create a correlation heatmap"""
        # Assume data is a correlation matrix or compute it
        if data.shape[0] != data.shape[1]:
            # Not a correlation matrix, compute it
            numeric_data = data.select_dtypes(include=[np.number])
            corr_matrix = numeric_data.corr()
        else:
            corr_matrix = data

        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))

        fig.update_layout(
            title=title or "Correlation Heatmap",
            xaxis=dict(side='bottom'),
            template='plotly_white'
        )

        return fig.to_dict()

    @staticmethod
    def create_distribution_plot(data: pd.DataFrame, columns: list[str],
                                title: Optional[str] = None,
                                **options) -> dict:
        """Create overlaid distribution plots"""
        fig = go.Figure()

        for col in columns:
            if col in data.columns:
                fig.add_trace(go.Histogram(
                    x=data[col],
                    name=col,
                    opacity=0.6,
                    nbinsx=30
                ))

        fig.update_layout(
            title=title or "Distribution Comparison",
            xaxis_title="Value",
            yaxis_title="Frequency",
            barmode='overlay',
            template='plotly_white'
        )

        return fig.to_dict()

    @staticmethod
    def create_time_series(data: pd.DataFrame, date_column: str,
                          value_columns: list[str],
                          title: Optional[str] = None,
                          **options) -> dict:
        """Create a time series chart"""
        fig = go.Figure()

        for col in value_columns:
            if col in data.columns:
                fig.add_trace(go.Scatter(
                    x=data[date_column],
                    y=data[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(width=2),
                    marker=dict(size=4)
                ))

        fig.update_layout(
            title=title or "Time Series",
            xaxis_title=date_column,
            yaxis_title="Value",
            hovermode='x unified',
            template='plotly_white',
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1d", step="day", stepmode="backward"),
                        dict(count=7, label="1w", step="day", stepmode="backward"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=3, label="3m", step="month", stepmode="backward"),
                        dict(step="all", label="All")
                    ])
                ),
                rangeslider=dict(visible=True),
                type='date'
            )
        )

        return fig.to_dict()

    @staticmethod
    def create_candlestick(data: pd.DataFrame, date_column: str,
                          open_col: str, high_col: str,
                          low_col: str, close_col: str,
                          title: Optional[str] = None,
                          **options) -> dict:
        """Create a candlestick chart (useful for process min/max/avg data)"""
        fig = go.Figure(data=[go.Candlestick(
            x=data[date_column],
            open=data[open_col],
            high=data[high_col],
            low=data[low_col],
            close=data[close_col]
        )])

        fig.update_layout(
            title=title or "Process Data (OHLC)",
            xaxis_title=date_column,
            yaxis_title="Value",
            xaxis_rangeslider_visible=False,
            template='plotly_white'
        )

        return fig.to_dict()

    @staticmethod
    def create_range_plot(data: pd.DataFrame, date_column: str,
                         lower_col: str, upper_col: str,
                         center_col: Optional[str] = None,
                         title: Optional[str] = None,
                         **options) -> dict:
        """Create a range plot with confidence intervals"""
        fig = go.Figure()

        # Add range as filled area
        fig.add_trace(go.Scatter(
            x=data[date_column],
            y=data[upper_col],
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            name='Upper'
        ))

        fig.add_trace(go.Scatter(
            x=data[date_column],
            y=data[lower_col],
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False,
            name='Lower'
        ))

        # Add center line if provided
        if center_col and center_col in data.columns:
            fig.add_trace(go.Scatter(
                x=data[date_column],
                y=data[center_col],
                mode='lines+markers',
                name='Center',
                line=dict(color='blue', width=2),
                marker=dict(size=4)
            ))

        fig.update_layout(
            title=title or "Range Plot",
            xaxis_title=date_column,
            yaxis_title="Value",
            hovermode='x unified',
            template='plotly_white'
        )

        return fig.to_dict()

    @classmethod
    def generate_chart(cls, chart_type: ChartType, data: pd.DataFrame,
                      x: Optional[str] = None,
                      y: Optional[str] = None,
                      color: Optional[str] = None,
                      size: Optional[str] = None,
                      title: Optional[str] = None,
                      x_label: Optional[str] = None,
                      y_label: Optional[str] = None,
                      **options) -> dict:
        """
        Main entry point for chart generation.

        Args:
            chart_type: Type of chart to generate
            data: DataFrame with the data
            x: X-axis column
            y: Y-axis column
            color: Color grouping column
            size: Size column (for scatter)
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            **options: Additional chart-specific options

        Returns:
            Plotly figure dictionary
        """
        if chart_type == ChartType.LINE:
            return cls.create_line_chart(data, x, y, color, title, x_label, y_label, **options)
        elif chart_type == ChartType.BAR:
            return cls.create_bar_chart(data, x, y, color=color, title=title, x_label=x_label, y_label=y_label, **options)
        elif chart_type == ChartType.SCATTER:
            return cls.create_scatter_chart(data, x, y, color, size, title, x_label, y_label, **options)
        elif chart_type == ChartType.HISTOGRAM:
            return cls.create_histogram(data, x or y, color=color, title=title, x_label=x_label, **options)
        elif chart_type == ChartType.BOX:
            return cls.create_box_plot(data, x, y, color, title, **options)
        elif chart_type == ChartType.VIOLIN:
            return cls.create_violin_plot(data, x, y, color, title, **options)
        elif chart_type == ChartType.HEATMAP:
            return cls.create_heatmap(data, title, **options)
        elif chart_type == ChartType.DISTRIBUTION:
            columns = options.get('columns', [x, y] if x and y else [])
            return cls.create_distribution_plot(data, columns, title, **options)
        elif chart_type == ChartType.TIME_SERIES:
            value_cols = options.get('value_columns', [y] if y else [])
            return cls.create_time_series(data, x, value_cols, title, **options)
        elif chart_type == ChartType.CANDLESTICK:
            return cls.create_candlestick(data, x, **options)
        elif chart_type == ChartType.RANGE_PLOT:
            return cls.create_range_plot(data, x, **options)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
