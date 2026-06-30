import importlib.resources

import signaltest


def test_top_level_exports_present():
    for name in ["Case", "assert_no_regression", "run_suite", "ExactMatch", "Step"]:
        assert hasattr(signaltest, name)


def test_version_is_set():
    assert signaltest.__version__


def test_py_typed_marker_shipped():
    assert (importlib.resources.files("signaltest") / "py.typed").is_file()
