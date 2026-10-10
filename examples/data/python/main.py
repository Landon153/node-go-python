"""Offline, deterministic data-flow lab. This is not a benchmark or quality claim."""
import json
from pathlib import Path
import tempfile

import duckdb
import numpy as np
import pandas as pd
import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq
from sklearn.linear_model import LinearRegression


def main():
    orders = pd.DataFrame({
        "customer": ["An", "An", "Binh", "Chi"],
        "amount": [20, 30, 10, 40],
    })
    expected = {"An": 50, "Binh": 10, "Chi": 40}
    pandas_totals = orders.groupby("customer")["amount"].sum().to_dict()
    with tempfile.TemporaryDirectory(prefix="node-go-python-data-") as directory:
        artifact = Path(directory) / "orders.parquet"
        pq.write_table(pa.Table.from_pandas(orders, preserve_index=False), artifact)
        polars_rows = (pl.scan_parquet(artifact)
                       .group_by("customer").agg(pl.col("amount").sum())
                       .collect().iter_rows())
        polars_totals = dict(polars_rows)
        with duckdb.connect() as con:
            duckdb_totals = dict(con.execute(
                "SELECT customer, SUM(amount) FROM read_parquet(?) GROUP BY customer",
                [str(artifact)],
            ).fetchall())
    assert pandas_totals == polars_totals == duckdb_totals == expected
    amounts = orders["amount"].to_numpy(dtype=np.float64)
    centered = amounts - amounts.mean()
    np.testing.assert_allclose(centered, [-5, 5, -15, 15])
    # y = 2*x on toy data demonstrates fit/predict, not held-out evaluation.
    x = np.array([[1.0], [2.0], [3.0], [4.0]])
    y = np.array([2.0, 4.0, 6.0, 8.0])
    model = LinearRegression().fit(x, y)
    prediction = float(model.predict([[7.0]])[0])
    np.testing.assert_allclose(prediction, 14.0)
    print(json.dumps({
        "revenue": {key: int(pandas_totals[key]) for key in sorted(expected)},
        "mean_amount": float(amounts.mean()),
        "centered": centered.tolist(),
        "toy_prediction": round(prediction, 6),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
