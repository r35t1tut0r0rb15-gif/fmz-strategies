"""Double-decker RSI, 1-hour bars: RSI 5 above 70 with RSI 14 above 50 goes long, RSI 5 under 40 with RSI 14 under 50 goes short; a long closes when RSI 5 falls under 55, a short when it rises over 45.
Port of FMZ strategy #440428 "双层RSI交易策略Double-Decker-RSI-Trading-Strategy" (Strategy- Double Decker RSI).

FMZ source id: 440428

Source
    https://www.fmz.com/strategy/440428 (PineScript v4, FMZ last modified 2024-01-30 15:21:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 169-204), fast RSI 5, slow RSI 14; years 2000-2021 (the filter is fixed true); size 1
    long = rsi5 > 70 and rsi14 > 50 and position <= 0 -> entry Long;  short = rsi5 < 40 and rsi14 < 50 and position >= 0 -> entry Short
    rsi5 < 55 and position > 0 -> close_all;  rsi5 > 45 and position < 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * An opposite entry always comes with its own exit test true (RSI 5 under 40 is under 55; over 70
      is over 45), and close_all after an entry leaves the bar flat (as #430380): a position ends flat
      and the next entry starts from flat. Opposite entries cannot occur (entries only from flat). The
      size 1 is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, two RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: size 1 is sizing.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440428_double_decker_rsi"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_rsi": [5, 3],
    "slow_rsi": [14, 21],
}
DEFAULT_PARAMS = {"fast_rsi": 5, "slow_rsi": 14}


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
    f, s = _rsi(c, int(p["fast_rsi"])), _rsi(c, int(p["slow_rsi"]))
    L = ((f > 70) & (s > 50)).to_numpy()
    S = ((f < 40) & (s < 50)).to_numpy()
    LX, SX = (f < 55).to_numpy(), (f > 45).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if L[i] and pos <= 0:
            new = 1
        if S[i] and pos >= 0:
            new = -1
        if (LX[i] and pos > 0) or (SX[i] and pos < 0):
            new = 0                                      # close_all also cancels a same-bar entry
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt != 1), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt != -1), index=ix))


def portfolio_kwargs(**params):
    return {}
