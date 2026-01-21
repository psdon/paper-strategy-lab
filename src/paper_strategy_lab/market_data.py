from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class MarketData:
    prices: pd.DataFrame
    features: dict[str, pd.DataFrame] = field(default_factory=dict)

    def feature(self, name: str) -> pd.DataFrame:
        try:
            return self.features[name]
        except KeyError as e:
            raise KeyError(f"Missing feature {name!r}. Available: {sorted(self.features)}") from e

