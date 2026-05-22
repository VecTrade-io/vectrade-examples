"""Validation tests for vectrade-examples repository.

Tests verify:
- All Python examples have valid syntax
- All examples use environment variables (no hardcoded keys)
- Directory structure follows conventions
- README references are accurate
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def python_files() -> list[Path]:
    """Collect all Python example files."""
    files = []
    for d in ["python", "use-cases", "templates"]:
        path = ROOT / d
        if path.exists():
            files.extend(path.rglob("*.py"))
    return sorted(files)


@pytest.fixture(scope="session")
def shell_files() -> list[Path]:
    """Collect all shell script files."""
    return sorted(ROOT.glob("curl/*.sh"))


class TestPythonExamples:
    """Validate Python example files."""

    def test_all_valid_syntax(self, python_files):
        """All Python files must have valid syntax."""
        errors = []
        for f in python_files:
            try:
                ast.parse(f.read_text())
            except SyntaxError as e:
                errors.append(f"{f.relative_to(ROOT)}: {e}")
        assert not errors, f"Syntax errors: {errors}"

    def test_no_hardcoded_live_keys(self, python_files):
        """No live API keys in examples."""
        pattern = re.compile(r"vq_live_[a-zA-Z0-9]{10,}")
        violations = []
        for f in python_files:
            if pattern.search(f.read_text()):
                violations.append(str(f.relative_to(ROOT)))
        assert not violations, f"Hardcoded keys in: {violations}"

    def test_uses_env_variable_pattern(self, python_files):
        """Examples should use os.environ or env vars for API keys."""
        for f in python_files:
            content = f.read_text()
            # Skip if file doesn't reference API keys at all
            if "api_key" not in content.lower() and "VecTrade(" not in content:
                continue
            # Should use environment variable pattern
            uses_env = (
                "os.environ" in content
                or "os.getenv" in content
                or "VECTRADE_API_KEY" in content
                or "VecTrade()" in content  # Auto-reads from env
            )
            assert uses_env, f"{f.relative_to(ROOT)} should use env vars for API keys"

    def test_quickstart_exists(self):
        """Python quickstart example must exist."""
        assert (ROOT / "python" / "quickstart.py").exists()


class TestShellExamples:
    """Validate shell script examples."""

    def test_quickstart_exists(self):
        """curl quickstart must exist."""
        assert (ROOT / "curl" / "quickstart.sh").exists()

    def test_no_hardcoded_keys(self, shell_files):
        """No hardcoded API keys in shell scripts."""
        pattern = re.compile(r"vq_live_[a-zA-Z0-9]{10,}")
        for f in shell_files:
            assert not pattern.search(f.read_text()), f"Hardcoded key in {f.name}"

    def test_uses_variable(self, shell_files):
        """Shell scripts should use $VECTRADE_API_KEY."""
        for f in shell_files:
            content = f.read_text()
            if "api" in content.lower() or "vectrade" in content.lower():
                assert "VECTRADE_API_KEY" in content or "$" in content


class TestStructure:
    """Validate repository structure."""

    @pytest.mark.parametrize("directory", [
        "python",
        "typescript",
        "curl",
        "use-cases",
        "templates",
    ])
    def test_directory_exists(self, directory):
        assert (ROOT / directory).is_dir(), f"Missing directory: {directory}"

    def test_readme_exists(self):
        assert (ROOT / "README.md").exists()

    def test_readme_references_examples(self):
        content = (ROOT / "README.md").read_text()
        assert "python" in content.lower() or "Python" in content


class TestSecurity:
    """Security-focused validation."""

    def test_no_private_keys(self, python_files):
        """No private key material in examples."""
        patterns = [
            re.compile(r"-----BEGIN.*PRIVATE KEY-----"),
            re.compile(r"sk_live_[a-zA-Z0-9]{10,}"),
        ]
        for f in python_files:
            content = f.read_text()
            for pat in patterns:
                assert not pat.search(content), f"Private key in {f.relative_to(ROOT)}"


class TestGitHubConfig:
    """Verify GitHub configuration files."""

    @pytest.mark.parametrize("filename", [
        "LICENSE",
        "README.md",
        "CHANGELOG.md",
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
    ])
    def test_oss_file_exists(self, filename):
        assert (ROOT / filename).exists()

    def test_codeowners_exists(self):
        assert (ROOT / ".github" / "CODEOWNERS").exists()

    def test_dependabot_exists(self):
        assert (ROOT / ".github" / "dependabot.yml").exists()

    def test_ci_workflow_exists(self):
        assert (ROOT / ".github" / "workflows" / "ci.yml").exists()
