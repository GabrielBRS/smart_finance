"""Python escape hatch. Loaded at runtime by Mojo bridges, not compiled by Mojo.

This package is not the application. Mojo owns HTTP, gRPC, routing, domain,
use cases and orchestration. Modules here wrap Python-only ML libraries.

Out of scope here:
- HTTP / gRPC servers
- Langfuse SDK (use OpenTelemetry from Mojo)
- vLLM (external inference service)
- LiteLLM (external proxy)
"""
