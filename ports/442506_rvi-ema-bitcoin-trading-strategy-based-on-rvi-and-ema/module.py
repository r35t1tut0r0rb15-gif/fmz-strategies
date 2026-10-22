"""RVI(4) crossing its signal line with an EMA 95 / 200 trend filter, 1-hour bars: from flat, the RVI crossing over with the low above a rising-stack EMA 95 goes long, the mirror short; exits when the bar's
low / high passes the signal bar's low - 2 ATR(19) stop or high + 1 ATR target, read at the close.
Port of FMZ strategy #442506 "基于RVI和EMA的比特币交易策略Bitcoin-Trading-Strategy-Based-on-RVI-and-EMA" (Relative Vigor Index (RVGI)).

FMZ source id: 442506

Source
    https://www.fmz.com/strategy/442506 (PineScript v5, FMZ last modified 2024-02-22 13:50:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 135-240), RVI 4; ATR 19; EMA 95 / 200; ATR SL 2.0, TP 1.0
    rvi = sum(swma(close - open), 4) / sum(swma(high - low), 4);  sig = swma(rvi);  esalcista = low > ema95 and ema95 > ema200;  bajista = high < ema95 and ema95 < ema200
    long: low < SL -> close;  high > TP -> close.  flat: crossover(rvi, sig) and esalcista -> entry BUY, SL = low - 2 atr, TP = high + 1 atr
    short: high > SL -> close;  low < TP -> close.  flat: crossunder and bajista -> entry SELL, SL = high + 2 atr, TP = low - 1 atr

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are strategy.close calls on the bar's own low / high against the levels set on the
      signal bar, read at the bar close and filled at the next open, not broker stops; they are
      tested from the bar the position is held at. Entries come only from flat. The "Atr TP" table
      value true is the 1.0 default. ta.swma is the 1-2-2-1 weighted average of four bars. No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RVI crossings with an EMA stack; signal-bar levels tested on the bar range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_442506_rvi_cross_ema_stack_atr_levels"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [4, 10],
    "atr_sl": [2.0, 1.0],
}
DEFAULT_PARAMS = {"length": 4, "atr_sl": 2.0, "atr_tp": 1.0, "atr_len": 19, "ema1": 95, "ema2": 200}


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


def _swma(x):
    return (x.shift(3) + 2 * x.shift(2) + 2 * x.shift(1) + x) / 6


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    with np.errstate(divide="ignore", invalid="ignore"):
        rvi = _swma(c - o).rolling(n).sum() / _swma(h - lo).rolling(n).sum()
    sig = _swma(rvi)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"]))
    e1 = c.ewm(span=int(p["ema1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ema2"]), adjust=False).mean()
    bull = ((lo > e1) & (e1 > e2)).to_numpy()
    bear = ((h < e1) & (e1 < e2)).to_numpy()
    up = ((rvi > sig) & (rvi.shift(1) <= sig.shift(1))).to_numpy()
    dn = ((rvi < sig) & (rvi.shift(1) >= sig.shift(1))).to_numpy()
    hv, lv, av = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), atr.to_numpy(dtype=float)
    ks, kt = float(p["atr_sl"]), float(p["atr_tp"])
    m = len(hv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    held, sl, tp = 0, 0.0, 0.0
    for i in range(m):
        new = held
        if held == 1 and (lv[i] < sl or hv[i] > tp):
            lx[i], new = True, 0
        elif held == -1 and (hv[i] > sl or lv[i] < tp):
            sx[i], new = True, 0
        if held == 0 and not np.isnan(av[i]):
            if up[i] and bull[i]:
                le[i], new, sl, tp = True, 1, lv[i] - av[i] * ks, hv[i] + av[i] * kt
            elif dn[i] and bear[i]:
                se[i], new, sl, tp = True, -1, hv[i] + av[i] * ks, lv[i] - av[i] * kt
        held = new
    ix = bars_df.index
    return tuple(pd.Series(a, index=ix) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
