"""Hourly bars: the close crossing over the upper band (VWMA 200 of hlc3 plus 3 standard deviations of hlc3) goes long, crossing under the lower band goes short; a close 2 % beyond the fill price, or RSI 14 under 30 for a long (over 70 for a short), closes the trade at the next open; reversing.
Port of FMZ strategy #489134 "Fibonacci Bollinger Bands with RSI Dynamic Take Profit Strategy" (Fibonacci Bollinger Bands with RSI Dynamic Take Profit Strategy).

FMZ source id: 489134

Source
    https://www.fmz.com/strategy/489134 (PineScript v5, FMZ last modified 2025-04-02 09:37:00).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 188-237), VWMA 200 of hlc3; 3 x stdev 200 of hlc3 (bands at 1 x dev); RSI 14 (30 / 70); profit target 2 % from position_avg_price; 100 % of equity
    buySignal = crossover(close, basis + dev) -> entry Long;  sellSignal = crossunder(close, basis - dev) -> entry Short
    long: close >= position_avg_price x 1.02 or rsi < 30 -> close Long;  short: close <= position_avg_price x 0.98 or rsi > 70 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are close tests against the fill price with market closes, so they fill at the next open
      (exact in the signals). The closes act only on a position the bar's entries leave unchanged; an
      opposite entry reverses. The RSI exits close a long on weakness and a short on strength. The
      "Fibonacci" bands are plain VWMA bands (one multiplier). REVERSAL INTENDED. 100 % of equity is
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked target from the fill and RSI closes in the signals.
    2 generic: PASS, volume-weighted band breakouts with a fixed-percent target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the VWMA 200 weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489134_vwma200_band_breakout_pct_target_rsi_exit_1h_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [3.0, 2.0],
    "tp_pct": [2.0, 3.0],
}
DEFAULT_PARAMS = {"length": 200, "mult": 3.0, "tp_pct": 2.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    n = int(p["length"])
    src = (h + lo + c) / 3
    basis = (src * v).rolling(n).sum() / v.rolling(n).sum()
    dev = float(p["mult"]) * src.rolling(n).std(ddof=0)
    up_b, lo_b = basis + dev, basis - dev
    buy = ((c > up_b) & (c.shift(1) <= up_b.shift(1))).to_numpy()
    sell = ((c < lo_b) & (c.shift(1) >= lo_b.shift(1))).to_numpy()
    r = _rsi(c, 14).to_numpy()
    on, cn = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tp = float(p["tp_pct"]) / 100
    m = len(cn)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt, held_prev, fp = 0, 0, np.nan
    for i in range(m):
        held = tgt                          # the position after this bar's open
        if held != 0 and held != held_prev:
            fp = on[i]                      # a new trade filled at this open
        new = held
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == held:
            if held == 1 and (cn[i] >= fp * (1 + tp) or r[i] < 30):
                new = 0
            elif held == -1 and (cn[i] <= fp * (1 - tp) or r[i] > 70):
                new = 0
        if new != held and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif held == 1:
                lx[i] = True
            else:
                sx[i] = True
            tgt = new
        held_prev = held
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
