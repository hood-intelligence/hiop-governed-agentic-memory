"""Refuse frozen hiop_dev as the live memory target."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from importlib.machinery import SourceFileLoader

mod = SourceFileLoader(
    "live_vector_proof",
    str(Path(__file__).resolve().parents[1] / "scripts" / "04_live_vector_proof.py"),
).load_module()


def test_dsn_hiop_dev_is_rejected():
    assert mod._db_name("postgresql://u:p@h:26257/hiop_dev?sslmode=verify-full") == "hiop_dev"


def test_dsn_agent_memory_accepted_name():
    assert mod._db_name("postgresql://u:p@h:26257/hiop_agent_memory?sslmode=require") == "hiop_agent_memory"
