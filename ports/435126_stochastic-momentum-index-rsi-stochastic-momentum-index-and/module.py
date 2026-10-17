"""Noro's SMI / fast-RSI fades, 5-minute bars: a red bar with a real body while the 2-bar SMI is under -50 or the RSI 2 under
10 goes long; a green bar with a body while the SMI is over 50 or the RSI 2 over 90 goes short (reversing); a long is
closed on any green bar with a body and a short on any red one.
Port of FMZ strategy #435126 "基于Stochastic-Momentum-Index和RSI的量化策略Stochastic-Momentum-Index-and-RSI-Based-Quant-Trading-Strategy" (Noro's Stochastic Strategy v1.3).

FMZ source id: 435126

Source
    https://www.fmz.com/strategy/435126 (PineScript v2, FMZ last modified 2023-12-12 15:20:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 138-229), SMI K 2 / D 2 (SMA smoothing), limit 50; RSI 2, limit 10; colour and body filters on; martingale off; years 2018-2100
    up = (SMI < -50 or rsi2 < 10) and close < open and body;  dn = (SMI > 50 or rsi2 > 90) and close > open and body   (body = |close - open| > sma(body, 10) / 3)
    up -> close a short, entry long;  dn -> close a long, entry short;  (long and close > open or short and close < open) and body -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SMI is (close - mid of the 2-bar range) smoothed twice by SMA 2 over half the smoothed
      range, as written. The closes act on the position held on the bar; an entry on the same bar
      wins. The equity lot and the (off) martingale are sizing. strategy.entry reverses: REVERSAL
      INTENDED. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator extremes with bar filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity lot and the martingale option stored.
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

NAME = "fmz_435126_noro_smi_rsi_fade"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "limitsmi": [50, 30],
    "limitrsi": [10, 20],
}
DEFAULT_PARAMS = {"a": 2, "b": 2, "limitsmi": 50, "periodrsi": 2, "limitrsi": 10}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ch = c.diff()
    n = int(p["periodrsi"])
    fu = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    fd = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + fu / fd)).where(fu != 0, 0.0).where(fd != 0, 100.0).where(fu.notna())
    a, b = int(p["a"]), int(p["b"])
    ll, hh = lo.rolling(a).min(), h.rolling(a).max()
    avgrel = (c - (hh + ll) / 2).rolling(b).mean().rolling(b).mean()
    avgdiff = (hh - ll).rolling(b).mean().rolling(b).mean()
    smi = (avgrel / (avgdiff / 2) * 100).where(avgdiff != 0, 0.0)
    nb = (c - o).abs()
    body = (nb > nb.rolling(10).mean() / 3).to_numpy()
    gb, rb = (c > o).to_numpy(), (c < o).to_numpy()
    ls, lr = float(p["limitsmi"]), float(p["limitrsi"])
    sv, rv = smi.to_numpy(), rsi.to_numpy()
    with np.errstate(invalid="ignore"):
        up = ((sv < -ls) | (rv < lr)) & rb & body
        dn = ((sv > ls) | (rv > 100 - lr)) & gb & body
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if (pos == 1 and gb[i] and body[i]) or (pos == -1 and rb[i] and body[i]):
            new = 0
        if up[i]:
            new = 1
        if dn[i]:
            new = -1
        tgt[i] = new
        pos = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
