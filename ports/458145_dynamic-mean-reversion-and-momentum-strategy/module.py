"""Bollinger 20 / 2 extremes confirmed by the RSI 14, 2-hour bars: a close under the lower band with the RSI under 30 goes long, over the upper band with the RSI over 70 goes short; reversing. The 2 ATR bracket is re-sent every bar from the latest close and is not ported (pending).
Port of FMZ strategy #458145 "Dynamic Mean Reversion and Momentum Strategy" (BARONES - Mean Reversion and Momentum Strategy).

FMZ source id: 458145

Source
    https://www.fmz.com/strategy/458145 (PineScript v5, FMZ last modified 2024-07-30 12:12:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-198), RSI 14, levels 30 / 70; BB 20, 2 sd; ATR 14; stop and target 2 ATR from the current close
    close < lower and rsi < 30 -> entry Long;  close > upper and rsi > 70 -> entry Short;  every bar: exit(Long / Short, limit / stop = close +- 2 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent on every bar from that bar's close and ATR, so its levels move after entry:
      stops() cannot express a level re-set every bar, so it is described here and kept pending (as
      #438034, mark trailing_stop_pending). Positions end at the opposite entry until then. REVERSAL
      INTENDED. No sizing code. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band extremes with RSI confirmation; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the ATR bracket inputs stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_458145_bb20_rsi_extreme_entries_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_len": [20, 50],
    "bb_mult": [2.0, 2.5],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 2.0, "rsi_len": 14}


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
    n, k = int(p["bb_len"]), float(p["bb_mult"])
    basis = c.rolling(n).mean()
    dev = k * c.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsi_len"]))
    le = (c < basis - dev) & (r < 30)
    se = (c > basis + dev) & (r > 70)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
