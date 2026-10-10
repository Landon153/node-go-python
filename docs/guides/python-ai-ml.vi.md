# Python: AI, ML, inference và MLOps

[README](../../README.vi.md) · [VI](python-ai-ml.vi.md) · [EN](python-ai-ml.en.md)

Các ví dụ là minh họa API, cần cài đúng dependency trong môi trường riêng. Chúng chưa được chạy toàn bộ trong CI. File đầu vào, model weights, provider/key/service và hardware được nêu khi cần; không cài tất cả thư viện cùng lúc. Lab offline cuối guide data là phần được kiểm tra thực thi.

Tham khảo nhóm công cụ từ [best-of-ml-python](https://github.com/lukasmasuch/best-of-ml-python) và [awesome-python](https://github.com/vinta/awesome-python), rồi đối chiếu docs official ở mỗi mục. Các mô tả/đánh giá/ví dụ được viết riêng; không sao chép ranking hoặc kết luận performance từ stars.

## Phân biệt training, inference và application

Training học tham số từ data; inference chạy model đã học; application thêm auth, retrieval, tool và UI. Không cần PyTorch, TensorFlow, Keras và JAX cùng lúc: chọn nền tảng theo model/team/hardware. API async không tự offload model inference; nhiều process có thể nhân bản weights và pool.

### Data chung cho ví dụ scikit-learn, XGBoost và LightGBM

Iris là dataset nhỏ có sẵn, không cần tải model/API key. Chạy đoạn sau trước các ví dụ đó; CatBoost có fixture riêng. Metric toy không chứng minh quality ngoài bài tập.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

## ML truyền thống

### scikit-learn

**Công dụng và tình huống:** scikit-learn có estimator, preprocessing, pipeline, split/CV/metric/search. Dùng làm baseline classification cho bảng đặc trưng. [Official getting started](https://scikit-learn.org/stable/getting_started.html)

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=300))
model.fit(X_train, y_train)
print(model.score(X_test, y_test))
```

**Kết quả:** Fit scaler + logistic regression trên training split, trả accuracy trên held-out test.

**Đánh giá:** Fit preprocessing trên toàn data gây leakage; dùng pipeline. Split theo thời gian/group khi cần; accuracy không đủ cho class lệch.

### XGBoost

**Công dụng và tình huống:** XGBoost là gradient boosting cho regression/classification/ranking, có sklearn interface. Dùng so sánh cây boosting trên dữ liệu có cấu trúc. [Official Python introduction](https://xgboost.readthedocs.io/en/stable/python/python_intro.html)

```python
from xgboost import XGBClassifier
model = XGBClassifier(n_estimators=30, max_depth=3, tree_method="hist", random_state=42)
model.fit(X_train, y_train)
print(model.predict(X_test[:3]))
model.save_model("iris.ubj")
```

**Kết quả:** Predict ba class IDs và lưu artifact iris.ubj.

**Đánh giá:** Early stopping cần validation set/API đúng version. GPU phụ thuộc build/hardware; không mặc định tốt nhất mọi loại data.

### LightGBM

**Công dụng và tình huống:** LightGBM là boosted trees với histogram và leaf-wise growth. Dùng tabular model có kiểm soát leaves/depth. [Official Python introduction](https://lightgbm.readthedocs.io/en/stable/Python-Intro.html)

```python
from lightgbm import LGBMClassifier
model = LGBMClassifier(n_estimators=30, num_leaves=7, random_state=42, verbosity=-1)
model.fit(X_train, y_train)
print(model.predict_proba(X_test[:2]))
```

**Kết quả:** Predict probability từng class cho hai input.

**Đánh giá:** Leaf-wise có thể overfit; constrain và validate. Category cần dtype/encoding đúng; tốc độ tùy workload.

### CatBoost

**Công dụng và tình huống:** CatBoost có xử lý categorical features tích hợp cho boosted trees. Dùng bảng chứa country/product strings. [Official usage examples](https://catboost.ai/docs/en/concepts/python-usages-examples)

```python
from catboost import CatBoostClassifier
rows = [["VN", 10], ["US", 30], ["VN", 12], ["US", 28]]
model = CatBoostClassifier(iterations=20, depth=2, verbose=False, random_seed=42)
model.fit(rows, [0, 1, 0, 1], cat_features=[0])
print(model.predict([["VN", 11]]))
```

**Kết quả:** Class prediction từ feature đầu là category; bốn hàng chỉ minh họa cú pháp.

**Đánh giá:** Vẫn cần split, missing policy, drift và leakage checks. Native categories không loại bỏ việc đánh giá model.

## Deep learning và gradient

### PyTorch

**Công dụng và tình huống:** PyTorch cung cấp tensor, autograd, modules, optimizer, data loading và accelerator execution. Dùng custom training loop hoặc fine-tune network. [Official quickstart](https://docs.pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html)

```python
import torch
model = torch.nn.Linear(2, 1)
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
x = torch.tensor([[1.0, 2.0]])
y = torch.tensor([[3.0]])
optimizer.zero_grad()
loss = torch.nn.functional.mse_loss(model(x), y)
loss.backward()
optimizer.step()
```

**Kết quả:** Thực hiện một gradient update của Linear model; chưa tạo predictor đã train.

**Đánh giá:** Device/dtype phải khớp. `eval()` đổi layer behavior; `inference_mode`/`no_grad` đổi gradient tracking. Chọn wheel và GPU memory theo hardware.

### TensorFlow

**Công dụng và tình huống:** TensorFlow cung cấp tensor runtime, gradient, tf.data, training và export. Dùng pipeline hiện có trong hệ TensorFlow. [Official beginner quickstart](https://www.tensorflow.org/tutorials/quickstart/beginner)

```python
import tensorflow as tf
x = tf.Variable(3.0)
with tf.GradientTape() as tape:
    loss = x ** 2
