from abc import ABC, abstractmethod

from app import store


class DataProvider(ABC):
    """One alternative-data source. `name` is the DB key under
    `provider_signals`; `real_world_analog` documents which actual API this
    stub stands in for, shown by GET /providers for demo narration.
    """

    name: str
    category: str
    real_world_analog: str

    def fetch_raw(self, persona_id: str) -> dict:
        """Returns the raw, source-shaped metrics for this persona.
        Backed today by the seeded `provider_signals` table; a real
        integration would call the provider's API here instead.
        """
        signal = store.get_provider_signal(persona_id, self.name)
        if signal is None:
            raise ValueError(f"no seeded signal for {self.name}/{persona_id}")
        return signal

    @abstractmethod
    def normalize(self, raw: dict) -> float:
        """Maps this source's raw metrics to a 0-1 sub-score."""

    def score(self, persona_id: str) -> dict:
        raw = self.fetch_raw(persona_id)
        return {
            "provider": self.name,
            "category": self.category,
            "real_world_analog": self.real_world_analog,
            "raw": raw,
            "normalized_value": round(self.normalize(raw), 3),
        }
