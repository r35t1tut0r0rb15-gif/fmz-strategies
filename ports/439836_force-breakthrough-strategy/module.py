"""Connors RSI 2 snap-backs, 30-minute bars: above the EMA 200, a close at or under the EMA 10 as the RSI 2 leaves the under-5 zone goes long; below the EMA 200, a close above the EMA 10 as the RSI leaves the
over-95 zone goes short; a long closes above the EMA 10, a short at or under it.
Port of FMZ strategy #439836 "Force Breakthrough Strategy" (Estrategia Larry Connors).

FMZ source id: 439836

Source
    https://www.fmz.com/strategy/439836 (PineScript v5, FMZ last modified 2024-01-24 11:25:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 146-256), longs and shorts on; "SMA" 1 = EMA 10, "SMA" 2 = EMA 200 (the code uses ta.ema); RSI 2, levels 5 / 95; start 2000 (open)
    long = close > ema200 and not close > ema10 and rsi[1] < 5 and not rsi < 5 and not long;  short = not close > ema200 and close > ema10 and rsi[1] > 95 and not rsi > 95 and not short
    if long and close > ema10: close long;  if short and not close > ema10: close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The averages are EMAs although named SMA. The closes test the position held at the bar close,
      after the entries: a close of the side just reversed out of meets no position and the reversal
      stands (as #438020). strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "30min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA sides and RSI 2 zone exits.
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

NAME = "fmz_439836_connors_rsi2_snapback_ema10_200"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_os": [5, 10],
    "sma_2_length": [200, 100],
}
DEFAULT_PARAMS = {"rsi_os": 5, "sma_2_length": 200, "sma_1_length": 10, "rsi_length": 2}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e1 = c.ewm(span=int(p["sma_1_length"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["sma_2_length"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    os_, ob = float(p["rsi_os"]), 100 - float(p["rsi_os"])
    above1, up_tr = (c > e1).to_numpy(), (c > e2).to_numpy()
    ros, rob = (r < os_), (r > ob)
    lc3 = (ros.shift(1, fill_value=False) & ~ros).to_numpy()
    sc3 = (rob.shift(1, fill_value=False) & ~rob).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if up_tr[i] and not above1[i] and lc3[i] and pos != 1:
            new = 1
        if not up_tr[i] and above1[i] and sc3[i] and pos != -1:
            new = -1
        if pos == 1 and above1[i] and new == 1:
            new = 0
        if pos == -1 and not above1[i] and new == -1:
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
