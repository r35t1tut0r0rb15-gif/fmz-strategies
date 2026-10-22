"""RSI 14 and Bollinger (20, 2) re-entries on the same bar, 4-hour bars: the RSI crossing over 30 while the close crosses back over the lower band goes long, the RSI crossing under 70 while the close
crosses back under the upper band goes short; reversing.
Port of FMZ strategy #446986 "RSI和布林带双重策略RSI-and-Bollinger-Bands-Double-Strategy" (CA_-_RSI_Bol_Strat_1.1 (Bollinger + RSI, Double Strategy by ChartArt)).

FMZ source id: 446986

Source
    https://www.fmz.com/strategy/446986 (PineScript v4, FMZ last modified 2024-04-03 17:54:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-169), RSI 14, levels 30 / 70; BB 20 / 2
    crossover(rsi, 30) and crossover(close, lower) -> entry RSI_BB_L, else cancel;  crossunder(rsi, 70) and crossunder(close, upper) -> entry RSI_BB_S, else cancel

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are market orders filled at the next open, before the next bar's cancel can reach
      them, so the cancels never act. Pine's stdev is the population deviation. strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. FREQ = "4h" from the backtest header (UTC-aligned 4-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, simultaneous RSI and band re-entries.
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

NAME = "fmz_446986_rsi_band_double_reentry_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "bb_len": [20, 50],
}
DEFAULT_PARAMS = {"rsi_len": 14, "bb_len": 20, "mult": 2.0, "os": 30.0, "ob": 70.0}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["bb_len"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    lower = basis - float(p["mult"]) * sd
    upper = basis + float(p["mult"]) * sd
    os_, ob = float(p["os"]), float(p["ob"])
    r1, c1 = r.shift(1), c.shift(1)
    le = (r > os_) & (r1 <= os_) & (c > lower) & (c1 <= lower.shift(1))
    se = (r < ob) & (r1 >= ob) & (c < upper) & (c1 >= upper.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
