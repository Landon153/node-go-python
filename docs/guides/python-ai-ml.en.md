# Python: AI, ML, inference, and MLOps

[README](../../README.en.md) · [VI](python-ai-ml.vi.md) · [EN](python-ai-ml.en.md)

Examples illustrate API shape and require matching dependencies in a separate environment. They are not all executed in CI. Input files, model weights, providers/keys/services, and hardware are called out where required; do not install every library together. The offline lab at the end of the data guide is execution-checked.

Categories were explored using [best-of-ml-python](https://github.com/lukasmasuch/best-of-ml-python) and [awesome-python](https://github.com/vinta/awesome-python), then checked against official docs per entry. Descriptions/assessments/examples are original; rankings and performance claims based on stars are not carried over.

## Training, inference, and applications

Training learns parameters from data; inference executes a trained model; applications add auth, retrieval, tools, and UI. PyTorch, TensorFlow, Keras, and JAX are alternatives rather than mandatory simultaneous layers. Select by model/team/hardware. Async APIs do not automatically offload inference; multiple processes can duplicate weights and pools.

### Shared data for scikit-learn, XGBoost, and LightGBM examples

Iris is bundled and needs no model downloads/API keys. Execute this fixture before those examples; CatBoost has its own data. Toy metrics do not establish quality outside the exercise.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

## Classical ML

### scikit-learn

**Purpose and scenario:** preprocessing, supervised/unsupervised estimators, pipelines, train/test splits, cross-validation, metrics, and parameter search. Scenario: establish a tabular classification baseline. [Official getting started](https://scikit-learn.org/stable/getting_started.html).

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=300))
model.fit(X_train, y_train)
print(model.score(X_test, y_test))
```

**Expected result and assessment:** held-out classification accuracy. Caveat: fitting preprocessing on all data causes leakage; keep it inside the pipeline. Choose splits by time/group when random splitting violates the real prediction problem. Accuracy alone is insufficient for imbalanced classes; this is not deep-learning training infrastructure.

### XGBoost

**Purpose and scenario:** boosting for regression, classification, and ranking, with native, scikit-learn, and distributed interfaces. Scenario: benchmark a tree model for structured features. [Official Python introduction](https://xgboost.readthedocs.io/en/stable/python/python_intro.html).

```python
from xgboost import XGBClassifier
model = XGBClassifier(n_estimators=30, max_depth=3, tree_method="hist", random_state=42)
model.fit(X_train, y_train)
print(model.predict(X_test[:3]))
model.save_model("iris.ubj")
```

**Expected result and assessment:** predicted class IDs and a model artifact. Caveat: early stopping requires an appropriate validation set and correct API for the installed version. GPU configuration depends on build/hardware. Tune and evaluate on the actual dataset; tree boosting is not automatically best for every modality.

### LightGBM

**Purpose and scenario:** boosted decision trees with histogram-based training and leaf-wise tree growth. Scenario: compare tabular models with controlled depth/leaves and held-out evaluation. [Official Python introduction](https://lightgbm.readthedocs.io/en/stable/Python-Intro.html).

```python
from lightgbm import LGBMClassifier
model = LGBMClassifier(n_estimators=30, num_leaves=7, random_state=42, verbosity=-1)
model.fit(X_train, y_train)
print(model.predict_proba(X_test[:2]))
```

**Expected result and assessment:** a class-probability row per input. Caveat: leaf-wise growth can overfit insufficient data; constrain leaves/depth and validate. Native categorical support still requires documented dtype/encoding conventions. Training speed is workload dependent; no unqualified comparison to XGBoost or CatBoost.

### CatBoost

**Purpose and scenario:** boosted trees with built-in categorical-feature handling. Scenario: train on a table containing country/product strings without manually constructing one-hot columns. [Official usage examples](https://catboost.ai/docs/en/concepts/python-usages-examples).

```python
from catboost import CatBoostClassifier
rows = [["VN", 10], ["US", 30], ["VN", 12], ["US", 28]]
model = CatBoostClassifier(iterations=20, depth=2, verbose=False, random_seed=42)
model.fit(rows, [0, 1, 0, 1], cat_features=[0])
print(model.predict([["VN", 11]]))
```

**Expected result and assessment:** a class prediction using the categorical first feature. Caveat: four rows illustrate syntax only; they cannot substantiate model quality. Missing/category policies, train/validation boundaries, and model size require attention. Native handling does not remove the need to evaluate drift and leakage.

## Deep learning and gradients

### PyTorch

**Purpose and scenario:** tensors, automatic differentiation, neural network modules, optimizers, data loading, and accelerator execution. Scenario: customize a training loop or fine-tune a pretrained network. [Official quickstart](https://docs.pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html).

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

**Expected result and assessment:** one gradient update, not a trained predictor. Caveat: devices/dtypes must align; `model.eval()` changes layer behavior while `no_grad`/`inference_mode` controls gradient tracking. GPU memory, seeds, kernels, and installation builds affect behavior. Avoid CPU/GPU performance claims from this toy step.

### TensorFlow

**Purpose and scenario:** tensor computation, differentiation, `tf.data`, training, and export/deployment tooling. Scenario: maintain a training/export workflow already built around TensorFlow. [Official beginner quickstart](https://www.tensorflow.org/tutorials/quickstart/beginner).

```python
import tensorflow as tf
x = tf.Variable(3.0)
with tf.GradientTape() as tape:
    loss = x ** 2
