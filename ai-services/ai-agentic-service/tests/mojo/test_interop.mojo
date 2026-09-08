from infrastructure.settings import load_settings
from interop.python.embeddings_bridge import EmbeddingModel
from interop.python.langgraph_bridge import LangGraphRuntime
from interop.python.tokenizer_bridge import Tokenizer
from interop.python.training_bridge import TrainingRuntime
from interop.python.transformers_bridge import TransformersRuntime
from std.testing import assert_equal, assert_true, TestSuite


def test_load_settings_uses_defaults_without_env() raises:
    var settings = load_settings()
    assert_equal(settings.app_name, "ai-orchestrator")
    assert_equal(settings.http_port, 8080)


def test_tokenizer_hides_python() raises:
    var tokenizer = Tokenizer()
    var tokens = tokenizer.encode("Hello Mojo")
    assert_equal(len(tokens), 2)
    assert_equal(tokens[0], "Hello")
    assert_equal(tokens[1], "Mojo")


def test_tokenizer_batch_is_one_crossing() raises:
    var tokenizer = Tokenizer()
    var texts = List[String]()
    texts.append("Hello Mojo")
    texts.append("one crossing")
    var batches = tokenizer.encode_batch(texts)
    assert_equal(len(batches), 2)
    assert_equal(len(batches[0]), 2)
    assert_equal(len(batches[1]), 2)
    assert_equal(batches[1][0], "one")


def test_python_runtimes_ping_without_heavy_deps() raises:
    var graph = LangGraphRuntime()
    var transformers = TransformersRuntime()
    var embeddings = EmbeddingModel()
    var training = TrainingRuntime()
    assert_true(graph.ping().find("langgraph") >= 0)
    assert_true(transformers.ping().find("transformers") >= 0)
    assert_true(embeddings.ping().find("sentence-transformers") >= 0)
    assert_true(training.ping().find("trl") >= 0)


def main() raises:
    TestSuite.discover_tests[__functions_in_module()]().run()
