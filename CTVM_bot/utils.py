def rating_to_stars(rating):
    """Converte una valutazione in un display a stelle (su scala 1-5)."""
    if rating is None or rating == 0:
        return "Non valutato"
    stars = round(rating)
    return "⭐" * stars + "☆" * (5 - stars)
