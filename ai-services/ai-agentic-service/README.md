# ai-orchestrator

Terceiro processo da plataforma: agentes, workflows e tools. O core é
**Mojo-first** (`main.mojo` → `./build/agentd`). Os três processos falam
**IPC ACE1** (mesmo framing do `ai-compute-engine` e do `ai-data-engine`).

O processo Mojo agora serve HTTP. gRPC fica como adapter de entrada
ainda não ligado. FastAPI legado em `src/ai_orchestrator/` é Strangler Fig.

```text
OS → ./build/agentd → main.mojo → bootstrap.Application
                                      ├─ HTTP Router → Handlers → Use Cases
                                      └─ Domain / Graph / Agents
                                              └─ Python só em interop/python
```

Camadas: `src/bootstrap`, `src/transport`, `src/domain`, `src/application`,
`src/infrastructure`, `src/interop/python`, `src/python`.
Python só para LangGraph / HF / torch / PEFT / TRL / datasets — nunca HTTP.
Detalhe em `docs/architecture/layers.md`.

## Transports

| Canal | Bind default | Estado |
| --- | --- | --- |
| IPC unix socket | `/tmp/ai-orchestrator-python.sock` | ACE1 health 1/2, agent 210, workflow 220 |
| HTTP | `0.0.0.0:8080` | `GET /health` `POST /agents/execute` `POST /workflows/execute` |
| gRPC | `0.0.0.0:50051` | adapter ainda não sobe |
| Compute IPC | `/tmp/ai-compute-engine.sock` | generate / embed |
| Data IPC | `/tmp/ai-data-engine.sock` | retrieve / rag |

Prefixo de ambiente: `AOR_*`.

## Run (Mojo)

Requer [Pixi](https://pixi.sh/) e Mojo 1.0+.

```bash
pixi install
pixi run test
pixi run run
```

Com o servidor no ar:

```bash
curl -s http://127.0.0.1:8080/health
curl -s -X POST http://127.0.0.1:8080/agents/execute \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"hello mojo"}'
curl -s -X POST http://127.0.0.1:8080/workflows/execute \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"ACE1"}'
```

## Run (legado Python — HTTP / gRPC)

```bash
uv sync
uv run pytest
uv run ai-orchestrator-python
uv run python examples/simple_agent/main.py
```
