"""Outer Bollinger band with RSI extremes, 15-minute bars: a close below the 3-stdev lower band with
RSI 14 at or under 20 goes long; a close above the 3-stdev upper band with RSI at or over 80 goes
short. Positions are held until the opposite signal.
Port of FMZ strategy #427986 "Dual Bollinger Quant Options Strategy" (Double Bollinger Binary Options).

FMZ source id: 427986

Source
    https://www.fmz.com/strategy/427986 (PineScript v5, FMZ last modified 2023-09-27 16:19:30).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 178-216), BB 20 x 2 (drawn) and 20 x 3, RSI 14 (20 / 80)
    buy = close < lower(20, 3) and rsi(14) <= 20 -> entry long ("CALL")
    sell = close > upper(20, 3) and rsi(14) >= 80 -> entry short ("PUT")

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source is meant for binary options (fixed-expiry bets); as a strategy() it holds each
      position until the opposite entry, and that is what is ported. The 2-stdev band is drawn only.
    * Margin settings are sizing. strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, standard deviations and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin settings stored in original_sizing.txt.
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

NAME = "fmz_427986_outer_bollinger_rsi_extreme"
FAMILY = "mean_reversion_band"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length2": [20, 40],
    "mult2": [3.0, 2.5],
}
DEFAULT_PARAMS = {"length2": 20, "mult2": 3.0, "rsi_len": 14, "rsi_low": 20, "rsi_high": 80}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length2"])
    basis, dev = c.rolling(n).mean(), p["mult2"] * c.rolling(n).std(ddof=0)
    d = c.diff()
    k = int(p["rsi_len"])
    up, dn = _rma(d.clip(lower=0), k), _rma(-d.clip(upper=0), k)
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())
    buy = ((c < basis - dev) & (rsi <= p["rsi_low"])).to_numpy()
    sell = ((c > basis + dev) & (rsi >= p["rsi_high"])).to_numpy()
    m = len(buy)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if buy[i]:
            pos = 1
        elif sell[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
