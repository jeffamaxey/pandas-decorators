# pandas-decorators
Function decorators for validating column names and data types of pandas dataframes.  

## Description 

In projects using Pandas, it's very common to have functions that take Pandas DataFrames as input or produce them as output.
It's hard to figure out quickly what these DataFrames contain. This library offers simple decorators to annotate your functions
so that they document themselves and that documentation is kept up-to-date by validating the input and output on runtime.

For example,

```python
@df_in(columns=["Brand", "Price"])     # the function expects a DataFrame as input parameter with columns Brand and Price
@df_out(columns=["Brand", "Price"])    # the function will return a DataFrame with columns Brand and Price
def filter_cars(car_df):
    # before this code is executed, the input DataFrame is validated according to the above decorator
    # filter some cars..
    return filtered_cars_df
```

## Table of Contents
* [Installation](#installation)
* [Usage](#usage)

## Installation

Install with your favorite Python dependency manager like

```sh
pip install pandas-decorators
```

## Usage 

Start by importing the needed decorators:

```python
from pandas_decorators import df_in, df_out
```

To check a DataFrame input to a function, annotate the function with `@df_in`. For example the following function expects to get
a DataFrame with columns `Brand` and `Price`:

```python
@df_in(columns=["Brand", "Price"])
def process_cars(car_df):
    # do stuff with cars
```

If your function takes multiple arguments, specify the field to be checked with it's `name`:

```python
@df_in(name="car_df", columns=["Brand", "Price"])
def process_cars(year, style, car_df):
    # do stuff with cars
```

You can also check columns of multiple arguments if you specify the names
```python
@df_in(name="car_df", columns=["Brand", "Price"])
@df_in(name="brand_df", columns=["Brand", "BrandName"])
def process_cars(car_df, brand_df):
    # do stuff with cars
```

To check that a function returns a DataFrame with specific columns, use `@df_out` decorator:

```python
@df_out(columns=["Brand", "Price"])
def get_all_cars():
    # get those cars
    return all_cars_df
```

In case one of the listed columns is missing from the DataFrame, a helpful assertion error is thrown:

```python
AssertionError("Column Price missing from DataFrame. Got columns: ['Brand']")
```

To check both input and output, just use both annotations on the same function:

```python
@df_in(columns=["Brand", "Price"])
@df_out(columns=["Brand", "Price"])
def filter_cars(car_df):
    # filter some cars
    return filtered_cars_df
```

If you want to also check the data types of each column, you can replace the column array:

```python
columns=["Brand", "Price"]
```

with a dict:

```python
columns={"Brand": "object", "Price": "int64"}
```

This will not only check that the specified columns are found from the DataFrame but also that their `dtype` is the expected.
In case of a wrong `dtype`, an error message similar to following will explain the mismatch:

```
AssertionError("Column Price has wrong dtype. Was int64, expected float64")
```

You can enable strict-mode for both `@df_in` and `@df_out`. This will raise an error if the DataFrame contains columns
not defined in the annotation:

```python
@df_in(columns=["Brand"], strict=True)
def process_cars(car_df):
    # do stuff with cars
```

will, when `car_df` contains columns `["Brand", "Price"]` raise an error:

```
AssertionError: DataFrame contained unexpected column(s): Price
```

To quickly check what the incoming and outgoing dataframes contain, you can add a `@df_log` annotation to the function. For
example adding `@df_log` to the above `filter_cars` function will product log lines:

```
Function filter_cars parameters contained a DataFrame: columns: ['Brand', 'Price']
Function filter_cars returned a DataFrame: columns: ['Brand', 'Price']
```

or with `@df_log(include_dtypes=True)` you get:

```
Function filter_cars parameters contained a DataFrame: columns: ['Brand', 'Price'] with dtypes ['object', 'int64']
Function filter_cars returned a DataFrame: columns: ['Brand', 'Price'] with dtypes ['object', 'int64']
```
