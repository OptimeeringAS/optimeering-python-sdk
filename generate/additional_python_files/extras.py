import functools
from collections import defaultdict
from importlib import import_module
from typing import Any, Callable, Dict, List, Optional

pd: Any = None

try:
    pd = import_module("pandas")
except ImportError:
    PANDAS_AVAILABLE = False
else:
    PANDAS_AVAILABLE = True

polars: Any = None

try:
    polars = import_module("polars")
except ImportError:
    POLARS_AVAILABLE = False
else:
    POLARS_AVAILABLE = True

pyarrow: Any = None

try:
    pyarrow = import_module("pyarrow")
except ImportError:
    PYARROW_AVAILABLE = False
else:
    PYARROW_AVAILABLE = True

STRICT_DATETIME_COLUMNS = {"publication_time", "start", "end", "prediction_for", "event_time"}


def require_pandas(fn: Callable):
    @functools.wraps(fn)
    def inner(cls, *args, **kwargs):
        if not PANDAS_AVAILABLE:
            raise ImportError("Pandas is not available.")
        return fn(cls, *args, **kwargs)

    return inner


def require_polars(fn: Callable):
    @functools.wraps(fn)
    def inner(cls, *args, **kwargs):
        if not POLARS_AVAILABLE:
            raise ImportError("Polars is not available.")
        return fn(cls, *args, **kwargs)

    return inner


def require_pyarrow(fn: Callable):
    @functools.wraps(fn)
    def inner(cls, *args, **kwargs):
        if not PYARROW_AVAILABLE:
            raise ImportError("PyArrow is not available.")
        return fn(cls, *args, **kwargs)

    return inner


ALLOWED_UNPACK_VALUE_METHODS = ("retain_original", "new_rows", "new_columns")
EXPLOSION_COLUMNS = {
    # predictions
    "events": "event",
    "predictions": "prediction",
    "value": "value",
}

EXPLOSION_COLUMNS_POLARS = {
    # predictions
    "events": "event",
    "predictions": "prediction",
    "value": "value",
}

EXPLOSION_COLUMNS_POLARS_KEYS = set(EXPLOSION_COLUMNS_POLARS.keys())


def _merge_resolving_conflicting_columns(
    df_left: "pd.DataFrame", df_right: "pd.DataFrame", expanded_column_name: str
) -> "pd.DataFrame":
    """
    Joins 2 dataframe upon their indices.
    If there are any columns that are conflicting, the column on the right dataframe will be kept
    """
    # Expanded column is no longer required
    del df_left[expanded_column_name]

    columns_only_left = df_left.columns.difference(df_right.columns)
    if len(columns_only_left):
        return pd.merge(df_left[columns_only_left], df_right, left_index=True, right_index=True).reset_index(drop=True)

    return pd.merge(df_left, df_right, left_index=True, right_index=True).reset_index(drop=True)


def pydantic_to_pandas(obj, unpack_value_method: Optional[str] = None) -> "pd.DataFrane":  # type: ignore[name-defined]
    dict_repr = obj.model_dump()
    if "items" in dict_repr:
        dict_repr = dict_repr["items"]

    try:
        df = pd.DataFrame(dict_repr)
    except ValueError as err:
        if "If using all scalar values, you must pass an index" in str(err):
            # if dict_repr is a dict, convert to list
            df = pd.DataFrame([dict_repr])
        else:
            raise err

    while merge_columns := set(EXPLOSION_COLUMNS).intersection(set(df.columns)):
        for merge_column in merge_columns:
            column_type = type(df[merge_column].iloc[0])
            if column_type is list:
                df = df.explode(merge_column).reset_index(drop=True)
                break
            elif column_type is dict:
                if merge_column in ("value",):
                    match unpack_value_method:
                        case "retain_original":
                            continue
                        case "new_rows":
                            df = df.reset_index(drop=True)
                            df_value = (
                                pd.DataFrame(df[merge_column].to_list())
                                .melt(var_name="value_category", value_name="value", ignore_index=False)
                                .dropna(subset=["value"])
                            )
                            df = _merge_resolving_conflicting_columns(df, df_value, merge_column)
                            break
                        case "new_columns":
                            df = df.reset_index(drop=True)
                            df_value = pd.json_normalize(df["value"])
                            df_value = df_value.rename(columns={i: f"value_{i}" for i in df_value.columns})
                            df = _merge_resolving_conflicting_columns(df, df_value, merge_column)
                            break
                        case _:
                            raise ValueError(
                                f"`unpack_value_method` must be used, and be one of {','.join(ALLOWED_UNPACK_VALUE_METHODS)}"
                            )
                else:
                    # If columns are of type dict, make each record a new column
                    df = df.reset_index(drop=True)
                    df_value = pd.DataFrame.from_dict(df[merge_column].to_list())
                    df = _merge_resolving_conflicting_columns(df, df_value, merge_column)
                    break
        else:
            # All columns that needs to be operated on has been completed
            # Break the while loop.
            break
    datetime_columns = STRICT_DATETIME_COLUMNS.intersection(df.columns)
    for col in datetime_columns:
        df[col] = pd.to_datetime(df[col], utc=True)
    return df


