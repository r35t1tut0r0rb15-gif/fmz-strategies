"""Very slow RSI of ohlc4, 1-minute bars: the EMA 250 of a 500-bar RSI rising through 48 while at or under 50 goes long, falling through 52 while at or above 50 goes short; reversing.
Port of FMZ strategy #436910 "慢速RSI超买超卖策略Slow-RSI-OB-OS-Strategy" (SLOW RSI OB/OS Strategy).

FMZ source id: 436910

Source
    https://www.fmz.com/strategy/436910 (PineScript v4, FMZ last modified 2023-12-28 18:07:48).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 140-162), RSI 500 of ohlc4 (Wilder), EMA 250, OB 52, OS 48
    rsi = 100 - 100 / (1 + rma(up change, 500) / rma(down change, 500));  EmaRSI = ema(rsi, 250)
    long = change(EmaRSI) > 0 and EmaRSI <= 50 and crossover(EmaRSI, 48) -> entry Long;  short = change < 0 and EmaRSI >= 50 and crossunder(EmaRSI, 52) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The RSI is written out with rma as Pine's own (down == 0 -> 100, up == 0 -> 0). The commented-out
      exits are not ported; positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ =
      "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels.
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

NAME = "fmz_436910_slow_rsi_ema_levels"
FAMILY = "rsi_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [500, 250],
    "smoother": [250, 125],
}
DEFAULT_PARAMS = {"length": 500, "smoother": 250, "ob": 52.0, "os": 48.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    price = (o + h + lo + c) / 4
    d = price.diff()
    n = int(p["length"])
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())
    e = r.ewm(span=int(p["smoother"]), adjust=False).mean()
    ch = e.diff()
    ob, os_ = float(p["ob"]), float(p["os"])
    e1 = e.shift(1)
    lc = (ch > 0) & (e <= 50) & (e > os_) & (e1 <= os_)
    sc = (ch < 0) & (e >= 50) & (e < ob) & (e1 >= ob)
    false = pd.Series(False, index=bars_df.index)
    return lc, false, sc, false.copy()


def portfolio_kwargs(**params):
    return {}
