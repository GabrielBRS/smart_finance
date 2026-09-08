# Arquitetura

Mojo-first, hexagonal. HTTP e gRPC são adapters de entrada. Domain e
use cases não conhecem FastAPI, sockets, JSON de transporte nem CPython.

```text
main.mojo
    → bootstrap.Application.build()
        → HTTP Router → Handler → Use Case → Orchestrator / Domain
        → TCP (interop/python) só lê e escreve bytes
```

Não existe framework web oficial da Modular equivalente ao FastAPI.
O router e os handlers são nossos, em Mojo.

Ver `layers.md` e `python-interop.md`.
