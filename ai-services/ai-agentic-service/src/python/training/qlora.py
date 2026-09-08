"""QLoRA / bitsandbytes quantization config. One coarse prepare() call.

bitsandbytes stays behind this module. Do not import it from domain.
"""

from __future__ import annotations

from python._lazy import dump, installed, load, require


class QLoRARuntime:
    def ping(self) -> str:
        return dump(
            {
                "backend": "qlora",
                "bitsandbytes": installed("bitsandbytes"),
                "peft": installed("peft"),
            }
        )

    def prepare(self, config_json: str) -> str:
        config = load(config_json)
        require("bitsandbytes")
        bits = int(config.get("bits") or 4)
        return dump(
            {
                "method": "qlora",
                "bits": bits,
                "quantization": "nf4" if bits == 4 else "int8",
            }
        )
