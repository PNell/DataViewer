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
                         y_columns: Optional[list[str]] = None,
                         secondary_y_columns: Optional[list[str]] = None,
                         **options) -> dict:
        """Create a line chart with optional multi-Y columns and secondary axis"""
        fig = go.Figure()

        # Determine which columns to plot
        columns_to_plot = y_columns if y_columns else [y]
        secondary_cols = set(secondary_y_columns or [])
        has_secondary = len(secondary_cols) > 0

        if color and color in data.columns:
            # Grouped by color — use first Y column only to avoid trace explosion
            plot_y = columns_to_plot[0]
            for group_name in data[color].unique():
                group_data = data[data[color] == group_name]
                fig.add_trace(go.Scatter(
                    x=group_data[x],
                    y=group_data[plot_y],
                    mode='lines+markers',
                    name=str(group_name),
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
        else:
            # Multiple Y columns
            for col in columns_to_plot:
                if col not in data.columns:
                    continue
                trace_kwargs = dict(
                    x=data[x],
                    y=data[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(width=2),
                    marker=dict(size=6)
                )
                if has_secondary and col in secondary_cols:
                    trace_kwargs['yaxis'] = 'y2'
                fig.add_trace(go.Scatter(**trace_kwargs))

        # Build layout
        layout = dict(
            title=title or f"{', '.join(columns_to_plot)} vs {x}",
            xaxis_title=x_label or x,
            hovermode='closest',
            template='plotly_white'
        )

        if has_secondary:
            primary_cols = [c for c in columns_to_plot if c not in secondary_cols]
            layout['yaxis'] = dict(
                title=y_label or (', '.join(primary_cols) if primary_cols else 'Primary'),
                side='left'
            )
            layout['yaxis2'] = dict(
                title=', '.join(secondary_cols),
                side='right',
                overlaying='y',
                showgrid=False
            )
        else:
            layout['yaxis_title'] = y_label or (columns_to_plot[0] if len(columns_to_plot) == 1 else "Value")

        fig.update_layout(**layout)

        return fig.to_dict()

    @staticmethod
    def create_bar_chart(data: pd.DataFrame, x: str, y: Optional[str] = None,
                        orientation: str = 'v',
                        color: Optional[str] = None,
                        title: Optional[str] = None,
                        x_label: Optional[str] = None,
                        y_label: Optional[str] = None,
                        bar_mode: str = 'group',
                        sort_order: str = '',
                        **options) -> dict:
        """Create a bar chart with stacked/grouped mode and sorting"""
        fig = go.Figure()

        # Apply sorting
        plot_data = data.copy()
        if sort_order and y and y in plot_data.columns and x in plot_data.columns:
            if sort_order == 'asc':
                plot_data = plot_data.sort_values(by=y, ascending=True)
            elif sort_order == 'desc':
                plot_data = plot_data.sort_values(by=y, ascending=False)
            elif sort_order == 'alpha':
                plot_data = plot_data.sort_values(by=x, ascending=True)

        if y is None:
            # Count frequency
            counts = plot_data[x].value_counts()
            if sort_order == 'asc':
                counts = counts.sort_values(ascending=True)
            elif sort_order == 'desc':
                counts = counts.sort_values(ascending=False)
            elif sort_order == 'alpha':
                counts = counts.sort_index(ascending=True)
            else:
                counts = counts.sort_index()

            if orientation == 'v':
                fig.add_trace(go.Bar(x=counts.index, y=counts.values))
            else:
                fig.add_trace(go.Bar(y=counts.index, x=counts.values, orientation='h'))
        else:
            # Use y values
            if color and color in plot_data.columns:
                for group_name in plot_data[color].unique():
                    group_data = plot_data[plot_data[color] == group_name]
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
                    fig.add_trace(go.Bar(x=plot_data[x], y=plot_data[y]))
                else:
                    fig.add_trace(go.Bar(y=plot_data[x], x=plot_data[y], orientation='h'))

        fig.update_layout(
            title=title or f"Bar Chart",
            xaxis_title=x_label or (x if orientation == 'v' else (y if y else "Count")),
            yaxis_title=y_label or ((y if y else "Count") if orientation == 'v' else x),
            template='plotly_white',
            barmode=bar_mode
        )

        return fig.to_dict()

    @staticmethod
    def create_scatter_chart(data: pd.DataFrame, x: str, y: str,
                           color: Optional[str] = None,
                           size: Optional[str] = None,
                           title: Optional[str] = None,
                           x_label: Optional[str] = None,
                           y_label: Optional[str] = None,
                           show_trendline: bool = False,
                           trendline_degree: int = 1,
                           color_numeric: Optional[str] = None,
                           **options) -> dict:
        """Create a scatter plot with optional trendline and numeric color"""
        fig = go.Figure()

        hover_template = f"<b>{x}</b>: %{{x}}<br><b>{y}</b>: %{{y}}"
        if color:
            hover_template += f"<br><b>{color}</b>: %{{text}}"
        if size:
            hover_template += f"<br><b>{size}</b>: %{{marker.size}}"

        if color_numeric and color_numeric in data.columns:
            # Continuous numeric color mapping
            marker_size = data[size] if (size and size in data.columns) else 8
            fig.add_trace(go.Scatter(
                x=data[x],
                y=data[y],
                mode='markers',
                marker=dict(
                    size=marker_size,
                    color=data[color_numeric],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title=color_numeric)
                ),
                hovertemplate=f"<b>{x}</b>: %{{x}}<br><b>{y}</b>: %{{y}}<br><b>{color_numeric}</b>: %{{marker.color}}<extra></extra>"
            ))
        elif color and color in data.columns:
            for group_name in data[color].unique():
                group_data = data[data[color] == group_name]
                marker_size = group_data[size] if (size and size in data.columns) else 8

                fig.add_trace(go.Scatter(
                    x=group_data[x],
                    y=group_data[y],
                    mode='markers',
                    name=str(group_name),
                    marker=dict(size=marker_size),
                    text=str(group_name),
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

        # Trendline
        if show_trendline:
            clean = data[[x, y]].dropna()
            x_vals = pd.to_numeric(clean[x], errors='coerce')
            y_vals = pd.to_numeric(clean[y], errors='coerce')
            mask = x_vals.notna() & y_vals.notna()
            x_vals = x_vals[mask].values
            y_vals = y_vals[mask].values

            if len(x_vals) > 1:
                degree = max(1, min(trendline_degree, 5))
                coeffs = np.polyfit(x_vals, y_vals, degree)
                x_sorted = np.sort(x_vals)
                y_fit = np.polyval(coeffs, x_sorted)

                # Calculate R-squared
                y_pred = np.polyval(coeffs, x_vals)
                ss_res = np.sum((y_vals - y_pred) ** 2)
                ss_tot = np.sum((y_vals - np.mean(y_vals)) ** 2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

                # Build equation string
                if degree == 1:
                    eq_str = f"y = {coeffs[0]:.2f}x + {coeffs[1]:.2f}"
                else:
                    terms = []
                    for i, c in enumerate(coeffs):
                        power = degree - i
                        if power == 0:
                            terms.append(f"{c:.2f}")
                        elif power == 1:
                            terms.append(f"{c:.2f}x")
                        else:
                            terms.append(f"{c:.2f}x^{power}")
                    eq_str = " + ".join(terms)

                fig.add_trace(go.Scatter(
                    x=x_sorted,
                    y=y_fit,
                    mode='lines',
                    name=f'Trendline (R²={r_squared:.4f})',
                    line=dict(color='red', width=2, dash='dash')
                ))

                # Add equation annotation below the plot area
                # fig.add_annotation(
                #     text=f"{eq_str}  |  R² = {r_squared:.4f}",
                #     # xref="paper", yref="paper",
                #     # # x=0.5, y=-0.15,
                #     # xanchor="center", yanchor="bottom",
                #     showarrow=False,
                #     bordercolor="black",
                #     borderwidth=1,
                #     borderpad=4,
                #     bgcolor="rgba(255, 255, 255, 0.85)",
                #     font=dict(family="monospace", size=11),
                #     align="center"
                # )

        fig.update_layout(
            title=title or f"{y} vs {x}",
            xaxis_title=x_label or x,
            yaxis_title=y_label or y,
            hovermode='closest',
            template='plotly_white',
            margin=dict(b=80) if show_trendline else None,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            ) if (color or color_numeric) else None
        )

        return fig.to_dict()

    @staticmethod
    def create_histogram(data: pd.DataFrame, column: str,
                        bins: int = 30,
                        color: Optional[str] = None,
                        title: Optional[str] = None,
                        x_label: Optional[str] = None,
                        show_distribution_fit: bool = False,
                        show_statistics: bool = False,
                        **options) -> dict:
        """Create a histogram with optional distribution fit and statistics"""
        fig = go.Figure()

        col_data = data[column].dropna()

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
                x=col_data,
                nbinsx=bins,
                name=column,
                histnorm='probability density' if show_distribution_fit else None
            ))

        # Distribution fit overlay
        if show_distribution_fit and len(col_data) > 1:
            from scipy import stats as scipy_stats

            mu, sigma = scipy_stats.norm.fit(col_data)
            x_range = np.linspace(float(col_data.min()), float(col_data.max()), 200)
            pdf_values = scipy_stats.norm.pdf(x_range, mu, sigma)

            fig.add_trace(go.Scatter(
                x=x_range,
                y=pdf_values,
                mode='lines',
                name=f'Normal Fit (\u03bc={mu:.2f}, \u03c3={sigma:.2f})',
                line=dict(color='red', width=2.5)
            ))

        # Statistics annotation
        if show_statistics and len(col_data) > 0:
            from scipy import stats as scipy_stats

            n = len(col_data)
            mean_val = float(col_data.mean())
            std_val = float(col_data.std())
            median_val = float(col_data.median())
            skewness = float(col_data.skew())
            kurtosis = float(col_data.kurtosis())

            # Shapiro-Wilk test (limit sample size for performance)
            sample = col_data if n <= 5000 else col_data.sample(5000, random_state=42)
            try:
                _, shapiro_p = scipy_stats.shapiro(sample)
            except Exception:
                shapiro_p = None

            stats_lines = [
                f"<b>Statistics</b>",
                f"n = {n:,}",
                f"Mean = {mean_val:.4f}",
                f"Std = {std_val:.4f}",
                f"Median = {median_val:.4f}",
                f"Skewness = {skewness:.4f}",
                f"Kurtosis = {kurtosis:.4f}",
            ]
            if shapiro_p is not None:
                stats_lines.append(f"Shapiro-Wilk p = {shapiro_p:.4e}")

            fig.add_annotation(
                text="<br>".join(stats_lines),
                xref="paper", yref="paper",
                x=0.98, y=0.98,
                xanchor="right", yanchor="top",
                showarrow=False,
                bordercolor="black",
                borderwidth=1,
                borderpad=6,
                bgcolor="rgba(255, 255, 255, 0.85)",
                font=dict(family="monospace", size=11),
                align="left"
            )

        fig.update_layout(
            title=title or f"Distribution of {column}",
            xaxis_title=x_label or column,
            yaxis_title="Probability Density" if show_distribution_fit else "Frequency",
            template='plotly_white'
        )

        return fig.to_dict()

    @staticmethod
    def create_box_plot(data: pd.DataFrame, x: Optional[str] = None,
                       y: str = None,
                       color: Optional[str] = None,
                       title: Optional[str] = None,
                       show_points: bool = False,
                       horizontal: bool = False,
                       **options) -> dict:
        """Create a box plot with optional data points and horizontal orientation"""
        fig = go.Figure()

        box_kwargs = {}
        if show_points:
            box_kwargs['boxpoints'] = 'all'
            box_kwargs['jitter'] = 0.3
            box_kwargs['pointpos'] = -1.5

        if x and x in data.columns:
            for group_name in sorted(data[x].unique()):
                group_data = data[data[x] == group_name]
                if horizontal:
                    fig.add_trace(go.Box(
                        x=group_data[y],
                        name=str(group_name),
                        boxmean='sd',
                        **box_kwargs
                    ))
                else:
                    fig.add_trace(go.Box(
                        y=group_data[y],
                        name=str(group_name),
                        boxmean='sd',
                        **box_kwargs
                    ))
        else:
            if horizontal:
                fig.add_trace(go.Box(
                    x=data[y],
                    name=y,
                    boxmean='sd',
                    **box_kwargs
                ))
            else:
                fig.add_trace(go.Box(
                    y=data[y],
                    name=y,
                    boxmean='sd',
                    **box_kwargs
                ))

        if horizontal:
            fig.update_layout(
                title=title or f"Box Plot of {y}",
                xaxis_title=y,
                yaxis_title=x if x else "",
                template='plotly_white'
            )
        else:
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
                          show_points: bool = False,
                          horizontal: bool = False,
                          **options) -> dict:
        """Create a violin plot with optional data points and horizontal orientation"""
        fig = go.Figure()

        violin_kwargs = {}
        if show_points:
            violin_kwargs['points'] = 'all'
            violin_kwargs['jitter'] = 0.3
            violin_kwargs['pointpos'] = -1.5

        if x and x in data.columns:
            for group_name in sorted(data[x].unique()):
                group_data = data[data[x] == group_name]
                if horizontal:
                    fig.add_trace(go.Violin(
                        x=group_data[y],
                        name=str(group_name),
                        box_visible=True,
                        meanline_visible=True,
                        orientation='h',
                        **violin_kwargs
                    ))
                else:
                    fig.add_trace(go.Violin(
                        y=group_data[y],
                        name=str(group_name),
                        box_visible=True,
                        meanline_visible=True,
                        **violin_kwargs
                    ))
        else:
            if horizontal:
                fig.add_trace(go.Violin(
                    x=data[y],
                    name=y,
                    box_visible=True,
                    meanline_visible=True,
                    orientation='h',
                    **violin_kwargs
                ))
            else:
                fig.add_trace(go.Violin(
                    y=data[y],
                    name=y,
                    box_visible=True,
                    meanline_visible=True,
                    **violin_kwargs
                ))

        if horizontal:
            fig.update_layout(
                title=title or f"Violin Plot of {y}",
                xaxis_title=y,
                yaxis_title=x if x else "",
                template='plotly_white'
            )
        else:
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
                      colorscale: str = 'RdBu',
                      show_annotations: bool = True,
                      **options) -> dict:
        """Create a correlation heatmap with configurable colorscale and annotations"""
        # Assume data is a correlation matrix or compute it
        if data.shape[0] != data.shape[1]:
            # Not a correlation matrix, compute it
            numeric_data = data.select_dtypes(include=[np.number])
            corr_matrix = numeric_data.corr()
        else:
            corr_matrix = data

        heatmap_kwargs = dict(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale=colorscale,
            zmid=0,
            colorbar=dict(title="Correlation")
        )

        if show_annotations:
            heatmap_kwargs['text'] = corr_matrix.values
            heatmap_kwargs['texttemplate'] = '%{text:.2f}'
            heatmap_kwargs['textfont'] = {"size": 10}

        fig = go.Figure(data=go.Heatmap(**heatmap_kwargs))

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
