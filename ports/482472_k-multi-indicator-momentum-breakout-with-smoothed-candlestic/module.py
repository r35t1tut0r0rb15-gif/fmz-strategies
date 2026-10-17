"""Green Heikin-Ashi bars closing above the upper Bollinger band (20, 2) with RSI 14 above 50 go long; a red Heikin-Ashi
bar or RSI at 70 closes the trade, long only, six-hour bars.
Port of FMZ strategy #482472 "多指标动量突破结合平滑K线交易策略-Multi-Indicator-Momentum-Breakout-with-Smoothed-Candlestick-Trading-Strategy" (Bollinger Bands + RSI + Heikin Ashi Breakout).

FMZ source id: 482472

Source
    https://www.fmz.com/strategy/482472 (PineScript v6, FMZ last modified 2025-02-18 15:38:21).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 156-193), BB 20 / 2, RSI 14 (70)
    haClose = ohlc4; haOpen = na(haOpen[1]) ? (open + close) / 2 : (haOpen[1] + haClose[1]) / 2
    haClose > haOpen and close > upper and rsi > 50 -> entry long
    haClose < haOpen or rsi >= 70 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close is written after the entry: it acts on the position held at the bar's start and never undoes an
      entry on that bar (#430850). State machine; exits emitted only on going flat.
    * Long only. Signal module, no stops. FREQ = "6h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Heikin-Ashi colour, Bollinger bands and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482472_ha_green_bb_upper_break_rsi_long"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "6h"  # backtest header period: 6h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_mult": [2.0, 1.5],
    "rsi_exit": [70.0, 80.0],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 2.0, "rsi_len": 14, "rsi_exit": 70.0}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ha_c = ((o + h + lo + c) / 4).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    ha_o = np.full(m, np.nan)
    for i in range(m):
        ha_o[i] = (ov[i] + cv[i]) / 2 if i == 0 or np.isnan(ha_o[i - 1]) else (ha_o[i - 1] + ha_c[i - 1]) / 2
    n = int(p["bb_len"])
    upper = c.rolling(n).mean() + p["bb_mult"] * c.rolling(n).std(ddof=0)
    rsi = _rsi(c, int(p["rsi_len"]))
    buy = (ha_c > ha_o) & ((c > upper) & (rsi > 50)).to_numpy()
    sell = (ha_c < ha_o) | (rsi >= p["rsi_exit"]).to_numpy()
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        start = pos
        if buy[i] and pos != 1:
            le[i], pos = True, 1
        if sell[i] and start == 1 and pos == 1:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
