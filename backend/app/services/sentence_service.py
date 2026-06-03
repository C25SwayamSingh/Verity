from app.utils.text import clean_text, split_sentences


class SentenceService:
    def process(self, raw_text: str) -> tuple[str, list[str]]:
        cleaned = clean_text(raw_text)
        return cleaned, split_sentences(cleaned)
