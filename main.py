import os
from pathlib import Path


def create_directory_structure():
    """Create the rl-copilot-langgraph directory structure"""

    # Define the base directory
    base_dir = Path("rl-copilot-langgraph")

    # Define all directories to create
    directories = [
        base_dir,
        base_dir / "configs",
        base_dir / "data",
        base_dir / "index",
        base_dir / "src" / "agent",
        base_dir / "src" / "memory",
        base_dir / "src" / "tools",
        base_dir / "src" / "types",
        base_dir / "tests"
    ]

    # Create all directories
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

    # Define files to create (empty files)
    files = [
        base_dir / "app.py",
        base_dir / ".env.example",
        base_dir / "requirements.txt",
        base_dir / "configs" / "settings.toml",
        base_dir / "data" / "rl_book.pdf",
        base_dir / "index" / "pdf.index",
        base_dir / "index" / "meta.json",
        base_dir / "src" / "agent" / "agent_graph.py",
        base_dir / "src" / "agent" / "prompts.py",
        base_dir / "src" / "memory" / "graph_memory.py",
        base_dir / "src" / "tools" / "pdf_ingest.py",
        base_dir / "src" / "tools" / "pdf_store.py",
        base_dir / "src" / "tools" / "web_tools.py",
        base_dir / "src" / "tools" / "util.py",
        base_dir / "src" / "types" / "state.py",
        base_dir / "tests" / "eval_questions.jsonl"
    ]

    # Create empty files
    for file_path in files:
        file_path.touch()
        print(f"Created file: {file_path}")


    print(f"\nDirectory structure created successfully at: {base_dir.absolute()}")



if __name__ == "__main__":
    create_directory_structure()