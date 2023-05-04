"""Decorators for validating column names and data types of function inputs and outputs.

This module offers decorators to annotate functions which validate the input and output columns and data types in functions which input or return pandas dataframes.
from .pandas_decorators import df_in  # noqa
from .pandas_decorators import df_log  # noqa
from .pandas_decorators import df_out  # noqa
"""
import inspect
import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union
import pandas as pd

ColumnsDef = Union[List, Dict]

def _check_columns(df: pd.DataFrame, columns: ColumnsDef, strict: bool) -> None:
    if isinstance(columns, list):
        for column in columns:
            assert column in df.columns, f"Column {column} missing from DataFrame. Got {_describe_pd(df)}"
    if isinstance(columns, dict):
        for column, dtype in columns.items():
            assert column in df.columns, f"Column {column} missing from DataFrame. Got {_describe_pd(df)}"
            assert (
                df[column].dtype == dtype
            ), f"Column {column} has wrong dtype. Was {df[column].dtype}, expected {dtype}"
    if strict:
        assert len(df.columns) == len(
            columns
        ), f"DataFrame contained unexpected column(s): {', '.join(set(df.columns) - set(columns))}"

def df_out(columns: Optional[ColumnsDef] = None, strict: bool = False) -> Callable:
    """Decorate a function that returns a Pandas DataFrame.

    Document the return value of a function. The return value will be validated in runtime.

    Args:
        columns (ColumnsDef, optional): List or dict that describes expected columns of the DataFrame. Defaults to None.
        strict (bool, optional): If True, columns must match exactly with no extra columns. Defaults to False.

    Returns:
        Callable: Decorated function
    """

    def wrapper_df_out(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: str, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            assert isinstance(result, pd.DataFrame), f"Wrong return type. Expected pandas dataframe, got {type(result)}"
            if columns:
                _check_columns(result, columns, strict)
            return result

        return wrapper

    return wrapper_df_out

def _get_parameter(func: Callable, name: Optional[str] = None, *args: str, **kwargs: Any) -> pd.DataFrame:
    if not name:
        if len(args) == 0:
            return None
        return args[0]

    if name and (name not in kwargs):
        func_params_in_order = list(inspect.signature(func).parameters.keys())
        parameter_location = func_params_in_order.index(name)
        return args[parameter_location]

    return kwargs[name]

def df_in(name: Optional[str] = None, columns: Optional[ColumnsDef] = None, strict: bool = False) -> Callable:
    """Decorate a function parameter that is a Pandas DataFrame.

    Document the contents of an inpute parameter. The parameter will be validated in runtime.

    Args:
        name (Optional[str], optional): Name of the parameter that contains a DataFrame. Defaults to None.
        columns (ColumnsDef, optional): List or dict that describes expected columns of the DataFrame. Defaults to None.
        strict (bool, optional): If True, columns must match exactly with no extra columns. Defaults to False.

    Returns:
        Callable: Decorated function
    """

    def wrapper_df_in(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: str, **kwargs: Any) -> Any:
            df = _get_parameter(func, name, *args, **kwargs)
            assert isinstance(
                df, pd.DataFrame
            ), f"Wrong parameter type. Expected Pandas DataFrame, got {type(df).__name__} instead."
            if columns:
                _check_columns(df, columns, strict)
            return func(*args, **kwargs)

        return wrapper

    return wrapper_df_in

def _describe_pd(df: pd.DataFrame, include_dtypes: bool = False) -> str:
    result = f"columns: {list(df.columns)}"
    if include_dtypes:
        readable_dtypes = [dtype.name for dtype in df.dtypes]
        result += f" with dtypes {readable_dtypes}"
    return result

def _log_input(level: int, func_name: str, df: Any, include_dtypes: bool) -> None:
    if isinstance(df, pd.DataFrame):
        logging.log(
            level,
            f"Function {func_name} parameters contained a DataFrame: {_describe_pd(df, include_dtypes)}",
        )

def _log_output(level: int, func_name: str, df: Any, include_dtypes: bool) -> None:
    if isinstance(df, pd.DataFrame):
        logging.log(
            level,
            f"Function {func_name} returned a DataFrame: {_describe_pd(df, include_dtypes)}",
        )

def df_log(level: int = logging.DEBUG, include_dtypes: bool = False) -> Callable:
    """Decorate a function that consumes or produces a Pandas DataFrame or both.

    Logs the columns of the consumed and/or produced DataFrame.

    Args:
        level (int, optional): Level of the logging messages produced. Defaults to logging.DEBUG.
        include_dtypes (bool, optional): When set to True, will log also the dtypes of each column. Defaults to False.

    Returns:
        Callable: Decorated function.
    """

    def wrapper_df_log(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: str, **kwargs: Any) -> Any:
            _log_input(level, func.__name__, _get_parameter(func, None, *args, **kwargs), include_dtypes)
            result = func(*args, **kwargs)
            _log_output(level, func.__name__, result, include_dtypes)

        return wrapper

    return wrapper_df_log