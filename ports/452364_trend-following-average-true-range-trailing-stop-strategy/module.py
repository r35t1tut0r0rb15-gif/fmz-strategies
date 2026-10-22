"""Close crossings of a clamped ATR line, 1-hour bars: the line is the previous line raised to at least the close minus 3 ATR 10 and then capped at the close plus 3 ATR; the close crossing over it goes long, under it goes short; reversing.
Port of FMZ strategy #452364 "Trend Following Average True Range Trailing Stop Strategy" (Long TAP (ATR trailing line)).

FMZ source id: 452364

Source
    https://www.fmz.com/strategy/452364 (PineScript v5, FMZ last modified 2024-05-24 18:12:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-138), key value 3; ATR 10
    line = min(max(nz(line[1]), close - 3 atr), close + 3 atr);  crossover(close, line) -> entry Long;  crossunder(close, line) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two statements are applied as written (ta.highest / ta.lowest over 1 bar are the values
      themselves): unlike the usual UT-bot line it never resets on a flip, it is raised to close - 3
      ATR and then capped at close + 3 ATR every bar. While the ATR is na the line is na (nz turns
      the previous na into 0 on the next bar). The pos variable only colours the plot. REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR-line crossings.
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

NAME = "fmz_452364_clamped_atr_line_cross_reversal"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key": [3.0, 2.0],
    "atr_len": [10, 14],
}
DEFAULT_PARAMS = {"key": 3.0, "atr_len": 10}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    nl = (float(p["key"]) * _atr(bars_df, p["atr_len"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    line = np.full(m, np.nan)
    for i in range(m):
        prev = line[i - 1] if i > 0 and not np.isnan(line[i - 1]) else 0.0
        if np.isnan(nl[i]):
            continue                          # math.max / min with na give na
        line[i] = min(max(prev, cv[i] - nl[i]), cv[i] + nl[i])
    ln = pd.Series(line, index=c.index)
    c1, l1 = c.shift(1), ln.shift(1)
    le = (c > ln) & (c1 <= l1)
    se = (c < ln) & (c1 >= l1)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