print(tape.gradient(loss, x).numpy())
```

**Kết quả:** Gradient của x² tại 3 là 6.0.

**Đánh giá:** Eager và traced graph khác nhau; Python side effect trong tf.function cần chú ý. OS/build/accelerator và tf.keras/Keras phải tương thích.

### Keras

**Công dụng và tình huống:** Keras có layers/model/fit/evaluate/callback/save ở mức cao và nhiều backend. Dùng dựng neural model nhanh với định nghĩa rõ. [Official Sequential guide](https://keras.io/guides/sequential_model/)

```python
import os
os.environ["KERAS_BACKEND"] = "tensorflow"  # Set before importing keras.
import keras
model = keras.Sequential([
    keras.Input(shape=(4,)),
    keras.layers.Dense(8, activation="relu"),
    keras.layers.Dense(3, activation="softmax"),
])
model.summary()
```

**Kết quả:** Summary mô tả network 4 input, hidden 8, output 3; chưa training.

**Đánh giá:** Chọn backend trước import và cài backend package. Custom layers nên dùng backend-neutral ops; kiểm tra saved-format compatibility.

### JAX

**Công dụng và tình huống:** JAX kết hợp array với grad/jit/vmap cho chương trình số có thể vi phân. Dùng optimization khoa học hoặc nghiên cứu. [Official beginner guide](https://docs.jax.dev/en/latest/beginner_guide.html)

```python
import jax
import jax.numpy as jnp
def squared_norm(x):
    return jnp.sum(x ** 2)
