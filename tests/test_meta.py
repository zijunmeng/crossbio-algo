"""Meta tests — release-blocker guards: single version source + correct repo identity."""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _read(p):
    with open(os.path.join(ROOT, p)) as f:
        return f.read()


def test_all_versions_match():
    """pyproject == plugin.json == CITATION.cff == CHANGELOG == README Status (single source of truth)."""
    v = re.search(r'^version\s*=\s*"([^"]+)"', _read("pyproject.toml"), re.M).group(1)
    plugin = json.loads(_read(".claude-plugin/plugin.json"))["version"]
    cite = re.search(r'^version:\s*"([^"]+)"', _read("CITATION.cff"), re.M).group(1)
    cl = re.search(r"##\s*\[?([0-9]+\.[0-9]+\.[0-9]+)\]?", _read("CHANGELOG.md")).group(1)
    assert plugin == v, f"plugin.json {plugin} != pyproject {v}"
    assert cite == v, f"CITATION.cff {cite} != {v}"
    assert cl == v, f"CHANGELOG {cl} != {v}"
    m = re.search(r"^##\s+Status\s*\n+\s*v([0-9]+\.[0-9]+\.[0-9]+)", _read("README.md"), re.M)
    assert m, "README.md: no '## Status' line starting with a vX.Y.Z version"
    assert m.group(1) == v, f"README.md Status v{m.group(1)} != pyproject {v}"


def test_plugin_homepage_points_to_real_repo():
    plugin = json.loads(_read(".claude-plugin/plugin.json"))
    assert "zijunmeng/crossbio-algo" in plugin.get("homepage", ""), plugin.get("homepage")
