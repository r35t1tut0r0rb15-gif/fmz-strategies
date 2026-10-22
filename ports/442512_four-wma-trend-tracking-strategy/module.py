"""Four WMA crossings, 1-hour bars: the WMA 10 crossing under the WMA 20 goes long, the WMA 40 crossing under the WMA 30 goes short (both as written); a 1 % target and 1 % stop from the entry; reversing.
Port of FMZ strategy #442512 "Four WMA Trend Tracking Strategy" (Four WMA Strategy with TP and SL (4WMA TP/SL)).

FMZ source id: 442512

Source
    https://www.fmz.com/strategy/442512 (PineScript v5, FMZ last modified 2024-02-22 15:21:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 142-180), WMA 10 / 20 (long), 30 / 40 (short); take profit 1 %, stop loss 1 %
    crossunder(wma10, wma20) -> entry Long, exit(limit = close (1 + 1 %), stop = close (1 - 1 %))
    crossunder(wma40, wma30) -> entry Short, exit(limit = close (1 - 1 %), stop = close (1 + 1 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long fires on the fast WMA crossing UNDER the slower one, as written. The bracket is 1 % of
      the signal close: a fixed fraction 0.01 of the fill (#437751); a new same-side signal while held
      moves the script's levels, which the port does not follow (as #439608). The "%" table values
      true are the 1.0 defaults. When both fire on one bar the later Short call wins (as #437773).
      strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, WMA crossings.
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

NAME = "fmz_442512_four_wma_cross_pct_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [0.01, 0.02],
    "sl_pct": [0.01, 0.02],
}
DEFAULT_PARAMS = {"tp_pct": 0.01, "sl_pct": 0.01, "long1": 10, "long2": 20, "short1": 30, "short2": 40}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    l1, l2 = _wma(c, int(p["long1"])), _wma(c, int(p["long2"]))
    s1, s2 = _wma(c, int(p["short1"])), _wma(c, int(p["short2"]))
    lsig = ((l1 < l2) & (l1.shift(1) >= l2.shift(1))).to_numpy()
    ssig = ((s2 < s1) & (s2.shift(1) >= s1.shift(1))).to_numpy()
    s_, t_ = float(p["sl_pct"]), float(p["tp_pct"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        if i + 1 < m:
            if ssig[i] and pos != -1:                    # the later Short call wins a same-bar pair
                se[i], pos, entry_i = True, -1, i + 1
            elif lsig[i] and not ssig[i] and pos != 1:
                le[i], pos, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
