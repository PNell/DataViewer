"""
Data analysis utilities for exploratory data analysis (EDA).
"""
import pandas as pd
import numpy as np
from typing import Optional, Literal
from app.models.schemas import ChartType, ChartSuggestion, SummaryStats


class DataAnalyzer:
    """Utility class for data analysis and EDA"""

    @staticmethod
    def detect_outliers(df: pd.DataFrame, column: str,
                       method: Literal["iqr", "zscore"] = "iqr",
                       threshold: float = 1.5) -> tuple[list[int], list]:
        """
        Detect outliers in a column using IQR or Z-score method.

        Args:
            df: DataFrame
            column: Column name
            method: Detection method ('iqr' or 'zscore')
            threshold: Threshold value (1.5 for IQR, 3.0 for Z-score typically)

        Returns:
            Tuple of (outlier_indices, outlier_values)
        """
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found")

        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(f"Column '{column}' must be numeric")

        data = df[column].dropna()

        if method == "iqr":
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            outlier_mask = (data < lower_bound) | (data > upper_bound)

        elif method == "zscore":
            z_scores = np.abs((data - data.mean()) / data.std())
            outlier_mask = z_scores > threshold

        else:
            raise ValueError(f"Unknown method: {method}")

        outlier_indices = data[outlier_mask].index.tolist()
        outlier_values = data[outlier_mask].tolist()

        return outlier_indices, outlier_values

    @staticmethod
    def get_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate correlation matrix for numeric columns.

        Args:
            df: DataFrame

        Returns:
            Correlation matrix
        """
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            raise ValueError("No numeric columns found for correlation analysis")

        return numeric_df.corr()

    @staticmethod
    def get_distribution_stats(df: pd.DataFrame, column: str) -> dict:
        """
        Get distribution statistics for a column.

        Args:
            df: DataFrame
            column: Column name

        Returns:
            Dictionary with statistics
        """
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found")

        data = df[column]

        stats = {
            "count": int(data.count()),
            "null_count": int(data.isna().sum()),
            "unique_count": int(data.nunique())
        }

        if pd.api.types.is_numeric_dtype(data):
            stats.update({
                "mean": float(data.mean()) if not data.empty else None,
                "median": float(data.median()) if not data.empty else None,
                "std": float(data.std()) if not data.empty else None,
                "min": float(data.min()) if not data.empty else None,
                "max": float(data.max()) if not data.empty else None,
                "q25": float(data.quantile(0.25)) if not data.empty else None,
                "q75": float(data.quantile(0.75)) if not data.empty else None,
                "skewness": float(data.skew()) if not data.empty else None,
                "kurtosis": float(data.kurtosis()) if not data.empty else None
            })
        else:
            # For categorical data
            value_counts = data.value_counts()
            stats.update({
                "most_common": value_counts.index[0] if not value_counts.empty else None,
                "most_common_count": int(value_counts.iloc[0]) if not value_counts.empty else None,
                "least_common": value_counts.index[-1] if not value_counts.empty else None,
                "least_common_count": int(value_counts.iloc[-1]) if not value_counts.empty else None
            })

        return stats

    @staticmethod
    def detect_time_series(df: pd.DataFrame) -> list[str]:
        """
        Identify datetime columns in the DataFrame.

        Args:
            df: DataFrame

        Returns:
            List of datetime column names
        """
        datetime_cols = []

        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                datetime_cols.append(col)

        return datetime_cols

    @staticmethod
    def suggest_chart_types(df: pd.DataFrame, max_suggestions: int = 10) -> list[ChartSuggestion]:
        """
        Suggest appropriate chart types based on data characteristics.

        Args:
            df: DataFrame
            max_suggestions: Maximum number of suggestions

        Returns:
            List of chart suggestions
        """
        suggestions = []
        priority = 1

        # Get column types
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = DataAnalyzer.detect_time_series(df)

        # Time series suggestions (highest priority)
        if datetime_cols and numeric_cols:
            for dt_col in datetime_cols[:2]:  # Limit to first 2 datetime columns
                for num_col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                    suggestions.append(ChartSuggestion(
                        chart_type=ChartType.TIME_SERIES,
                        x_column=dt_col,
                        y_column=num_col,
                        reason=f"Time series analysis of {num_col} over {dt_col}",
                        priority=priority
                    ))
                    priority += 1

        # Correlation heatmap for multiple numeric columns
        if len(numeric_cols) >= 3:
            suggestions.append(ChartSuggestion(
                chart_type=ChartType.HEATMAP,
                x_column=None,
                y_column=None,
                reason="Correlation analysis between numeric variables",
                priority=priority
            ))
            priority += 1

        # Distribution plots for numeric columns
        for col in numeric_cols[:3]:
            suggestions.append(ChartSuggestion(
                chart_type=ChartType.HISTOGRAM,
                x_column=col,
                y_column=None,
                reason=f"Distribution analysis of {col}",
                priority=priority
            ))
            priority += 1

        # Box plots for numeric vs categorical
        if categorical_cols and numeric_cols:
            for cat_col in categorical_cols[:2]:
                unique_count = df[cat_col].nunique()
                if 2 <= unique_count <= 10:  # Reasonable number of categories
                    for num_col in numeric_cols[:2]:
                        suggestions.append(ChartSuggestion(
                            chart_type=ChartType.BOX,
                            x_column=cat_col,
                            y_column=num_col,
                            reason=f"Compare {num_col} distribution across {cat_col} categories",
                            priority=priority
                        ))
                        priority += 1

        # Scatter plots for numeric pairs
        if len(numeric_cols) >= 2:
            # Suggest scatter for pairs with high correlation
            try:
                corr_matrix = DataAnalyzer.get_correlation_matrix(df)
                for i, col1 in enumerate(numeric_cols[:5]):
                    for col2 in numeric_cols[i+1:6]:
                        if col1 in corr_matrix.index and col2 in corr_matrix.columns:
                            corr_value = abs(corr_matrix.loc[col1, col2])
                            if corr_value > 0.5:  # High correlation
                                suggestions.append(ChartSuggestion(
                                    chart_type=ChartType.SCATTER,
                                    x_column=col1,
                                    y_column=col2,
                                    reason=f"Correlation between {col1} and {col2} (r={corr_value:.2f})",
                                    priority=priority
                                ))
                                priority += 1
            except:
                pass

        # Bar chart for categorical columns
        for col in categorical_cols[:3]:
            unique_count = df[col].nunique()
            if 2 <= unique_count <= 20:
                suggestions.append(ChartSuggestion(
                    chart_type=ChartType.BAR,
                    x_column=col,
                    y_column=None,
                    reason=f"Frequency distribution of {col}",
                    priority=priority
                ))
                priority += 1

        # Sort by priority and limit
        suggestions.sort(key=lambda x: x.priority)
        return suggestions[:max_suggestions]

    @staticmethod
    def get_summary_stats_list(df: pd.DataFrame) -> list[SummaryStats]:
        """
        Get summary statistics for all columns.

        Args:
            df: DataFrame

        Returns:
            List of SummaryStats
        """
        stats_list = []

        for col in df.columns:
            data = df[col]
            stat = SummaryStats(
                column=col,
                count=int(data.count()),
                null_count=int(data.isna().sum()),
                unique_values=int(data.nunique())
            )

            if pd.api.types.is_numeric_dtype(data):
                if not data.empty:
                    stat.mean = float(data.mean())
                    stat.std = float(data.std())
                    stat.min = float(data.min())
                    stat.max = float(data.max())
                    stat.q25 = float(data.quantile(0.25))
                    stat.median = float(data.median())
                    stat.q75 = float(data.quantile(0.75))

            stats_list.append(stat)

        return stats_list