print(tape.gradient(loss, x).numpy())
```

**Expected result and assessment:** derivative `6.0`. Caveat: eager execution and traced graph behavior differ; Python side effects inside `tf.function` need care. Accelerator support depends on OS, build, and installation. `tf.keras` and independently installed Keras should follow documented compatibility guidance.

### Keras

**Purpose and scenario:** layers, model composition, standard fit/evaluate loops, callbacks, and saving. Modern Keras supports multiple backends. Scenario: quickly construct a dense network while retaining a clear model definition. [Official Sequential guide](https://keras.io/guides/sequential_model/).

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

**Expected result and assessment:** a model with 4 input features and 3 output class probabilities once trained. Caveat: `summary` constructs/describes a model; it does not train it. Use backend-neutral operations for portable custom layers. Backend packages, custom code, and saved-format compatibility need explicit choices.

### JAX

**Purpose and scenario:** array computation plus `grad`, `jit`, and `vmap` transformations for differentiable numerical programs. Scenario: optimize a scientific function or develop research code. [Official beginner guide](https://docs.jax.dev/en/latest/beginner_guide.html).

```python
import jax
import jax.numpy as jnp
def squared_norm(x):
    return jnp.sum(x ** 2)
gradient = jax.jit(jax.grad(squared_norm))
print(gradient(jnp.array([2.0, 3.0])))
```

**Expected result and assessment:** `[4, 6]`; the first invocation includes tracing/compilation work. Caveat: transformations expect suitable functional computation; hidden mutation, dynamic Python control flow, and shapes need care. PRNG handling is explicit. JAX itself is not a complete model serving or experiment-management stack.

## Models, datasets, and embeddings

### Transformers

**Purpose and scenario:** architectures, tokenizers/processors, pretrained loading, task pipelines, generation, and Trainer workflows. Scenario: classify incoming text with an existing model before considering fine-tuning. [Official quickstart](https://huggingface.co/docs/transformers/quicktour).

```python
from transformers import pipeline
classifier = pipeline(
    "text-classification",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
)
print(classifier("The delivery was excellent."))
```

**Expected result and assessment:** label/score objects for English sentiment. Caveat: first use downloads weights; model task, language, license, revision, RAM, and device support matter. A classifier score is not a universal confidence guarantee. Check current Trainer argument names when promoting older examples.

### Datasets

**Purpose and scenario:** load/version dataset splits, map preprocessing, use Arrow-backed storage, and stream data. Scenario: convert a local JSONL corpus into tokenized training records. [Official quickstart](https://huggingface.co/docs/datasets/quickstart).

```python
from datasets import Dataset
records = Dataset.from_dict({"text": ["hello", "goodbye"], "label": [0, 1]})
records = records.map(lambda row: {"length": len(row["text"])})
print(records[0])
```

**Expected result and assessment:** a record containing text, label, and derived length. Caveat: distinguish random-access `Dataset` from streaming `IterableDataset`. Mapping can create caches and disk usage. Audio/video/image data may need extras; decoded object types have changed between versions. Dataset licensing and train/test contamination remain application responsibilities.

### Tokenizers

**Purpose and scenario:** train/run tokenizers, normalization, pre-tokenization, subwords, padding, truncation, offsets, and serialization. Scenario: inspect exactly which token IDs a model receives. [Official quicktour](https://huggingface.co/docs/tokenizers/quicktour).

```python
from tokenizers import Tokenizer
tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
encoded = tokenizer.encode("Ship the order today.")
print(encoded.tokens, encoded.ids)
```

**Expected result and assessment:** token strings and corresponding vocabulary IDs, including the tokenizer's special-token behavior. Caveat: the tokenizer must match the checkpoint; switching vocabulary or normalization changes inputs. Downloads/revisions apply here too. Token IDs are model inputs, not embeddings or semantic vectors.

### Accelerate

**Purpose and scenario:** adapt PyTorch training to devices, distributed execution, and mixed precision with less setup code. Scenario: move the same training loop from a CPU development run to multiple accelerators. [Official quicktour](https://huggingface.co/docs/accelerate/quicktour).

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

**Expected result and assessment:** one device-aware gradient update. Caveat: a real training loop should prepare its DataLoader too, zero gradients, gather evaluation outputs correctly, and use the proper launcher/configuration. Accelerate does not choose a good dataset, objective, or model for you.

### PEFT

**Purpose and scenario:** parameter-efficient adaptation methods such as LoRA, updating adapters instead of every base-model parameter. Scenario: adapt a pretrained causal model to a narrow task. [Official quicktour](https://huggingface.co/docs/peft/quicktour).

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

**Expected result and assessment:** a model with trainable adapter parameters; no fine-tuning has happened yet. Caveat: target module names depend on the architecture. You still load/run the base model, so LoRA does not eliminate its compute/memory requirements. Quantization, adapter merging, and training configurations need separate verification.

### Sentence Transformers

**Purpose and scenario:** encode text into semantic vectors; separate cross-encoder models rerank query/document pairs. Scenario: semantic duplicate detection or the retrieval step of RAG. [Official quickstart](https://www.sbert.net/docs/quickstart.html).

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
vectors = model.encode(["Shipping policy", "How deliveries work"])
print(vectors.shape)
print(model.similarity(vectors, vectors))
```

