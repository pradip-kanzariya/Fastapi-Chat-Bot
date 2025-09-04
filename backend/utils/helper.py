from datetime import datetime

def format_created_at(created_at: datetime) -> str:
    """Formate datetime for created_at datetime value."""
    now = datetime.now().date()
    if created_at.date() == now:
        # Same day → only show time
        return f"Today {created_at.strftime('%H:%M:%S')}"
    else:
        # Different day → show full date and time
        return created_at.strftime("%Y-%m-%d %H:%M:%S")
    