from std.python import PythonObject

from domain.errors import OrchestratorError
from domain.status import StatusCode
from interop.python.bridge import PythonBridge


struct TrainingRuntime:
    """Mojo-facing training facade (TRL, PEFT, datasets, QLoRA).

    Layer: interop/python
    Why Python: TRL / PEFT / Accelerate / datasets / bitsandbytes.
    Call train() once with the full config — never a Python step loop from Mojo.
    """

    var _trainer: PythonObject
    var _peft: PythonObject
    var _qlora: PythonObject
    var _datasets: PythonObject

    def __init__(out self) raises:
        try:
            self._trainer = PythonBridge.import_local(
                "python.training.trainer"
            ).Trainer()
            self._peft = PythonBridge.import_local(
                "python.training.peft_runtime"
            ).PeftRuntime()
            self._qlora = PythonBridge.import_local(
                "python.training.qlora"
            ).QLoRARuntime()
            self._datasets = PythonBridge.import_local(
                "python.training.datasets"
            ).DatasetRuntime()
        except e:
            raise OrchestratorError(
                StatusCode.unavailable, "falha ao criar TrainingRuntime"
            )

    def ping(self) raises -> String:
        return String(self._trainer.ping())

    def train(self, config_json: String) raises -> String:
        try:
            return String(self._trainer.train(config_json))
        except e:
            raise OrchestratorError(StatusCode.internal, "training.train falhou")

    def prepare_adapter(self, config_json: String) raises -> String:
        try:
            return String(self._peft.prepare(config_json))
        except e:
            raise OrchestratorError(
                StatusCode.internal, "training.prepare_adapter falhou"
            )

    def prepare_qlora(self, config_json: String) raises -> String:
        try:
            return String(self._qlora.prepare(config_json))
        except e:
            raise OrchestratorError(
                StatusCode.internal, "training.prepare_qlora falhou"
            )

    def load_dataset(self, config_json: String) raises -> String:
        try:
            return String(self._datasets.load(config_json))
        except e:
            raise OrchestratorError(
                StatusCode.internal, "training.load_dataset falhou"
            )
