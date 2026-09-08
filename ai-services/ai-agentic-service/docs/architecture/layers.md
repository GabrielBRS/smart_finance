# Camadas Mojo-first

```text
                MOJO
                  │
      ┌───────────┼───────────┐
      │           │           │
   Domain    Application   Infrastructure
                              │
                              ▼
                           Interop
                              │
                              ▼
                           Python
                              │
                              ▼
                   Ecossistema Python
```

| Camada | Path | Entra aqui | Não entra aqui |
| --- | --- | --- | --- |
| Domain | `src/domain/` | tipos, regras, ports/traits | I/O, Python, vendors |
| Application | `src/application/` | use cases, grafo, agents, fluxo RAG | HTTP, JSON, gRPC, `Python.import_module` |
| Bootstrap | `src/bootstrap/` | `Application.build()`, wiring | regras de negócio |
| Transport | `src/transport/` | router, handlers, HTTP/gRPC | regras de domínio |
| Infrastructure | `src/infrastructure/` | adapters Mojo, IPC, compute, settings loader | `PythonObject` |
| Interop | `src/interop/python/` | bridges Mojo → CPython | regras de negócio |
| Python | `src/python/` | wrappers finos de libs Python-only | orquestração |

`src/ai_orchestrator/` é legado (Strangler Fig). Código Python novo vai para `src/python/`.

Adapters Python: `agentic/langgraph_runtime.py`, `models/{transformers,tokenizer,embeddings}`, `training/{trainer,peft,lora,qlora,datasets}`, `integrations/mlflow_adapter.py`. Bridges em `src/interop/python/`. Sem Langfuse/vLLM/LiteLLM neste processo.

## Compile time vs runtime

| Momento | O que acontece |
| --- | --- |
| **Compile time** | `mojo build` / `mojo run` compilam `.mojo`. Structs, traits e `main` viram binário (`./build/agentd`). Arquivos `.py` **não** entram nesse passo. |
| **Runtime** | O binário Mojo sobe. Se um bridge chama `Python.import_module`, o CPython embutido carrega `src/python/*.py` e as libs do site-packages. |

## Custo da fronteira

```text
Mojo → Python runtime → PythonObject → conversões → retorno para Mojo
```

Cada travessia aloca objetos Python, solta o GIL de forma cara e converte tipos. Prefira uma chamada que processa um lote inteiro, não milhares de idas e voltas por token.

## Migração futura

```text
hoje:  Mojo → Python Bridge → python/*.py
depois: Mojo → implementação nativa Mojo
```

Quem chama `Tokenizer.encode` não muda. Só o corpo do bridge (ou um novo tipo que satisfaz o mesmo contrato) é substituído.