def flatten_dict_columns_value(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    values = dictionary["value"]
    if isinstance(values, dict):
        dictionary.pop("value")
        columns_dict = {f"value_{item_key}": item for item_key, item in values.items()}
        columns_dict.update(dictionary)

        return columns_dict
    return dictionary


def flatten_dict_columns(dictionary: Dict[str, Any]) -> List[Dict[str, Any]]:
    intersection_keys = EXPLOSION_COLUMNS_POLARS_KEYS.intersection(dictionary)
    assert len(intersection_keys) == 1, f"Only one column is supported to explode {intersection_keys}"
    key = intersection_keys.pop()

    values = dictionary.pop(key)
    items: List[Dict[str, Any]] = []
    for item in values:
        if "value" in item:
            flat_value: Dict[str, Any] = flatten_dict_columns_value(item)
            flat_value.update(dictionary)
            items.append(flat_value)
        else:
            flat_child: List[Dict[str, Any]] = flatten_dict_columns(item)
            for child_item in flat_child:
                child_item.update(dictionary)
                items.append(child_item)
    return items


def flatten_dict_rows(
    dictionary: Dict[str, Any], output: Dict[str, Any], unpack_value_method: Optional[str] = None
) -> int:

    for key in EXPLOSION_COLUMNS_POLARS_KEYS.intersection(dictionary):
        values = dictionary[key]

        if key == "value":
            if isinstance(values, dict) and unpack_value_method == "new_rows":
                dictionary.pop(key)
                output[EXPLOSION_COLUMNS[key]].extend(values.values())
                output["value_category"].extend(values.keys())
                unpack_dict(dictionary, output, len(values))

                return len(values)
            else:
                unpack_dict(dictionary, output)
                return 1

        elif isinstance(values, list):
            dictionary.pop(key)
            count_items = 0

            conflict_columns = set(dictionary).intersection(values[0])

            for column_name in conflict_columns:
                dictionary.pop(column_name)

            for item in values:
                count_flat_child = flatten_dict_rows(item, output, unpack_value_method)
                unpack_dict(dictionary, output, count_flat_child)
                count_items += count_flat_child

            return count_items

    unpack_dict(dictionary, output)
    return 1


def nothing_to_explode(dictionary: Dict) -> bool:
    return len(EXPLOSION_COLUMNS_POLARS_KEYS.intersection(set(dictionary.keys()))) == 0


def unpack_dict(data: Dict[str, Any], out: Dict[str, List], count: int = 1):
    if count == 1:
        for k in data:
            out[k].append(data[k])
    else:
        for k in data:
            out[k].extend((data[k],) * count)


def flatten_data(obj, unpack_value_method: Optional[str] = None):
    dict_data = obj.model_dump()["items"]
    if unpack_value_method == "new_columns":
        output_columns: List[Dict[str, Any]] = []
        for item in dict_data:
            flat_item: List[Dict[str, Any]] = flatten_dict_columns(item)
            output_columns.extend(flat_item)
        return output_columns
    else:
        output_rows: Dict[str, List] = defaultdict(list)
        if nothing_to_explode(dict_data[-1]):
            for item in dict_data:
                unpack_dict(item, output_rows)
        else:
            for item in dict_data:
                flatten_dict_rows(item, output_rows, unpack_value_method=unpack_value_method)
        return output_rows


def pydantic_to_polars(obj, unpack_value_method: Optional[str] = None) -> "polars.DataFrame":  # type: ignore[name-defined]
    if unpack_value_method is not None and unpack_value_method not in ALLOWED_UNPACK_VALUE_METHODS:
        raise ValueError(f"`unpack_value_method` must be used, and be one of {','.join(ALLOWED_UNPACK_VALUE_METHODS)}")

    items = flatten_data(obj, unpack_value_method=unpack_value_method)
    if unpack_value_method == "retain_original":
        if isinstance(items["value"][0], dict):
            items["value"] = polars.Series(items["value"], dtype=polars.Object)
        return polars.DataFrame(items)

    elif unpack_value_method == "new_columns":
        return polars.DataFrame(items, infer_schema_length=None)

    return (
        polars.LazyFrame(pyarrow.table(items))
        .cast({polars.Datetime: polars.Datetime(time_unit="ns", time_zone="UTC")})
        .collect()
    )
