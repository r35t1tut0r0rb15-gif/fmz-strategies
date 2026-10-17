"""Hull MA 32 direction, 1-hour bars: when the Hull MA is above its values of the last 2 bars the direction turns up (long),
below them down (short); otherwise it keeps the last direction; always in.
Port of FMZ strategy #434196 "Dual Moving Average Reversal Trading Strategy" (Moving Average Color (MA_color strategy)).

FMZ source id: 434196

Source
    https://www.fmz.com/strategy/434196 (PineScript v3, FMZ last modified 2023-12-04 16:39:13).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 105-177), MA type HullMA, length 32, reaction 2
    ma = wma(2 wma(close, 16) - wma(close, 32), round(sqrt(32)) = 6)
    direction = rising(ma, 2) ? 1 : falling(ma, 2) ? -1 : direction[1];  direction > 0 -> entry long;  < 0 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * rising(x, 2) is x above both of its previous 2 values (falling mirrors). The entries are levels
      (ignored when already in that position). strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, the slope of an average.
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

NAME = "fmz_434196_hull_direction"
FAMILY = "hull_ma"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len": [32, 64],
    "reaction": [2, 4],
}
DEFAULT_PARAMS = {"ma_len": 32, "reaction": 2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(v, n):
    w = np.arange(1, n + 1, dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ (w / w.sum())
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    cv = bars_df["close"].to_numpy(dtype=float)
    n = int(p["ma_len"])
    diff = 2 * _wma(cv, n // 2) - _wma(cv, n)
    sq = int(np.floor(np.sqrt(n) + 0.5))
    ma = np.full(len(cv), np.nan)
    ok = ~np.isnan(diff)
    if ok.sum() >= sq:
        f0 = int(np.argmax(ok))
        ma[f0:] = _wma(diff[f0:], sq)
    s = pd.Series(ma)
    r = int(p["reaction"])
    prev_max = s.shift(1).rolling(r).max().to_numpy()
    prev_min = s.shift(1).rolling(r).min().to_numpy()
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    d = 0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if ma[i] > prev_max[i]:
                d = 1
            elif ma[i] < prev_min[i]:
                d = -1
            tgt[i] = d
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
