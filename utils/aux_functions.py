from pathlib import Path

def get_summary_file(match_file: str) -> str:
    path = Path(match_file)
    # Replace folder and filename
    return str(path.parent.parent / "summary_logs" / f"city_flows_{path.name}")
