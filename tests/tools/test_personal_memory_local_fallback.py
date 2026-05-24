from pathlib import Path

from tools import personal_memory_local_fallback as fallback
from tools.registry import registry


def _write_import(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "personal-memory-import-index.md").write_text(
        "# Personal Memory MCP Import Index\n", encoding="utf-8"
    )
    (root / "personal-memory-import-memory-01.md").write_text(
        """# Personal Memory MCP Import: memory chunk 1

---

## user_identitate_core

- id: `1`
- kind: `memory`
- type: `user`
- scopes: `assistant`
- updated_at: `2026-05-12T00:00:00.000Z`
- description: Date stabile de identitate Razvan.

### Content

# Date stabile

Răzvan locuiește în Arad.

---

## person_rares_girgiz

- id: `2`
- kind: `memory`
- type: `reference`
- scopes: `assistant`
- updated_at: `2026-05-12T00:00:00.000Z`
- description: Fiul lui Razvan.

### Content

Rareș este fiul lui Răzvan.
""",
        encoding="utf-8",
    )
    (root / "personal-memory-import-soul-01.md").write_text(
        """# Personal Memory MCP Import: soul chunk 1

---

## comunicare_reguli

- id: `3`
- kind: `soul`
- type: `user`
- scopes: `assistant`
- updated_at: `2026-05-12T00:00:00.000Z`
- description: Reguli stricte de comunicare.

### Content

Răspunde concis.
""",
        encoding="utf-8",
    )


def test_local_import_is_found_in_hermes_home_memory(monkeypatch, tmp_path):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    _write_import(tmp_path / "memory")

    assert fallback.has_local_personal_memory_import() is True


def test_read_and_search_local_import(monkeypatch, tmp_path):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    _write_import(tmp_path / "memory")

    assert "Arad" in fallback._read_handler({"name": "user_identitate_core"})
    result = fallback._search_handler({"query": "Rareș", "limit": 1})
    assert "person_rares_girgiz" in result


def test_registers_read_only_tools(monkeypatch, tmp_path):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    _write_import(tmp_path / "memory")

    names = fallback.register_personal_memory_local_fallback("unit test")

    assert "mcp_personal_memory_read_memory" in names
    assert registry.get_toolset_for_tool("mcp_personal_memory_read_memory") == "mcp-personal-memory"
    save_entry = registry.get_entry("mcp_personal_memory_save_memory")
    assert save_entry is not None
    save_result = save_entry.handler({"name": "x", "content": "y"})
    assert "read-only" in save_result


def test_bootstrap_contains_soul_recent_and_index(monkeypatch, tmp_path):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    _write_import(tmp_path / "memory")

    text = fallback._bootstrap_handler({"scope": "assistant", "recent_limit": 1})

    assert "local fallback" in text
    assert "comunicare_reguli" in text
    assert "user_identitate_core" in text
    assert "## Index" in text


def test_bootstrap_recent_memories_are_sorted_by_updated_at_desc(monkeypatch, tmp_path):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    root = tmp_path / "memory"
    _write_import(root)
    (root / "personal-memory-import-memory-02.md").write_text(
        """# Personal Memory MCP Import: memory chunk 2

---

## state_newer_context

- id: `4`
- kind: `memory`
- type: `project`
- scopes: `assistant`
- updated_at: `2026-05-24T10:00:00.000Z`
- description: Newer operating context.

### Content

This is the freshest context.
""",
        encoding="utf-8",
    )

    text = fallback._bootstrap_handler({"scope": "assistant", "recent_limit": 2})

    assert text.index("state_newer_context") < text.index("user_identitate_core")