gradient = jax.jit(jax.grad(squared_norm))
print(gradient(jnp.array([2.0, 3.0])))
```

**Kết quả:** Gradient là `[4,6]`; lần đầu có tracing/compilation.

**Đánh giá:** Thiết kế functional, chú ý mutation/control flow/shape và PRNG rõ ràng. JAX chưa phải stack serving/tracking đầy đủ.

## Model, dataset và embeddings

### Transformers

**Công dụng và tình huống:** Transformers cung cấp architecture, tokenizer/processor, pretrained loading, pipeline/generation/Trainer. Dùng thử model sentiment trước khi cân nhắc fine-tune. [Official quickstart](https://huggingface.co/docs/transformers/quicktour)

```python
from transformers import pipeline
classifier = pipeline(
    "text-classification",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
)
print(classifier("The delivery was excellent."))
```

**Kết quả:** Trả label/score cho câu tiếng Anh; lần đầu tải weights qua mạng.

**Đánh giá:** Kiểm tra language/task/license/revision/RAM/device. Score không phải bảo đảm confidence đúng mọi domain; API Trainer theo version.

### Datasets

**Công dụng và tình huống:** Datasets load/version split, map preprocessing, Arrow-backed storage và streaming. Dùng tạo corpus local JSONL phục vụ training. [Official quickstart](https://huggingface.co/docs/datasets/quickstart)

```python
from datasets import Dataset
records = Dataset.from_dict({"text": ["hello", "goodbye"], "label": [0, 1]})
records = records.map(lambda row: {"length": len(row["text"])})
print(records[0])
```

**Kết quả:** Record đầu chứa text, label và length mới.

**Đánh giá:** Dataset random-access khác IterableDataset streaming. Cache dùng disk; modality extras và license/contamination cần kiểm tra.

### Tokenizers

**Công dụng và tình huống:** Tokenizers train/chạy normalization, subword, padding/truncation, offsets và serialize tokenizer. Dùng xem token IDs đi vào model. [Official quicktour](https://huggingface.co/docs/tokenizers/quicktour)

```python
from tokenizers import Tokenizer
tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
encoded = tokenizer.encode("Ship the order today.")
print(encoded.tokens, encoded.ids)
```

**Kết quả:** In token strings và IDs, gồm special tokens của tokenizer; cần tải tokenizer.

**Đánh giá:** Vocabulary/normalization phải khớp checkpoint. Token ID không phải embedding; lưu revision để tái tạo input.

### Accelerate

**Công dụng và tình huống:** Accelerate hỗ trợ device, distributed execution và mixed precision cho training PyTorch. Dùng chuyển loop từ CPU sang accelerator. [Official quicktour](https://huggingface.co/docs/accelerate/quicktour)

```python
import torch
from accelerate import Accelerator
accelerator = Accelerator()
model = torch.nn.Linear(2, 1)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
model, optimizer = accelerator.prepare(model, optimizer)
x = torch.ones((1, 2), device=accelerator.device)
loss = model(x).square().mean()
accelerator.backward(loss)
optimizer.step()
```

**Kết quả:** Một update có device handling; chưa là training pipeline hoàn chỉnh.

**Đánh giá:** Loop thật cần chuẩn bị DataLoader, zero gradients, gather metric và launcher đúng. Công cụ không chọn objective/data tốt thay bạn.

### PEFT

**Công dụng và tình huống:** PEFT dùng adapter như LoRA để fine-tune ít tham số hơn base model. Dùng thích nghi pretrained causal model với task hẹp. [Official quicktour](https://huggingface.co/docs/peft/quicktour)

```python
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM
base = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B")
config = LoraConfig(
    task_type=TaskType.CAUSAL_LM, target_modules=["q_proj"], r=8, lora_alpha=16
)
model = get_peft_model(base, config)
model.print_trainable_parameters()
```

**Kết quả:** Tạo trainable adapter và in số tham số; chưa fine-tune. Cần tải base checkpoint.

**Đánh giá:** Module target phụ thuộc architecture. Vẫn phải load/chạy base model; LoRA không xóa chi phí memory/compute. Kiểm tra quantization/merge riêng.

### Sentence Transformers

**Công dụng và tình huống:** Sentence Transformers tạo semantic text embeddings; cross-encoder riêng làm reranking. Dùng duplicate detection và retrieval trong RAG. [Official quickstart](https://www.sbert.net/docs/quickstart.html)

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
vectors = model.encode(["Shipping policy", "How deliveries work"])
print(vectors.shape)
print(model.similarity(vectors, vectors))
```

**Kết quả:** Checkpoint ví dụ trả shape (2,384) và similarity matrix, cần tải model.

**Đánh giá:** Model tiếng Anh không tự phù hợp tài liệu Việt. Index/query cần embedding contract có version tương thích; model asymmetric có thể dùng prompt/encode_query và encode_document khác nhau; similarity không chứng minh câu trả lời đúng.

