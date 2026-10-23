"""Hourly bars: a new 5-bar volume high on a rising Heikin-Ashi candle goes long, on a falling Heikin-Ashi candle goes short; reversing.
Port of FMZ strategy #442545 "Adaptive Fluctuation Strategy Based on Quantitative Range Breakthrough" (Ranged Volume Strategy - evo (EvoCrypto)).

FMZ source id: 442545

Source
    https://www.fmz.com/strategy/442545 (PineScript v4, FMZ last modified 2024-02-22 16:50:46).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 143-188), range length 5; Heikin-Ashi colours on
    Close = security(heikinashi(tickerid), period, close);  Open = security(heikinashi(tickerid), period, open);  Highest = highest(volume, 5)
    Up = Highest > Highest[1] and Close > Open -> entry Long;  Dn = Highest > Highest[1] and Close < Open -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Heikin-Ashi series is requested on the chart's own timeframe, so it is the HA candle of each
      bar (close = ohlc4, open = the average of the previous HA open and close, seeded with the first
      bar's (open + close) / 2): no look-ahead. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume-range breakouts in the Heikin-Ashi candle's direction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as its 5-bar highest; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442545_volume_range_high_heikin_ashi_direction_1h_reversal"
FAMILY = "volume_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "range_len": [5, 10],
}
DEFAULT_PARAMS = {"range_len": 5}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    ha_c = ((o + h + lo + c) / 4).to_numpy(dtype=float)
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    ha_o = np.full(m, np.nan)
    for i in range(m):
        ha_o[i] = (ov[i] + cv[i]) / 2 if i == 0 else (ha_o[i - 1] + ha_c[i - 1]) / 2
    hv = v.rolling(int(p["range_len"])).max()
    new_hi = (hv > hv.shift(1)).to_numpy()
    up = new_hi & (ha_c > ha_o)
    dn = new_hi & (ha_c < ha_o)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(up, index=ix), false, pd.Series(dn, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
