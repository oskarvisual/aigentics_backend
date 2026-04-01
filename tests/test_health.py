from app.core.health import DependencyCheckResult, compute_overall_status


def test_compute_overall_status_ok() -> None:
    results = [
        DependencyCheckResult(name="mysql", status="ok", latency_ms=1, detail="ok"),
        DependencyCheckResult(name="redis", status="ok", latency_ms=1, detail="ok"),
    ]
    assert compute_overall_status(results) == "ok"


def test_compute_overall_status_degraded() -> None:
    results = [
        DependencyCheckResult(name="mysql", status="ok", latency_ms=1, detail="ok"),
        DependencyCheckResult(name="redis", status="error", latency_ms=1, detail="down"),
    ]
    assert compute_overall_status(results) == "degraded"


def test_compute_overall_status_error() -> None:
    results = [
        DependencyCheckResult(name="mysql", status="error", latency_ms=1, detail="down"),
        DependencyCheckResult(name="redis", status="error", latency_ms=1, detail="down"),
    ]
    assert compute_overall_status(results) == "error"
