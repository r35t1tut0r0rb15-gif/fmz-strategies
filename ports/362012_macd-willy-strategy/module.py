"""EMA 200 side with the MACD 12 / 26 / 9 histogram sign and a smoothed Williams %R (WMA 5 vs EMA 13 of %R 34), hourly bars: all three bullish holds a long, all bearish a short; the histogram and %R turning (with %R under -20 for longs, over -80 for shorts) closes; reversing.
Port of FMZ strategy #362012 "MACD Willy Strategy" (MACD Willy Strategy).

FMZ source id: 362012

Source
    https://www.fmz.com/strategy/362012 (PineScript v5, FMZ last modified 2022-05-09 16:32:15).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 95-219), EMA 200; MACD 12 / 26 / 9 (EMA / EMA); %R 34, WMA 5, EMA 13; volume MA 50 and daily ATR computed but unused
    close > ema200 and hist > 0 and wma(%R, 5) > ema(%R, 13) -> entry Long;  mirror -> entry Short
    hist < 0 and fast < slow and fast < -20 -> close Long;  hist > 0 and fast > slow and fast > -80 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The volume average and the daily ATR are computed but feed no order, so volume is not used (held by
      the static screen for the word "volume"). %R uses the 34-bar highest high and lowest low. The entries
      come before the closes: an entry that reverses a position stands although the other side's close is
      true on that bar (as #441963). REVERSAL INTENDED. The capital is sizing. The source carries the
      Mozilla Public License 2.0 notice. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA side with MACD and smoothed %R states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital 10000 stored, not ported.
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

NAME = "fmz_362012_ema200_macd_hist_smoothed_wpr_state_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "emalen1": [200, 100],
    "w_length": [34, 14],
}
DEFAULT_PARAMS = {"emalen1": 200, "w_length": 34, "fast_length": 12, "slow_length": 26, "signal_length": 9,
                  "fast_period": 5, "slow_period": 13}


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
    """Pine ta.wma on a series whose NaNs are only at the start."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        seg = v[s:]
        k = np.arange(n, 0, -1, dtype=float)            # weight n on the newest value
        r = np.convolve(seg, k)[:len(seg)] / k.sum()
        r[:n - 1] = np.nan
        out[s:] = r
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    e1 = ema(c, p["emalen1"])
    macd = ema(c, p["fast_length"]) - ema(c, p["slow_length"])
    hist = macd - ema(macd, p["signal_length"])
    n = int(p["w_length"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    wr = 100 * (c - hh) / (hh - ll)
    wf, ws = _wma(wr, int(p["fast_period"])), ema(wr, p["slow_period"])
    le = (c > e1) & (hist > 0) & (wf > ws)
    se = (c < e1) & (hist < 0) & (wf < ws)
    lx = (hist < 0) & (wf < ws) & (wf < -20)
    sx = (hist > 0) & (wf > ws) & (wf > -80)
    return le, lx & ~se & ~le, se, sx & ~le & ~se


def portfolio_kwargs(**params):
    return {}
