# Python: data, analytics, and visualization

[README](../../README.en.md) · [VI](python-data.vi.md) · [EN](python-data.en.md)

Examples illustrate API shape and require matching dependencies in a separate environment. They are not all executed in CI. Input files, model weights, providers/keys/services, and hardware are called out where required; do not install every library together. The offline lab at the end of the data guide is execution-checked.

Categories were explored using [best-of-ml-python](https://github.com/lukasmasuch/best-of-ml-python) and [awesome-python](https://github.com/vinta/awesome-python), then checked against official docs per entry. Descriptions/assessments/examples are original; rankings and performance claims based on stars are not carried over.

## Numerical arrays and tables

### NumPy

**Purpose and scenario:** homogeneous N-dimensional arrays, broadcasting, reductions, linear algebra, and random sampling. Scenario: normalize a numeric feature matrix before training. [Official beginner guide](https://numpy.org/doc/stable/user/absolute_beginners.html).

```python
import numpy as np
x = np.array([[10.0, 2.0], [20.0, 4.0], [30.0, 6.0]])
centered = x - x.mean(axis=0)
print(centered)
```

**Expected result and assessment:** each column's mean is subtracted, giving rows `[-10, -2]`, `[0, 0]`, `[10, 2]`. Caveat: arrays are generally in-memory; slicing can return a view whose mutation changes the original. Broadcasting shape mistakes can silently compute an unintended result. For real ML, fit preprocessing on training data only.

### pandas

**Purpose and scenario:** DataFrame/Series, CSV/Parquet I/O, missing-value handling, grouping, joins, dates, and reshaping. Scenario: aggregate transaction revenue per customer. [Official table I/O tutorial](https://pandas.pydata.org/docs/getting_started/intro_tutorials/02_read_write.html), [10 minutes](https://pandas.pydata.org/docs/user_guide/10min.html).

```python
import pandas as pd
orders = pd.DataFrame({"customer": ["An", "An", "Binh"], "amount": [20, 30, 10]})
print(orders.groupby("customer", as_index=False)["amount"].sum())
```

**Expected result and assessment:** An totals 50 and Binh totals 10. Caveat: pandas is mainly an in-memory table tool; avoid loading a full data lake into one DataFrame. Specify dtypes/time zones deliberately and check changed copy/mutation behavior when upgrading major versions. pandas is not a database transaction layer.

### Polars

**Purpose and scenario:** typed columnar DataFrames and lazy query plans with optimizer opportunities. Scenario: scan a large Parquet export, filter paid orders, and aggregate before materializing. [Official lazy API guide](https://docs.pola.rs/user-guide/concepts/lazy-api/).

```python
import polars as pl
result = (
    pl.scan_parquet("orders.parquet")
    .filter(pl.col("status") == "paid")
    .group_by("customer")
    .agg(pl.col("amount").sum())
    .collect()
)
```

**Expected result and assessment:** a small aggregated DataFrame; `scan_parquet` builds a plan and `collect` executes it. Caveat: expressions and lazy execution differ from pandas; Python row UDFs can lose optimization opportunities. Streaming support depends on the operations and selected engine. Do not claim every Polars workload is faster than pandas.

### PyArrow

**Purpose and scenario:** Arrow columnar arrays/tables, schema-aware interchange, IPC, Parquet, and datasets. Scenario: publish typed analytical data that multiple engines can read. [Official Parquet guide](https://arrow.apache.org/docs/python/parquet.html).

```python
import pyarrow as pa
import pyarrow.parquet as pq
table = pa.table({"customer": ["An", "Binh"], "amount": [50, 10]})
pq.write_table(table, "daily.parquet", compression="zstd")
print(pq.read_table("daily.parquet", columns=["amount"]).to_pydict())
```

**Expected result and assessment:** `{"amount": [50, 10]}`. Caveat: Arrow is an in-memory format and interoperability toolkit; Parquet is a disk format. Timestamp resolution, nullable types, codecs, and reader compatibility require attention. Zero-copy is possible for some conversions, not a guarantee for every bridge.

### DuckDB

**Purpose and scenario:** run analytical SQL over local files and DataFrames without running a separate database server. Scenario: summarize a Parquet export using SQL familiar to backend developers. [Official Python API](https://duckdb.org/docs/current/clients/python/overview).

```python
import duckdb
with duckdb.connect() as con:
    rows = con.sql("""
        SELECT customer, SUM(amount) AS revenue
        FROM read_parquet('orders.parquet')
        GROUP BY customer
    """).fetchall()
print(rows)
```

**Expected result and assessment:** customer/revenue tuples after the relation is fetched. Caveat: avoid a shared module-global connection in concurrent application code. Embedded analytics is a different role from a multi-client operational PostgreSQL server. Parameterize user-supplied values; table/file identifiers need deliberate handling.

### Dask

**Purpose and scenario:** coordinate partitioned arrays/DataFrames and task graphs locally or across workers. Scenario: aggregate many Parquet partitions when one pandas table is impractical. [Official DataFrame guide](https://docs.dask.org/en/stable/dataframe.html).

```python
import dask.dataframe as dd
orders = dd.read_parquet("orders/*.parquet")
totals = orders.groupby("customer")["amount"].sum()
print(totals.compute())
```

**Expected result and assessment:** building `totals` is lazy; `compute` runs tasks and collects the result. Caveat: scheduler overhead is unnecessary for tiny data. Distributed joins/shuffles can dominate time and network cost. The final computed result must fit where it is collected. Do not copy obsolete `sklearn.cross_validation` shown in some historical official examples; use `sklearn.model_selection`.

### PySpark

**Purpose and scenario:** distributed DataFrame/SQL jobs and access to Spark's streaming and ML ecosystem. Scenario: transform a warehouse export on an established Spark cluster. [Official DataFrame quickstart](https://spark.apache.org/docs/latest/api/python/getting_started/quickstart_df.html).

```python
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName("revenue").getOrCreate()
orders = spark.read.parquet("orders/")
orders.groupBy("customer").agg(F.sum("amount").alias("revenue")).show()
spark.stop()
```

**Expected result and assessment:** Spark plans transformations and executes an action at `show`. Caveat: driver/executor topology, JVM/Spark requirements, serialization, partitioning, and shuffles matter. `collect()` moves all rows to the driver and can exhaust its memory. A small local script does not demonstrate cluster performance.

### SciPy

**Purpose and scenario:** numerical optimization, statistics, signal processing, integration, sparse structures, and scientific linear algebra on top of NumPy. Scenario: fit a physical or business objective without implementing a solver. [Official optimization tutorial](https://docs.scipy.org/doc/scipy/tutorial/optimize.html).

```python
from scipy.optimize import minimize
result = minimize(lambda x: (x[0] - 3) ** 2, x0=[0.0])
print(result.success, result.x)
```

**Expected result and assessment:** a successful minimization near `x = 3`, subject to numerical tolerances. Caveat: solver choice, constraints, scaling, and convergence diagnostics matter. A numerical optimizer's returned parameters do not establish that a statistical model is scientifically valid.

### Pandera

**Purpose and scenario:** validate tabular dtypes, nullability, ranges, uniqueness, and table-level assumptions. Scenario: reject invalid feature batches before training. [Official DataFrame schemas](https://pandera.readthedocs.io/en/stable/dataframe_schemas.html).

```python
import pandas as pd
import pandera.pandas as pa
schema = pa.DataFrameSchema({"amount": pa.Column(int, pa.Check.ge(0))})
schema.validate(pd.DataFrame({"amount": [10, 20]}))
```

**Expected result and assessment:** returns a validated table; a negative value violates the contract. Caveat: choose the backend-specific import and matching package extras. Validation is not a cleaning algorithm or a proof of unbiased data. Coercion can change types; nullable and unexpected-column policies should be explicit.

## Exploration and charts

### Matplotlib

**Purpose and scenario:** explicit figure/axes APIs for publication or report charts. Scenario: export an experiment's loss curve. [Official quickstart](https://matplotlib.org/stable/users/explain/quick_start.html).

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [0.8, 0.5, 0.3], marker="o")
ax.set(xlabel="Epoch", ylabel="Validation loss")
fig.savefig("loss.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

**Expected result and assessment:** a PNG with a labeled decreasing loss curve. Caveat: fonts, layout, axes choices, and plotting backends affect exported results. Close figures in repeated jobs to avoid retaining memory. This plots precomputed values; it does not train a model.

### Seaborn

**Purpose and scenario:** high-level, dataset-aware plotting over Matplotlib, including categories, distributions, and relational plots. Scenario: inspect order amount distributions per sales channel. [Official introduction](https://seaborn.pydata.org/tutorial/introduction.html).

```python
import seaborn as sns
import matplotlib.pyplot as plt
ax = sns.boxplot(x=["web", "web", "store", "store"], y=[10, 30, 15, 20])
ax.set(xlabel="Channel", ylabel="Order amount")
plt.show()
```

**Expected result and assessment:** separate channel boxplots. Caveat: a chart may compute estimates or uncertainty internally; understand each plot's aggregation. Tiny samples are an API demonstration, not a meaningful distribution comparison. Network-downloaded demo datasets are optional, so use in-memory data for reproducible examples.

### Plotly

**Purpose and scenario:** figures with hover, zoom, selection, and browser rendering; Plotly Express offers compact table-driven construction. Scenario: share revenue exploration as an HTML file. [Official figure guide](https://plotly.com/python/creating-and-updating-figures/).

```python
import plotly.express as px
fig = px.bar(x=["An", "Binh"], y=[50, 10], labels={"x": "Customer", "y": "Revenue"})
fig.write_html("revenue.html", include_plotlyjs=True)
```

**Expected result and assessment:** an HTML figure with hover and interactive controls. Caveat: embedding the JavaScript bundle increases file size; large point counts need an appropriate renderer or aggregation. Static image export requires additional tooling and differs from HTML export.

## Compose stacks by data size and access pattern

| Need | Stack | Reason / limit |
| --- | --- | --- |
| Notebooks, small CSVs, familiar table logic | pandas + Pandera + Matplotlib/Seaborn | Easy inspection; tables and copies must fit RAM |
| Local Parquet exports to filter/aggregate | PyArrow + Polars lazy or DuckDB | Columnar files and pushdown; choose expressions or SQL by team |
| Interactive dashboards | Aggregated table + Plotly | Send only needed points to the browser rather than every row |
| Oversized partitions or an existing cluster | Dask or PySpark | Distributed execution adds scheduler/shuffle/cluster complexity |

Python often coordinates native kernels or distributed engines. Do not extrapolate a tiny Python loop to NumPy/Polars/Spark, or assume native execution guarantees low memory. Measure read, parse, query, transfer, and materialization separately.

## Offline lab: one table, three engines, one model

[main.py](../../examples/data/python/main.py) creates orders in memory, writes Parquet, and checks equal revenue totals through pandas, Polars, and DuckDB; NumPy centers amounts and scikit-learn fits a toy linear relationship. No cloud, keys, GPU, or model downloads. This checks APIs/data flow, not speed or model quality.

```sh
python3 -m venv .venv-data
.venv-data/bin/python -m pip install -r examples/data/python/requirements.txt
.venv-data/bin/python examples/data/python/main.py
```

Output JSON includes revenues `An=50`, `Binh=10`, `Chi=40`, mean `25.0`, and toy prediction `14.0`. Parquet files are temporary and removed on completion. CI executes the lab in a separate job; server requirements are not mixed with the data stack.

## Practical exercises

Add missing/negative amounts, explicitly choose reject/drop/fill, and check totals. Scan only two columns and inspect the plan before collecting. For ML, split before fitting the scaler and preserve feature order/dtypes with the model. See [AI/ML](python-ai-ml.en.md) and [backend](python-backend.en.md) for application integration.
