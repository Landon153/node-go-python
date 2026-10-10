# Python: data, analytics và visualization

[README](../../README.vi.md) · [VI](python-data.vi.md) · [EN](python-data.en.md)

Các ví dụ là minh họa API, cần cài đúng dependency trong môi trường riêng. Chúng chưa được chạy toàn bộ trong CI. File đầu vào, model weights, provider/key/service và hardware được nêu khi cần; không cài tất cả thư viện cùng lúc. Lab offline cuối guide data là phần được kiểm tra thực thi.

Tham khảo nhóm công cụ từ [best-of-ml-python](https://github.com/lukasmasuch/best-of-ml-python) và [awesome-python](https://github.com/vinta/awesome-python), rồi đối chiếu docs official ở mỗi mục. Các mô tả/đánh giá/ví dụ được viết riêng; không sao chép ranking hoặc kết luận performance từ stars.

## Mảng số và bảng

### NumPy

**Công dụng và tình huống:** NumPy tạo mảng số nhiều chiều, broadcasting, reduction và đại số tuyến tính. Dùng để chuẩn hóa matrix đặc trưng trước training. [Official beginner guide](https://numpy.org/doc/stable/user/absolute_beginners.html)

```python
import numpy as np
x = np.array([[10.0, 2.0], [20.0, 4.0], [30.0, 6.0]])
centered = x - x.mean(axis=0)
print(centered)
```

**Kết quả:** Trừ trung bình từng cột, nhận các hàng `[-10,-2]`, `[0,0]`, `[10,2]`.

**Đánh giá:** Mảng thường nằm trong RAM; slice có thể là view. Chú ý shape và chỉ fit preprocessing trên training data.

### pandas

**Công dụng và tình huống:** pandas xử lý bảng có nhãn: CSV/Parquet, missing values, group/join, ngày giờ và reshape. Dùng tổng hợp doanh thu theo khách hàng. [Official table I/O tutorial](https://pandas.pydata.org/docs/getting_started/intro_tutorials/02_read_write.html) [10 minutes](https://pandas.pydata.org/docs/user_guide/10min.html)

```python
import pandas as pd
orders = pd.DataFrame({"customer": ["An", "An", "Binh"], "amount": [20, 30, 10]})
print(orders.groupby("customer", as_index=False)["amount"].sum())
```

**Kết quả:** An có tổng 50, Binh có tổng 10.

**Đánh giá:** Phù hợp bảng trong RAM; dtype, timezone và copy behavior cần kiểm tra khi nâng version. Không thay transaction DB.

### Polars

**Công dụng và tình huống:** Polars xử lý bảng theo expression và lazy query plan. Dùng scan Parquet, lọc đơn paid rồi aggregate trước khi materialize. [Official lazy API guide](https://docs.pola.rs/user-guide/concepts/lazy-api/)

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

**Kết quả:** `scan_parquet` tạo plan; `collect` thực thi và trả DataFrame tổng theo khách.

**Đánh giá:** Cần file `orders.parquet` có customer/status/amount. Python UDF từng hàng làm mất cơ hội tối ưu; streaming tùy operation/engine, không có kết luận luôn nhanh hơn pandas.

### PyArrow

**Công dụng và tình huống:** PyArrow cung cấp Arrow arrays/tables, schema, IPC, Parquet và dataset I/O. Dùng trao đổi bảng typed giữa các engine. [Official Parquet guide](https://arrow.apache.org/docs/python/parquet.html)

```python
import pyarrow as pa
import pyarrow.parquet as pq
table = pa.table({"customer": ["An", "Binh"], "amount": [50, 10]})
pq.write_table(table, "daily.parquet", compression="zstd")
print(pq.read_table("daily.parquet", columns=["amount"]).to_pydict())
```

**Kết quả:** Ghi file Parquet rồi chỉ đọc cột amount, nhận `{"amount":[50,10]}`.

**Đánh giá:** Arrow là format trong memory, Parquet là format trên đĩa. Timestamp/nullability/codec cần tương thích; zero-copy không bảo đảm cho mọi conversion.

### DuckDB

**Công dụng và tình huống:** DuckDB chạy SQL analytics nhúng trên file/DataFrame mà không cần DB server riêng. Dùng tổng hợp export Parquet bằng SQL. [Official Python API](https://duckdb.org/docs/current/clients/python/overview)

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

**Kết quả:** Fetch trả tuples customer/revenue từ file orders.parquet có customer/amount.

**Đánh giá:** Không dùng một global connection chung cho app đồng thời. Vai trò analytics nhúng khác PostgreSQL operational; parameterize giá trị do user gửi.

### Dask

**Công dụng và tình huống:** Dask chia DataFrame/array và task graph thành partitions, chạy local hoặc nhiều worker. Dùng khi bảng pandas đơn không phù hợp. [Official DataFrame guide](https://docs.dask.org/en/stable/dataframe.html)

```python
import dask.dataframe as dd
orders = dd.read_parquet("orders/*.parquet")
totals = orders.groupby("customer")["amount"].sum()
print(totals.compute())
```

**Kết quả:** Groupby là lazy; `compute` chạy task và thu kết quả. Cần các file orders/*.parquet.

**Đánh giá:** Tiny data không cần scheduler. Join/shuffle tốn network; kết quả cuối phải vừa memory nơi thu về.

### PySpark

**Công dụng và tình huống:** PySpark điều khiển DataFrame/SQL, streaming và ML trong Spark. Dùng khi đã có Spark cluster cho pipeline warehouse. [Official DataFrame quickstart](https://spark.apache.org/docs/latest/api/python/getting_started/quickstart_df.html)

```python
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName("revenue").getOrCreate()
orders = spark.read.parquet("orders/")
orders.groupBy("customer").agg(F.sum("amount").alias("revenue")).show()
spark.stop()
```

**Kết quả:** Spark lập plan; `show` kích hoạt action và in bảng doanh thu. Cần Spark/JVM tương thích và file Parquet.

**Đánh giá:** Driver/executor, partition và shuffle quyết định chi phí. `collect()` kéo toàn bộ về driver có thể hết RAM; demo local không chứng minh performance cluster.

### SciPy

**Công dụng và tình huống:** SciPy có optimization, thống kê, signal processing, sparse matrix và scientific linear algebra trên NumPy. Dùng solver thay vì tự viết thuật toán tối ưu. [Official optimization tutorial](https://docs.scipy.org/doc/scipy/tutorial/optimize.html)

```python
from scipy.optimize import minimize
result = minimize(lambda x: (x[0] - 3) ** 2, x0=[0.0])
print(result.success, result.x)
```

**Kết quả:** Minimizer tìm x gần 3, tùy tolerance và convergence.

**Đánh giá:** Chọn solver, scale, constraint và kiểm tra diagnostics. Tham số tối ưu không tự chứng minh model có ý nghĩa thống kê.

### Pandera

**Công dụng và tình huống:** Pandera validate schema/dtype/null/range/uniqueness của DataFrame. Dùng chặn batch đặc trưng không hợp lệ trước training. [Official DataFrame schemas](https://pandera.readthedocs.io/en/stable/dataframe_schemas.html)

```python
import pandas as pd
import pandera.pandas as pa
schema = pa.DataFrameSchema({"amount": pa.Column(int, pa.Check.ge(0))})
schema.validate(pd.DataFrame({"amount": [10, 20]}))
```

**Kết quả:** Bảng amount 10,20 hợp lệ; giá trị âm vi phạm contract.

**Đánh giá:** Dùng import/extras đúng backend. Validation không làm sạch hay chứng minh data không bias; quyết định rõ coerce/null/extra columns.

## Khám phá và biểu đồ

### Matplotlib

**Công dụng và tình huống:** Matplotlib cho figure/axes chi tiết và export chart báo cáo. Dùng vẽ loss theo epoch từ metric đã có. [Official quickstart](https://matplotlib.org/stable/users/explain/quick_start.html)

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [0.8, 0.5, 0.3], marker="o")
ax.set(xlabel="Epoch", ylabel="Validation loss")
fig.savefig("loss.png", dpi=160, bbox_inches="tight")
plt.close(fig)
```

**Kết quả:** Tạo PNG loss.png có trục và curve; không huấn luyện model.

**Đánh giá:** Font, backend và layout ảnh hưởng export. Đóng figure trong job lặp để tránh giữ memory.

### Seaborn

**Công dụng và tình huống:** Seaborn vẽ chart thống kê theo dataset trên Matplotlib: phân phối, category và quan hệ. Dùng khám phá amount theo channel. [Official introduction](https://seaborn.pydata.org/tutorial/introduction.html)

```python
import seaborn as sns
import matplotlib.pyplot as plt
ax = sns.boxplot(x=["web", "web", "store", "store"], y=[10, 30, 15, 20])
ax.set(xlabel="Channel", ylabel="Order amount")
plt.show()
```

**Kết quả:** Tạo boxplot cho web/store; bốn điểm chỉ minh họa API.

**Đánh giá:** Hiểu aggregation/estimate của chart; sample nhỏ không đủ so sánh phân phối. Dùng data trong memory thay dataset tải mạng khi cần reproducibility.

### Plotly

**Công dụng và tình huống:** Plotly tạo figure tương tác có hover/zoom/selection và export HTML. Dùng chia sẻ khám phá doanh thu. [Official figure guide](https://plotly.com/python/creating-and-updating-figures/)

```python
import plotly.express as px
fig = px.bar(x=["An", "Binh"], y=[50, 10], labels={"x": "Customer", "y": "Revenue"})
fig.write_html("revenue.html", include_plotlyjs=True)
```

**Kết quả:** Tạo revenue.html với bar chart và JavaScript được embed.

**Đánh giá:** Bundle làm file lớn; nhiều điểm cần aggregate/renderer phù hợp. Export ảnh tĩnh cần tooling riêng.

## Ghép stack theo kích thước và cách truy cập dữ liệu

| Nhu cầu | Stack | Vì sao / giới hạn |
| --- | --- | --- |
| Notebook, CSV nhỏ, nghiệp vụ bảng quen thuộc | pandas + Pandera + Matplotlib/Seaborn | Dễ inspect; giữ bảng và bản sao vừa RAM |
| Export Parquet local cần filter/aggregate | PyArrow + Polars lazy hoặc DuckDB | Columnar file và pushdown; chọn expression hoặc SQL theo team |
| Dashboard tương tác | Bảng đã aggregate + Plotly | Đưa ít điểm cần thiết lên browser, tránh gửi mọi row |
| Partition quá lớn hoặc cluster đã có | Dask hoặc PySpark | Đổi thêm scheduler/shuffle/cluster complexity lấy execution phân tán |

Python thường điều khiển native kernels hoặc engine phân tán. Không suy luận tốc độ từ vòng lặp Python nhỏ sang phép toán NumPy/Polars/Spark; cũng không giả định native code tự bảo đảm memory thấp. Đo read, parse, query, transfer và materialization riêng.

## Lab offline: một bảng, ba engine, một model

[main.py](../../examples/data/python/main.py) tạo bảng đơn hàng trong RAM, ghi Parquet, kiểm tra tổng doanh thu bằng pandas, Polars và DuckDB giống nhau; NumPy chuẩn hóa giá trị; scikit-learn fit một quan hệ tuyến tính toy. Không cần cloud, key, GPU hoặc tải model. Lab chỉ kiểm tra API/data flow, không so sánh tốc độ hay model quality.

```sh
python3 -m venv .venv-data
.venv-data/bin/python -m pip install -r examples/data/python/requirements.txt
.venv-data/bin/python examples/data/python/main.py
```

Kết quả JSON có doanh thu `An=50`, `Binh=10`, `Chi=40`, mean `25.0` và dự đoán toy `14.0`. Các file Parquet được tạo trong thư mục tạm và xóa khi kết thúc. CI chạy lab trong job riêng; requirements của server không bị trộn với data stack.

## Bài tập thực tế

Thêm missing amount hoặc amount âm, quyết định rõ reject/drop/fill rồi kiểm tra tổng. Thử scan file chỉ lấy hai cột; xem query plan trước collect. Khi chuyển sang ML, split trước fit scaler, lưu feature order/dtype cùng model. Xem [AI/ML](python-ai-ml.vi.md) và [backend](python-backend.vi.md) để đưa bảng/model vào ứng dụng.