## NLP, ảnh, âm thanh và time series

### spaCy

**Công dụng và tình huống:** spaCy có tokenizer và pipeline trained cho POS/dependency/entities. Dùng trích tên tổ chức để phân loại tài liệu. [Official spaCy 101](https://spacy.io/usage/spacy-101)

```python
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("Acme opened an office in London.")
print([(entity.text, entity.label_) for entity in doc.ents])
```

**Kết quả:** Trả entity span/label do English model dự đoán, output có thể đổi theo model.

**Đánh giá:** Cài pipeline riêng: `python -m spacy download en_core_web_sm`. `spacy.blank` không tự có trained NER; đánh giá language/domain.

### OpenCV

**Công dụng và tình huống:** OpenCV xử lý image/video: I/O, color, filter, threshold, geometry. Dùng chuẩn bị ảnh receipt trước OCR. [Official Python tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html) [thresholding tutorial](https://docs.opencv.org/4.13.0/d7/d4d/tutorial_py_thresholding.html)

```python
import cv2
image = cv2.imread("receipt.png", cv2.IMREAD_GRAYSCALE)
if image is None:
    raise FileNotFoundError("receipt.png")
_, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
cv2.imwrite("receipt-binary.png", binary)
```

**Kết quả:** Đọc receipt.png grayscale, ghi receipt-binary.png; không nhận dạng chữ.

**Đánh giá:** Cần file ảnh; color thường BGR. Chọn một wheel variant đúng headless/GUI; preprocessing khác OCR/detector.

### librosa

**Công dụng và tình huống:** librosa xử lý audio, spectrogram/MFCC/pitch/rhythm. Dùng biến audio thành features cho classifier riêng. [Official MFCC API](https://librosa.org/doc/0.11.0/generated/librosa.feature.mfcc.html)

```python
import librosa
waveform, sample_rate = librosa.load("clip.wav", sr=16000)
mfcc = librosa.feature.mfcc(y=waveform, sr=sample_rate, n_mfcc=13)
print(mfcc.shape)
```

**Kết quả:** Clip WAV được resample 16 kHz, tạo MFCC shape (13,time_frames).

**Đánh giá:** Cần file và codec support. Channel/resampling/hop/normalization ảnh hưởng output; không phải speech-to-text. Nguồn API version 0.11.0.

### statsmodels

**Công dụng và tình huống:** statsmodels cung cấp statistical models/tests/diagnostics và time series như ARIMA/SARIMAX. Dùng baseline dự báo demand có giải thích. [Official forecasting notebook](https://www.statsmodels.org/stable/examples/notebooks/generated/statespace_forecasting.html) [ARIMA API](https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html)

```python
from statsmodels.tsa.arima.model import ARIMA
series = [10, 12, 11, 14, 13, 15, 14, 16, 15, 18, 17, 19]
fitted = ARIMA(series, order=(1, 0, 0)).fit()
print(fitted.forecast(steps=3))
```

**Kết quả:** Fit chuỗi toy 12 điểm rồi forecast 3 giá trị.

**Đánh giá:** Demo không chứng minh quality. Validate theo thời gian, xem seasonality/stationarity/residual và convergence; interval phụ thuộc assumptions.

## RAG, agent và model serving

### LangChain

**Công dụng và tình huống:** LangChain kết nối model/provider/tools và tạo agent. Dùng cho model tra trạng thái đơn hàng qua tool read-only. [Official quickstart](https://docs.langchain.com/oss/python/langchain/quickstart)

```python
import os
from langchain.agents import create_agent
def order_status(order_id: str) -> str:
    """Return the status of the example order."""
    return "shipped" if order_id == "A1" else "unknown"
agent = create_agent(model=os.environ["LANGCHAIN_MODEL"], tools=[order_status])
answer = agent.invoke({"messages": [{"role": "user", "content": "Where is order A1?"}]})
```

**Kết quả:** Agent trả message state; model đã cấu hình có thể gọi tool order_status.

**Đánh giá:** Cần provider integration/key hoặc local model. Tool ghi phải có authorization, giới hạn và failure handling; framework không train model.

### LangGraph

**Công dụng và tình huống:** LangGraph định nghĩa nodes/edges/state/checkpoint/interrupt cho workflow agent có state. Dùng làm bước retrieve/draft/approve rõ ràng. [Official overview](https://docs.langchain.com/oss/python/langgraph/overview)

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
class State(TypedDict):
    status: str
graph = StateGraph(State)
graph.add_node("validate", lambda state: {"status": "validated"})
graph.add_edge(START, "validate")
graph.add_edge("validate", END)
print(graph.compile().invoke({"status": "new"}))
```

**Kết quả:** Graph không có LLM, đổi status new thành validated.

**Đánh giá:** Compile không tự bật persistence; cần checkpointer khi resume. Replay/retry cần idempotency; có thể dùng không cần LangChain wrappers.

### LlamaIndex

**Công dụng và tình huống:** LlamaIndex làm load/split/index/query và kết nối retrieval store cho RAG. Dùng hỏi tài liệu nội bộ. [Official starter tutorial](https://developers.llamaindex.ai/python/framework/getting_started/starter_example/)

```python
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
response = index.as_query_engine().query("What is the shipping policy?")
print(response)
```

**Kết quả:** Đọc thư mục data, tạo index và query sau khi cấu hình model/embedding.

**Đánh giá:** Mặc định có thể gọi provider từ xa và phát sinh phí. Chọn model/embedding rõ; cần parsing/integration packages, ACL/citations/reindex/eval riêng.

### vLLM

**Công dụng và tình huống:** vLLM là engine/server inference cho pretrained LLM, batching/scheduling/cache phục vụ API. Dùng endpoint model nội bộ. [Official quickstart](https://docs.vllm.ai/en/latest/getting_started/quickstart/)

```bash
vllm serve Qwen/Qwen2.5-1.5B-Instruct --host 127.0.0.1 --port 8000
```

**Kết quả:** Khởi chạy model server sau khi tải weights trên hardware tương thích.

**Đánh giá:** Kiểm tra model/device/RAM/VRAM/template/quantization/install. Serving khác training; throughput tùy batch, token lengths, concurrency và hardware.

### Ollama

**Công dụng và tình huống:** Ollama là model runtime có HTTP API; ollama-python là client. Dùng prototype chat mà không tự viết model loader. [Official Python repository](https://github.com/ollama/ollama-python) [API introduction](https://docs.ollama.com/api/introduction)

```python
import ollama
reply = ollama.chat(
    model="llama3.2",
    messages=[{"role": "user", "content": "Explain an HTTP timeout."}],
)
print(reply.message.content)
```

**Kết quả:** Có response khi runtime chạy và model đã có: `ollama pull llama3.2`.

**Đánh giá:** Python package không phải runtime. Local/cloud khác network/key/cost; không mặc định mọi lời gọi offline. Chọn model theo task/language/hardware.

### ONNX Runtime

**Công dụng và tình huống:** ONNX Runtime chạy graph ONNX đã export qua execution providers. Dùng deploy classifier ngoài framework training. [Official Python guide](https://onnxruntime.ai/docs/get-started/with-python.html)

```python
import numpy as np
import onnxruntime as ort
# Assume an exported Iris classifier expecting [batch, 4] float32 input.
session = ort.InferenceSession("iris.onnx", providers=["CPUExecutionProvider"])
input_name = session.get_inputs()[0].name
outputs = session.run(None, {input_name: np.array([[5.1, 3.5, 1.4, 0.2]], dtype=np.float32)})
print(outputs)
```

**Kết quả:** Chạy artifact iris.onnx với float32 [batch,4], trả outputs theo model.

**Đánh giá:** Artifact phải có; names/shapes/dtype/opset/provider phải khớp. Export cần tooling khác và kiểm tra numerical equivalence; không tự bảo đảm acceleration.

### Hugging Face Evaluate

**Công dụng và tình huống:** Hugging Face Evaluate load metric/comparison/measurement qua API chung. Dùng tính metric task trên held-out data. [Official quick tour](https://huggingface.co/docs/evaluate/a_quick_tour)

```python
import evaluate
metric = evaluate.load("accuracy")
print(metric.compute(predictions=[0, 1, 1], references=[0, 0, 1]))
```

**Kết quả:** Accuracy của ba dự đoán là 2/3; metric module có thể được tải.

**Đánh giá:** Metric có extras; accuracy, overlap, retrieval recall và judge factuality đo khác nhau. RAG cần cả retrieval/answer eval và inspection theo task.

## Tracking, tuning, orchestration và artifact

### MLflow

**Công dụng và tình huống:** MLflow lưu params/metrics/artifacts, experiment và model lifecycle. Dùng liên kết run với data/code/model để so sánh. [Official tracking quickstart](https://mlflow.org/docs/latest/ml/tracking/quickstart/)

```python
import mlflow
mlflow.set_experiment("shipping-baseline")
with mlflow.start_run():
    mlflow.log_param("max_depth", 3)
    mlflow.log_metric("validation_accuracy", 0.91)
```

**Kết quả:** Tạo run có max_depth=3 và accuracy=0.91; số 0.91 là minh họa, không được đo.

**Đánh giá:** Cấu hình tracking URI, DB/artifact store, auth/retention/flavor. Tracking không tự version dataset hay deploy inference đáng tin cậy.

### Weights & Biases

**Công dụng và tình huống:** Weights & Biases lưu run/config/metric/artifact cho nghiên cứu nhóm. Dùng so sánh training curves. [Official SDK repository](https://github.com/wandb/wandb) [initialization API source](https://github.com/wandb/wandb/blob/main/wandb/sdk/wandb_init.py)

```python
import wandb
with wandb.init(project="shipping-baseline", config={"lr": 0.001}, mode="offline") as run:
    run.log({"epoch": 1, "loss": 0.7})
```

**Kết quả:** `mode="offline"` ghi run local; loss 0.7 là minh họa.

**Đánh giá:** Online sync cần key/hosting lựa chọn riêng. Không log secret/customer payload; storage và data handling cần cấu hình.

### Optuna

**Công dụng và tình huống:** Optuna tạo trial/search space/study để tối ưu objective và pruning. Dùng tune depth/learning rate theo validation. [Official first study tutorial](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/001_first.html)

```python
import optuna
def objective(trial):
    x = trial.suggest_float("x", -5.0, 5.0)
    return (x - 3.0) ** 2
study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=30)
print(study.best_params, study.best_value)
```

**Kết quả:** Tìm x gần 3 qua 30 trials, không cam kết chính xác.

**Đánh giá:** Không tune trên test set; giới hạn resource, seed/storage và chọn direction/metric đúng. Toy objective không đo quality ML.

### Prefect

**Công dụng và tình huống:** Prefect điều phối tasks/flows/state/retry/schedule/deploy cho pipeline data. Dùng extract, validate và publish daily features. [Official v3 quickstart](https://docs.prefect.io/v3/get-started/quickstart)

```python
from prefect import flow, task
@task(retries=2)
def total(values: list[int]) -> int:
    return sum(values)
@flow
def daily_summary() -> int:
    return total([10, 20, 30])
if __name__ == "__main__":
    print(daily_summary())
```

**Kết quả:** Flow local trả 60 và có run state.

**Đánh giá:** Decorator không tự schedule/deploy; cần backend/runtime phù hợp. Retry external writes cần idempotency; CPU vẫn cần execution resource.

### Apache Airflow

**Công dụng và tình huống:** Airflow điều phối DAG batch theo dependency, schedule/retry/backfill. Dùng refresh features sau upstream partitions. [Official TaskFlow tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html)

```python
import pendulum
from airflow.sdk import dag, task
@dag(schedule="@daily", start_date=pendulum.datetime(2026, 1, 1, tz="UTC"), catchup=False)
def revenue_pipeline():
    @task
    def aggregate() -> int:
        return sum([10, 20, 30])
    aggregate()
revenue_pipeline()
```

**Kết quả:** File định nghĩa DAG daily trong môi trường Airflow đã cấu hình; không tự thực thi khi đọc file.

**Đánh giá:** Ví dụ dùng Airflow mới `airflow.sdk`, version cũ khác. Cần scheduler/metadata/executor; XCom chứa reference thay data lớn. Không dùng cho từng HTTP request.

### DVC

**Công dụng và tình huống:** DVC version data/model lớn bằng Git metadata và cache/remote, có pipeline/experiment workflow. Dùng ghép data revision với training code. [Official getting started](https://doc.dvc.org/start)

```bash
# Inside an existing Git repository with data/features.parquet available.
dvc init
dvc add data/features.parquet
git add .dvc .dvcignore data/features.parquet.dvc data/.gitignore
```

**Kết quả:** Trong Git repo có data/features.parquet, tạo metadata nhỏ để commit.

**Đánh giá:** Git push chỉ chuyển metadata; cần DVC remote + push/pull artifact riêng. Quản lý ACL/retention; đây là CLI workflow tool, không phải numerical library.

## Ba pipeline hoàn chỉnh và trách nhiệm từng phần

### Tabular ML: dự đoán từ bảng

**Stack:** pandas/Polars → Pandera → scikit-learn Pipeline → metric/CV → MLflow → artifact → FastAPI/ONNX Runtime. XGBoost/LightGBM/CatBoost là estimator thay thế sau baseline. Chia train/validation/test theo bài toán thật; fit transformation trên train, tune trên validation, dùng test giữ lại cho đánh giá cuối. Lưu feature names/order/types, preprocessing và model như một đơn vị version.

### Deep learning: fine-tune một model

**Stack:** Datasets/DataLoader → PyTorch → Accelerate nếu cần distribution → PEFT nếu architecture phù hợp → checkpoint/eval → serving. TensorFlow/Keras hoặc JAX-based stack là hướng thay thế. Dataloader, gradient accumulation, precision, batch size và sequence length quyết định memory. Adapter ít tham số không có nghĩa bỏ base model. Pin checkpoint revision và license; thử một batch nhỏ trước full run.

### RAG: trả lời dựa trên tài liệu

**Stack:** parse/chunk → embedding phù hợp ngôn ngữ → vector store có metadata/ACL → retrieval → rerank tùy nhu cầu → generation → citations/eval. LlamaIndex nghiêng về data/index/query; LangChain về model/tool composition; LangGraph làm state/checkpoint rõ. Không cần cả ba cùng lúc. Lọc ACL lúc retrieval, giữ document/version/source IDs, xử lý delete/reindex khi nguồn đổi. Đo recall của retrieval riêng với chất lượng câu trả lời; giảm hallucination không phải chỉ tăng số chunk.

## MLOps: bốn việc không nên nhầm

| Việc | Công cụ ví dụ | Đầu ra cần quản lý |
| --- | --- | --- |
| Orchestration | Prefect hoặc Airflow | Run state, dependency, retry, schedule |
| Experiment tracking | MLflow hoặc W&B | Params, metrics, artifacts, code/data revision |
| Artifact/data version | DVC hoặc object store có version | File thật + metadata + quyền truy cập |
| Serving | vLLM, Ollama, ONNX Runtime hoặc app model worker | Model version, capacity, rollout, latency/error |

Optuna tìm hyperparameter; Evaluate tính metric; chúng không thay các lớp trên. Chỉ promote model khi metric theo task và tài nguyên đạt ngưỡng đã định. Model service cần warmup/readiness, bounded batch/queue, timeout/cancel và rollback; nhiều Uvicorn worker có thể nhân bản weights/VRAM thay vì tăng throughput.

## Phạm vi chuyên biệt để mở rộng

best-of-ml-python còn gợi ý graph, geospatial, recommender, reinforcement learning, privacy và medical data. Guide này đi sâu vào pipeline phổ biến để có ví dụ nhất quán; các miền đó cần guide và evaluation riêng. Trước khi thêm package, xác định modality/data size/objective/hardware và integration đang cần, thay vì cài toàn bộ danh sách.
