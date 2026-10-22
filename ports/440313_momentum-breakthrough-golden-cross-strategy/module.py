"""Monday MACD zero crossings, 1-hour bars, long only: the MACD (5, 13) line crossing above zero on a Monday with the RSI 14 above 50 goes long; the close crossing under the EMA 21 or the MACD line crossing
back under zero closes.
Port of FMZ strategy #440313 "Momentum Breakthrough Golden Cross Strategy" (MACD, EMA, and RSI Strategy).

FMZ source id: 440313

Source
    https://www.fmz.com/strategy/440313 (PineScript v5, FMZ last modified 2024-01-29 11:27:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 166-201), MACD 5 / 13 / 9; EMA 21; RSI 14, level 50
    buyCondition = crossover(macdLine, 0) and dayofweek == monday and rsi > 50 -> entry Long;  sellCondition = crossunder(close, ema21) or crossunder(macdLine, 0) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The comments speak of a weekly timeframe and a 50-day EMA, but the code runs everything on the
      chart's bars, as ported. dayofweek is read on the UTC bar open. The close acts only on a held
      long: on a bar with both, an entry from flat still fills. Long only. No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD zero crossings, EMA and RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: Mondays (UTC bar open) for entries.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440313_monday_macd_zero_cross_long"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [21, 50],
    "rsi_level": [50, 60],
}
DEFAULT_PARAMS = {"ema_len": 21, "rsi_level": 50, "fast": 5, "slow": 13, "rsi_len": 14}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    monday = pd.Series(bars_df.index.tz_convert("UTC").dayofweek == 0, index=c.index)
    buy = ((macd > 0) & (macd.shift(1) <= 0) & monday & (r > float(p["rsi_level"]))).to_numpy()
    sell = (((c < e) & (c.shift(1) >= e.shift(1))) | ((macd < 0) & (macd.shift(1) >= 0))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = 1 if buy[i] else pos
        if sell[i] and pos == 1 and new == 1:
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
