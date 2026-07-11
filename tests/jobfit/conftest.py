import sys
import types
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _install_optional_dependency_stubs() -> None:
    try:
        import dotenv  # noqa: F401
    except ImportError:
        dotenv_stub = types.ModuleType("dotenv")
        dotenv_stub.load_dotenv = lambda *args, **kwargs: False
        sys.modules["dotenv"] = dotenv_stub

    try:
        import requests  # noqa: F401
    except ImportError:
        requests_stub = types.ModuleType("requests")

        class RequestException(Exception):
            pass

        def get(*args, **kwargs):
            raise RuntimeError("requests is not installed in this test environment")

        requests_stub.RequestException = RequestException
        requests_stub.get = get
        sys.modules["requests"] = requests_stub


def _install_legacy_package_stubs() -> None:
    agents_stub = types.ModuleType("src.agents")
    agents_stub.call_cv_agent = lambda *args, **kwargs: None

    class CVWriter:
        pass

    agents_stub.CVWriter = CVWriter
    agents_stub.google_search_agent = None
    agents_stub.tavily_search_agent = None
    agents_stub.call_job_parsr_agent = lambda *args, **kwargs: None
    sys.modules.setdefault("src.agents", agents_stub)

    utils_stub = types.ModuleType("src.utils")
    utils_stub.load_config = lambda *args, **kwargs: {}
    utils_stub.load_docx_template = lambda *args, **kwargs: None
    sys.modules.setdefault("src.utils", utils_stub)


_install_legacy_package_stubs()
_install_optional_dependency_stubs()
