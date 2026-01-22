from pathlib import Path
import importlib.util

# Load the sibling module `keyboards.py` (project-level) and re-export its helpers
ROOT = Path(__file__).resolve().parent.parent
module_path = ROOT / "keyboards.py"
spec = importlib.util.spec_from_file_location("project_keyboards_module", str(module_path))
_kb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_kb)

inline_menu = _kb.inline_menu
reply_menu = _kb.reply_menu

__all__ = ["inline_menu", "reply_menu"]
