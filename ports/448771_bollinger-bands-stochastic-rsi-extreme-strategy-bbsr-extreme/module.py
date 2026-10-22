"""Band re-entries after stochastic-RSI extremes, 1-hour bars: a close rising back over the lower band (20, 2) after K and D under 10 goes long, a close falling back under the upper band after K and D over
90 goes short; reversing (the 1.5 % stop armed on later signal bars is not ported).
Port of FMZ strategy #448771 "Bollinger Bands Stochastic RSI Extreme Strategy BBSR Extreme Strategy" (BBSRExtStrat (BBSR Extreme Strategy [nachodog])).

FMZ source id: 448771

Source
    https://www.fmz.com/strategy/448771 (PineScript v5, FMZ last modified 2024-04-18 16:55:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-162), BB 20 / 2; stochastic RSI: RSI 14, stoch 14, K / D 3; limits 90 / 10; stop 1.5 % of the current close
    Bull = close[1] < lower[1] and close > lower and k[1] < 10 and d[1] < 10 -> entry Bull Entry;  Bear mirrored at the upper band (k / d > 90) -> entry Bear Entry
    exit(Bull Entry, stop = close x 0.985, when = Bear or close < lower);  exit(Bear Entry, stop = close x 1.015, when = Bull or close > upper)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each stop is created only on a bar where its when-condition holds, from that bar's close, and
      is re-sent on later such bars: it starts after entry and moves, which stops() cannot express, so
      it is not ported (mark trailing_stop_pending; as #437800); positions end at the opposite entry
      meanwhile. Pine's stdev is the population deviation. REVERSAL INTENDED. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the late-armed stop not ported (mark).
    2 generic: PASS, band re-entries after stochastic-RSI extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the 1.5 % stop quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_448771_band_reentry_stochrsi_extreme_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "upper_limit": [90.0, 80.0],
}
DEFAULT_PARAMS = {"length": 20, "upper_limit": 90.0, "lower_limit": 10.0, "mult": 2.0, "k": 3, "d": 3, "rsi_len": 14, "stoch_len": 14}


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
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper = basis + float(p["mult"]) * sd
    lower = basis - float(p["mult"]) * sd
    r = _rsi(c, int(p["rsi_len"]))
    sn = int(p["stoch_len"])
    lo_r, hi_r = r.rolling(sn).min(), r.rolling(sn).max()
    st = 100 * (r - lo_r) / (hi_r - lo_r).where(hi_r > lo_r)
    k = st.rolling(int(p["k"])).mean()
    d = k.rolling(int(p["d"])).mean()
    ul, ll = float(p["upper_limit"]), float(p["lower_limit"])
    bear = (c.shift(1) > upper.shift(1)) & (c < upper) & (k.shift(1) > ul) & (d.shift(1) > ul)
    bull = (c.shift(1) < lower.shift(1)) & (c > lower) & (k.shift(1) < ll) & (d.shift(1) < ll)
    false = pd.Series(False, index=bars_df.index)
    return bull & ~bear, false, bear, false.copy()


def portfolio_kwargs(**params):
    return {}
