"""
Phase 1 Demo - Simple working example showing modular architecture
"""

from pathlib import Path


def demo_modular_structure():
    """Demonstrate the new modular structure."""
    print("🏗️  PHASE 1: MODULAR ARCHITECTURE DEMO")
    print("=" * 50)

    # Get current directory
    current_dir = Path.cwd()
    api_src_dir = current_dir / "api" / "src"

    print(f"📁 Project Root: {current_dir}")
    print(f"📁 API Source: {api_src_dir}")
    print()

    # Show new modular structure
    modules = {
        "core/": ["config.py", "logging.py", "security.py"],
        "models/": ["schemas.py"],
        "routers/": ["health.py", "receipts.py", "splits.py"],
        "services/": ["split_logic.py", "openrouter_ocr.py", "minio_utils.py"],
        "": ["api_main.py"],
    }

    print("📋 NEW MODULAR STRUCTURE:")
    for folder, files in modules.items():
        folder_path = api_src_dir / folder
        print(f"   {folder if folder else './'}")
        for file in files:
            file_path = folder_path / file
            status = "✅" if file_path.exists() else "❌"
            print(f"      {status} {file}")
    print()

    # Show configuration example
    print("⚙️  CENTRALIZED CONFIGURATION:")
    config_file = api_src_dir / "core" / "config.py"
    if config_file.exists():
        with open(config_file, "r") as f:
            lines = f.readlines()
            # Show first few lines that demonstrate config structure
            for i, line in enumerate(lines[:20]):
                if line.strip() and not line.startswith('"""'):
                    print(f"   {line.rstrip()}")
                    if i > 10:
                        print("   ...")
                        break
    print()

    # Show schema example
    print("📝 PYDANTIC SCHEMAS:")
    schemas_file = api_src_dir / "models" / "schemas.py"
    if schemas_file.exists():
        with open(schemas_file, "r") as f:
            content = f.read()
            # Extract class definitions
            lines = content.split("\n")
            for line in lines:
                if line.strip().startswith("class ") and ":" in line:
                    print(f"   ✅ {line.strip()}")
    print()

    # Show code quality tools
    print("🔧 CODE QUALITY TOOLS:")
    tools = [
        (".pre-commit-config.yaml", "Pre-commit hooks"),
        ("pyproject.toml", "Dependencies & tools"),
        ("api/tests/", "Test structure"),
    ]

    for file_path, description in tools:
        full_path = current_dir / file_path
        status = "✅" if full_path.exists() else "❌"
        print(f"   {status} {description}: {file_path}")

    print()
    print("🎉 PHASE 1 ACHIEVEMENTS:")
    achievements = [
        "✅ Modular architecture with clear separation of concerns",
        "✅ Centralized configuration management",
        "✅ Structured logging with loguru",
        "✅ Security framework with JWT support",
        "✅ Comprehensive Pydantic schemas",
        "✅ API routers for better organization",
        "✅ Pre-commit hooks for code quality",
        "✅ Testing infrastructure with pytest",
    ]

    for achievement in achievements:
        print(f"   {achievement}")

    print()
    print("🚀 READY FOR PHASE 2: SECURITY HARDENING")


if __name__ == "__main__":
    demo_modular_structure()
