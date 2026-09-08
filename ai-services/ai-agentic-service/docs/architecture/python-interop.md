# Interop Mojo ↔ Python

Exemplo canônico do curso: tokenizer.

```text
application (ou teste)
      ↓
Tokenizer / LangGraphRuntime / TransformersRuntime / EmbeddingModel / TrainingRuntime
      ↓
Python.import_module(...)    # só src/interop/python/
      ↓
src/python/{agentic,models,training,integrations}
      ↓
LangGraph, transformers, torch, sentence-transformers, PEFT, TRL, datasets, bitsandbytes
```

Fora desta camada: HTTP/gRPC (Mojo), Langfuse (OTEL no Mojo), vLLM e LiteLLM (serviços externos).

Quem usa o tokenizer escreve só Mojo:

```mojo
var tokenizer = Tokenizer()
var tokens = tokenizer.encode("Hello Mojo")
```

## Os 10 pontos

1. **Arquivo `.py`** — `src/python/tokenizer.py`. Continua sendo Python. Não é compilado pelo Mojo.
2. **Bridge Mojo** — `src/interop/python/tokenizer_bridge.mojo`. Expõe `Tokenizer`.
3. **Import** — `PythonBridge.import_local("python.models.tokenizer")` coloca `src` em `sys.path` e pede o módulo ao CPython.
4. **Funções Python** — `module.some_fn(arg)` no `PythonObject`.
5. **Classes Python** — `module.Tokenizer()` cria a instância e o Mojo guarda o `PythonObject`.
6. **Retorno** — o resultado chega como `PythonObject` (`list`, `str`, …).
7. **Conversão** — `PythonBridge.to_string_list` vira `List[String]` antes de sair do bridge.
8. **Erros** — exceção Python vira `OrchestratorError` (`unavailable` / `internal`). Domain não vê traceback CPython.
9. **Lifetime** — `Tokenizer._impl` segura a instância Python enquanto o struct Mojo viver. Não deixe o `PythonObject` morrer e continue usando-o.
10. **Custo** — `encode` é uma travessia por texto; `encode_batch` é uma travessia por lote. Nunca tokenize caractere a caractere atravessando a fronteira.

## Runtime: achar o CPython

O compilador Mojo não embute o `libpython`. Sem `MOJO_PYTHON_LIBRARY` o processo aborta em `Py_Initialize`.

Este repo aponta para o `libpython` do Pixi (`pixi.toml` `[activation.env]` e `.vscode/settings.json`). A primeira chamada que toca Python paga a inicialização do CPython (cara); as seguintes reutilizam o runtime.

Não use `PYTHONPATH=src` no ambiente do `mojo`: isso faz o compilador perder o módulo `std`. O `PythonBridge.ensure_local_path()` coloca `src` no `sys.path` só em runtime.

## Quando crescer para Hugging Face

Não mova a regra de inferência para Python. Troque só `src/python/tokenizer.py` (e, se preciso, o bridge) para chamar `transformers`. `application/` continua falando com `Tokenizer`.
