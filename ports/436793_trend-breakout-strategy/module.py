"""Bar range against its average, 1-hour bars: a bar whose high-low range is smaller than the previous bar's 16-bar average range is long, larger is short, equal holds; an optional switch trades the reverse;
entries are sent on every bar of the state, reversing.
Port of FMZ strategy #436793 "Trend Breakout Strategy" ((H-L)/C Histogram Backtest).

FMZ source id: 436793

Source
    https://www.fmz.com/strategy/436793 (PineScript v3, FMZ last modified 2023-12-27 17:34:31).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 170-188), look back 1, SMA 16, % change off (range in price units), reverse off
    xPrice1 = high - low (or 100 (high - low) / close with % change on);  xPrice1SMA = sma(abs(xPrice1), 16)
    pos = 1 if xPrice1SMA[1] > abs(xPrice1), -1 if <, else pos[1];  possig = -pos when reverse;  entry Long / Short on possig

Interpretation choices (Pine rules in SURVEY_README.md)
    * The test compares a range with an average of the same ranges, so it is scale-free in either unit;
      the price-unit form (the default) is ported. The state is a level, so the entry is sent on every bar
      of the state; a same-side entry while in the position is ignored (pyramiding 0). REVERSAL INTENDED.
      No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, range against its own average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436793_range_vs_average_state"
FAMILY = "volatility_regime"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [16, 30],
    "bars_back": [1, 2],
}
DEFAULT_PARAMS = {"sma_len": 16, "bars_back": 1, "reverse": False}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    rng = (bars_df["high"] - bars_df["low"]).abs()
    avg = rng.rolling(int(p["sma_len"])).mean().shift(int(p["bars_back"]))
    a, r = avg.to_numpy(), rng.to_numpy()
    m = len(r)
    pos = np.zeros(m)
    prev = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if a[i] > r[i]:
                prev = 1.0
            elif a[i] < r[i]:
                prev = -1.0
            pos[i] = prev
    sig = -pos if p["reverse"] else pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(sig == 1, index=ix), false, pd.Series(sig == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