**Expected result and assessment:** shape `(2, 384)` for this checkpoint and a similarity matrix. Caveat: an English model is not a justified default for Vietnamese documents. Pick language/task-appropriate checkpoints and preserve a compatible, versioned embedding contract across indexing/querying; asymmetric models may use different query/document prompts and encode_query/encode_document paths. Similarity is a ranking signal, not a verified answer or factuality score.

## NLP, images, audio, and time series

### spaCy

**Purpose and scenario:** tokenization plus optional trained pipeline components for tags, dependency parsing, and named entities. Scenario: extract organization names before routing documents. [Official spaCy 101](https://spacy.io/usage/spacy-101).

```python
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("Acme opened an office in London.")
print([(entity.text, entity.label_) for entity in doc.ents])
```

**Expected result and assessment:** entity spans/labels predicted by the installed English pipeline; exact predictions depend on the model. Caveat: install the matching pipeline separately (`python -m spacy download en_core_web_sm`). `spacy.blank` only gives language/tokenization behavior unless components are added. Language coverage and domain accuracy require evaluation.

### OpenCV

**Purpose and scenario:** image I/O, color conversion, filtering, thresholding, feature operations, geometry, and video capture. Scenario: prepare a scanned image for OCR. [Official Python tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html), [thresholding tutorial](https://docs.opencv.org/4.13.0/d7/d4d/tutorial_py_thresholding.html).

```python
import cv2
image = cv2.imread("receipt.png", cv2.IMREAD_GRAYSCALE)
if image is None:
    raise FileNotFoundError("receipt.png")
_, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
cv2.imwrite("receipt-binary.png", binary)
```

**Expected result and assessment:** a binary grayscale image; thresholding does not recognize text. Caveat: OpenCV commonly uses BGR color order. GUI functions may not work in headless environments. Install one compatible OpenCV wheel variant and avoid conflating preprocessing with OCR or an object detector.

### librosa

**Purpose and scenario:** audio loading, spectrograms, MFCCs, pitch/rhythm analysis, and music/audio feature extraction. Scenario: turn audio into features for a separate classifier. [Official MFCC API](https://librosa.org/doc/0.11.0/generated/librosa.feature.mfcc.html).

```python
import librosa
waveform, sample_rate = librosa.load("clip.wav", sr=16000)
mfcc = librosa.feature.mfcc(y=waveform, sr=sample_rate, n_mfcc=13)
print(mfcc.shape)
```

**Expected result and assessment:** a `(13, time_frames)` feature matrix. Caveat: resampling, channel mixing, hop size, and feature normalization affect outputs. Audio codecs may need optional system/dependency support. librosa computes features; it is not a speech-to-text service. This source is versioned 0.11.0 because rolling tutorial URLs did not load during research.

### statsmodels

**Purpose and scenario:** statistical models, tests, parameter diagnostics, and time-series models including state-space/SARIMAX. Scenario: a transparent baseline for daily demand forecasts. [Official forecasting notebook](https://www.statsmodels.org/stable/examples/notebooks/generated/statespace_forecasting.html), [ARIMA API](https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html).

```python
from statsmodels.tsa.arima.model import ARIMA
series = [10, 12, 11, 14, 13, 15, 14, 16, 15, 18, 17, 19]
fitted = ARIMA(series, order=(1, 0, 0)).fit()
print(fitted.forecast(steps=3))
```

**Expected result and assessment:** three forecast values from the fitted model. Caveat: 12 observations illustrate the API only. Validate in chronological order, consider seasonality/stationarity and residual diagnostics, and inspect convergence warnings. A narrow prediction interval is conditional on model assumptions, not guaranteed future accuracy.

## RAG, agents, and model serving

### LangChain

**Purpose and scenario:** provider/model interfaces, tools, agent construction, and application composition. Scenario: let a model call an order lookup function. [Official quickstart](https://docs.langchain.com/oss/python/langchain/quickstart).

```python
import os
from langchain.agents import create_agent
def order_status(order_id: str) -> str:
    """Return the status of the example order."""
    return "shipped" if order_id == "A1" else "unknown"
agent = create_agent(model=os.environ["LANGCHAIN_MODEL"], tools=[order_status])
answer = agent.invoke({"messages": [{"role": "user", "content": "Where is order A1?"}]})
```

**Expected result and assessment:** an agent message state; the configured model may choose to call the tool. Caveat: install the provider integration and configure credentials or a local model. The stub is deliberately read-only. Tools with writes need application authorization, bounded arguments, and failure handling. This framework orchestrates calls; it does not train the underlying model.

### LangGraph

**Purpose and scenario:** graph nodes/edges, state updates, persistence/checkpoints, interrupts, and durable agent workflows. Scenario: make retrieval, answer drafting, and approval explicit. [Official overview](https://docs.langchain.com/oss/python/langgraph/overview).

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

**Expected result and assessment:** `{"status": "validated"}` without an LLM. Caveat: compiling a graph does not enable persistence automatically. Production resumption needs a suitable checkpointer and side-effect strategy; replay/retries require idempotency. LangGraph can be used without LangChain model wrappers.

### LlamaIndex

**Purpose and scenario:** load documents, split into nodes, create/query indexes, connect retrieval stores, and build RAG workflows. Scenario: search a small internal document set. [Official starter tutorial](https://developers.llamaindex.ai/python/framework/getting_started/starter_example/).

```python
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
response = index.as_query_engine().query("What is the shipping policy?")
print(response)
```

**Expected result and assessment:** an answer using retrieved document context after model/embedding configuration. Caveat: default settings can call remote embedding/LLM providers and incur cost; choose them explicitly for a runnable example. Parsing packages and integrations are separately installed. Chunking, ACL-filtered retrieval, citations, deletion/reindexing, and evaluation remain design work.

### vLLM

**Purpose and scenario:** run supported pretrained LLMs for batch inference or an HTTP API, with serving-specific scheduling and cache management. Scenario: put one compatible model behind an internal inference endpoint. [Official quickstart](https://docs.vllm.ai/en/latest/getting_started/quickstart/).

```bash
vllm serve Qwen/Qwen2.5-1.5B-Instruct --host 127.0.0.1 --port 8000
```

**Expected result and assessment:** a local model server after weights load on compatible hardware; applications send completion/chat requests to it. Caveat: check supported models, hardware, RAM/VRAM, chat templates, quantization, and version-specific installation. Serving an API is different from training. Throughput/latency depends on batching, sequence lengths, concurrency, and hardware; avoid universal speed claims.

### Ollama

**Purpose and scenario:** a local/hosted model runtime with HTTP APIs; `ollama-python` is the Python client. Scenario: prototype chat without writing model-loading code. [Official Python repository](https://github.com/ollama/ollama-python), [API introduction](https://docs.ollama.com/api/introduction).

```python
import ollama
reply = ollama.chat(
    model="llama3.2",
    messages=[{"role": "user", "content": "Explain an HTTP timeout."}],
)
print(reply.message.content)
```

**Expected result and assessment:** a generated response when the Ollama runtime is running and that model is available (`ollama pull llama3.2`). Caveat: the Python package alone is not the runtime. Model size/hardware/language/task fit differ. Local defaults and cloud options have different network, credential, and cost properties; do not say every Ollama invocation is automatically offline.

### ONNX Runtime

**Purpose and scenario:** execute ONNX graphs with selectable execution providers across deployment targets. Scenario: serve an exported classifier outside its training framework. [Official Python guide](https://onnxruntime.ai/docs/get-started/with-python.html).

```python
import numpy as np
import onnxruntime as ort
# Assume an exported Iris classifier expecting [batch, 4] float32 input.
session = ort.InferenceSession("iris.onnx", providers=["CPUExecutionProvider"])
input_name = session.get_inputs()[0].name
outputs = session.run(None, {input_name: np.array([[5.1, 3.5, 1.4, 0.2]], dtype=np.float32)})
print(outputs)
```

**Expected result and assessment:** the model's declared output arrays; class labels/probabilities depend on export. Caveat: the artifact must exist and shapes, names, dtypes, opset, and providers must match. Export/conversion requires separate tooling; numerical equivalence should be checked against the original model. Runtime support is not automatic acceleration.

### Hugging Face Evaluate

**Purpose and scenario:** load metric, comparison, and dataset measurement modules with a common API. Scenario: compute held-out classifier accuracy or a task-appropriate text metric. [Official quick tour](https://huggingface.co/docs/evaluate/a_quick_tour).

```python
import evaluate
metric = evaluate.load("accuracy")
print(metric.compute(predictions=[0, 1, 1], references=[0, 0, 1]))
```

**Expected result and assessment:** accuracy `2/3`. Caveat: modules may be downloaded and have extra dependencies. Classification accuracy, generation overlap, retrieval recall, and judge-based factuality assess different things. A RAG system needs retrieval and answer evaluation plus task-specific human inspection; no one score establishes correctness.

## Tracking, tuning, orchestration, and artifacts

### MLflow

**Purpose and scenario:** record parameters/metrics/artifacts, package/load models, track experiments, and manage models across a lifecycle. Scenario: compare model runs reproducibly and link artifacts to measured results. [Official tracking quickstart](https://mlflow.org/docs/latest/ml/tracking/quickstart/).

```python
import mlflow
mlflow.set_experiment("shipping-baseline")
with mlflow.start_run():
    mlflow.log_param("max_depth", 3)
    mlflow.log_metric("validation_accuracy", 0.91)
```

**Expected result and assessment:** a tracked run with one parameter and metric. The value `0.91` is deliberately illustrative, not a measured benchmark. Caveat: tracking URI, database/artifact storage, auth, retention, and compatible model flavors need configuration. Tracking metadata does not itself enforce reproducible datasets or deploy a reliable inference service.

### Weights & Biases

**Purpose and scenario:** record runs, metrics, configuration, artifacts, and experiment comparisons in a managed or configured environment. Scenario: compare training curves across researchers. [Official SDK repository](https://github.com/wandb/wandb), [initialization API source](https://github.com/wandb/wandb/blob/main/wandb/sdk/wandb_init.py).

```python
import wandb
with wandb.init(project="shipping-baseline", config={"lr": 0.001}, mode="offline") as run:
    run.log({"epoch": 1, "loss": 0.7})
```

**Expected result and assessment:** a locally recorded offline run; the metric is illustrative. Caveat: online sync and team hosting have their own credentials, data handling, storage, and plan choices. Avoid logging secrets or customer payloads as config/artifacts. The official docs quickstart redirected unsuccessfully during research; the official GitHub SDK README was checked instead.

### Optuna

**Purpose and scenario:** define a search space with trials, optimize an objective, and compare studies; supports pruning/integrations. Scenario: tune model depth/learning rate against validation data. [Official first study tutorial](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/001_first.html).

```python
import optuna
def objective(trial):
    x = trial.suggest_float("x", -5.0, 5.0)
    return (x - 3.0) ** 2
study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=30)
print(study.best_params, study.best_value)
```

**Expected result and assessment:** a sampled parameter near the optimum, with no exact guarantee after 30 trials. Caveat: tuning on the test set contaminates final evaluation. Bound trial resources, preserve seeds/storage, and choose optimization direction/metric correctly. The example optimizes a toy function, not model quality.

### Prefect

**Purpose and scenario:** tasks/flows, run states, retries, scheduling, deployments, and observability for data pipelines. Scenario: extract, validate, and publish a daily feature table. [Official v3 quickstart](https://docs.prefect.io/v3/get-started/quickstart).

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

**Expected result and assessment:** a tracked local flow returning 60. Caveat: decorating a function does not schedule or deploy it automatically. Configure the orchestration backend/runtime; retries require idempotent external writes. A task's CPU work still needs appropriate execution resources.

### Apache Airflow

**Purpose and scenario:** dependency-oriented scheduling, task execution, retries, monitoring, and backfills for data workflows. Scenario: refresh analytical features after upstream partitions arrive. [Official TaskFlow tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html).

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

**Expected result and assessment:** a registered DAG definition when placed in a configured Airflow environment, not execution from simply reading the file. Caveat: this is the newer `airflow.sdk` import; older major versions differ. Airflow requires scheduler/metadata/execution infrastructure. Keep large datasets out of ordinary XCom messages; pass artifact references. It is a batch workflow orchestrator rather than a per-request HTTP handler.

### DVC

**Purpose and scenario:** track large data/model artifacts through Git-stored metadata and a content cache/remote, plus pipeline/experiment workflows. Scenario: associate a training dataset revision with the code that produced a model. [Official getting started](https://doc.dvc.org/start).

```bash
# Inside an existing Git repository with data/features.parquet available.
dvc init
dvc add data/features.parquet
git add .dvc .dvcignore data/features.parquet.dvc data/.gitignore
```

**Expected result and assessment:** lightweight metadata is ready for Git tracking; the large file is managed through DVC's cache. Caveat: a Git push only transfers Git metadata; configure a DVC remote and push/pull artifact content separately. Access control, retention, and actual file availability require their own handling. DVC is a workflow/CLI tool, not a numerical Python library.

## Three complete pipelines and component responsibilities

### Tabular ML: predictions from tables

**Stack:** pandas/Polars → Pandera → scikit-learn Pipeline → metrics/CV → MLflow → artifact → FastAPI/ONNX Runtime. XGBoost/LightGBM/CatBoost are alternate estimators after a baseline. Split train/validation/test by the real prediction problem; fit transformations on train, tune on validation, and reserve test for final evaluation. Version feature names/order/types, preprocessing, and model together.

### Deep learning: fine-tuning a model

**Stack:** Datasets/DataLoader → PyTorch → Accelerate for distribution when needed → PEFT for compatible architectures → checkpoints/evaluation → serving. TensorFlow/Keras or JAX-based stacks are alternatives. Data loading, gradient accumulation, precision, batch size, and sequence length affect memory. Small adapters still require the base model. Pin checkpoint revisions/licenses and try a small batch before full runs.

### RAG: document-grounded answers

**Stack:** parse/chunk → language-appropriate embeddings → vector store with metadata/ACL → retrieval → optional reranking → generation → citations/evaluation. LlamaIndex emphasizes data/index/query, LangChain model/tool composition, and LangGraph explicit state/checkpoints. All three are not required together. Apply ACL filters during retrieval, preserve document/version/source IDs, and handle deletion/reindexing. Evaluate retrieval recall separately from answer quality; more chunks alone do not establish factuality.

## MLOps: four distinct responsibilities

| Responsibility | Example tools | Managed outputs |
| --- | --- | --- |
| Orchestration | Prefect or Airflow | Run state, dependencies, retries, schedules |
| Experiment tracking | MLflow or W&B | Params, metrics, artifacts, code/data revisions |
| Artifact/data versioning | DVC or versioned object storage | Actual files, metadata, and access controls |
| Serving | vLLM, Ollama, ONNX Runtime, or app model workers | Model versions, capacity, rollout, latency/errors |

Optuna searches hyperparameters; Evaluate computes metrics; neither replaces those layers. Promote models only after task metrics/resources meet defined criteria. Serving needs warmup/readiness, bounded batches/queues, timeout/cancellation, and rollback; extra Uvicorn workers may duplicate weights/VRAM rather than improve throughput.

## Specialist expansion areas

best-of-ml-python also surfaces graphs, geospatial, recommenders, reinforcement learning, privacy, and medical data. This guide develops common pipelines with consistent examples; those domains need dedicated guides/evaluation. Identify modality, data size, objective, hardware, and the missing integration before adding packages rather than installing the entire list.
