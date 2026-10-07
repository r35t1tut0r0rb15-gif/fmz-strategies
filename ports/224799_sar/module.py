"""Parabolic SAR side: long while the close is above SAR, short while below (always in).
Port of FMZ strategy #224799 "SAR抛物线转向指标" (Parabolic SAR indicator).

Source
    https://www.fmz.com/strategy/224799 (JavaScript, author "韬奋量化", FMZ last modified
    2021-11-02 10:53:24). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 79-126)
    records = GetRecords(time_interval = 3600 s); sar = talib.SAR(records, 0.02, 0.2)
    idle:  ticker.Last > sar[-1] -> buy;  ticker.Last < sar[-1] -> sell short
    long:  ticker.Last < sar[-1] -> close long (idle; the next poll opens the short)
    short: ticker.Last > sar[-1] -> close short (idle; the next poll opens the long)

Interpretation choices
    * The bot polls every 5 s on the forming bar; the port evaluates on completed bar t
      (ticker.Last -> close[t], sar[-1] -> SAR[t] including bar t, TA-Lib algorithm).
    * A close is followed 5 s later by the opposite entry, so a flip is a one-bar reversal:
      REVERSAL INTENDED (portfolio_kwargs {}; the engine's default opposite-entry reversal
      applies).
    * Bars: the `time_interval` argument defaults to 3600 s, so FREQ = "1h" (the code's own
      request; the backtest header overrides it to 86400 s).
    * SAR moves in price units but from the bars themselves: criterion 2 PASS.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_224799_parabolic_sar_side"
FAMILY = "parabolic_sar"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # code requests time_interval = 3600 s records (argument default)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "acceleration": [0.01, 0.02, 0.03],
    "maximum": [0.1, 0.2, 0.3],
}
DEFAULT_PARAMS = {"acceleration": 0.02, "maximum": 0.2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _sar(high, low, acc, maximum):
    """Parabolic SAR as TA-Lib's TA_SAR (first value at index 1; direction from MINUS_DM)."""
    h, lo = high.to_numpy(dtype=float), low.to_numpy(dtype=float)
    out = np.full(len(h), np.nan)
    if len(h) < 2:
        return pd.Series(out, index=high.index)
    diff_p, diff_m = h[1] - h[0], lo[0] - lo[1]
    minus_dm = diff_m if (diff_m > 0 and diff_p < diff_m) else 0.0
    is_long = not minus_dm > 0
    af = acc
    if is_long:
        ep, sar = h[1], lo[0]
    else:
        ep, sar = lo[1], h[0]
    new_low, new_high = lo[1], h[1]
    for t in range(1, len(h)):
        prev_low, prev_high = new_low, new_high
        new_low, new_high = lo[t], h[t]
        if is_long:
            if new_low <= sar:
                is_long, sar = False, ep
                sar = max(sar, prev_high, new_high)
                out[t] = sar
                af, ep = acc, new_low
                sar = max(sar + af * (ep - sar), prev_high, new_high)
            else:
                out[t] = sar
                if new_high > ep:
                    ep, af = new_high, min(af + acc, maximum)
                sar = min(sar + af * (ep - sar), prev_low, new_low)
        else:
            if new_high >= sar:
                is_long, sar = True, ep
                sar = min(sar, prev_low, new_low)
                out[t] = sar
                af, ep = acc, new_high
                sar = min(sar + af * (ep - sar), prev_low, new_low)
            else:
                out[t] = sar
                if new_low < ep:
                    ep, af = new_low, min(af + acc, maximum)
                sar = max(sar + af * (ep - sar), prev_high, new_high)
    return pd.Series(out, index=high.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sar = _sar(bars_df["high"], bars_df["low"], p["acceleration"], p["maximum"]).to_numpy()
    c = bars_df["close"].to_numpy(dtype=float)

    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if c[i] > sar[i] and pos != 1:
            le[i], pos = True, 1
        elif c[i] < sar[i] and pos != -1:
            se[i], pos = True, -1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
