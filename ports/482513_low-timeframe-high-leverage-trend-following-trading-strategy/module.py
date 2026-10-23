"""Hourly bars: the close crossing over the EMA 9 with RSI 14 over 50 on volume over 1.5 x its 50-bar average goes long, crossing under with RSI under 50 goes short; each trade gets a 1.3 % stop and a 2.6 % target from the signal close; reversing.
Port of FMZ strategy #482513 "Low Timeframe High Leverage Trend Following Trading Strategy" (Low Timeframe Leverage Strategy (LTF Lev 40x)).

FMZ source id: 482513

Source
    https://www.fmz.com/strategy/482513 (PineScript v5, FMZ last modified 2025-02-18 18:20:06).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 91-134), EMA 9; RSI 14 vs 50; volume SMA 50 x 1.5; SL 1.3 %, RR 2
    long_condition = crossover(close, ema9) and rsi > 50 and vol_spike -> entry Long, exit("Take Profit/Stop Loss", "Long", limit = close + 2 x 1.3 %, stop = close x 0.987)
    short_condition = crossunder(close, ema9) and rsi < 50 and vol_spike -> entry Short, exit(same id, "Short", ...)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on signal bars only, as levels from that close: ported as fractions of the
      fill, exact (1e-6 floor). Both sides share one exit id, but the calls only happen on their own
      signal bars (which never coincide), so each trade keeps its own bracket until the opposite entry
      reverses it. The "40x" leverage is in the title only. REVERSAL INTENDED. No sizing code. Stop
      module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket at the signal close as fractions of the fill.
    2 generic: PASS, EMA 9 crossings with RSI and volume-spike filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code (leverage named in the title only).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x its SMA 50; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482513_close_ema9_cross_rsi_volume_spike_1_3pct_rr2_1h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl": [0.013, 0.02],
    "rr": [2.0, 1.5],
}
DEFAULT_PARAMS = {"ema_len": 9, "sl": 0.013, "rr": 2.0, "vol_mult": 1.5}


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
    c, v = bars_df["close"], bars_df["volume"]
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    r = _rsi(c, 14)
    spike = v > v.rolling(50).mean() * float(p["vol_mult"])
    buy = (c > e) & (c.shift(1) <= e.shift(1)) & (r > 50) & spike
    sell = (c < e) & (c.shift(1) >= e.shift(1)) & (r < 50) & spike
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o
    sl, tp = float(p["sl"]), float(p["sl"]) * float(p["rr"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - k * (1 - sl))
            .mask(sf, k * (1 + sl) - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, k * (1 + tp) - 1)
            .mask(sf, 1 - k * (1 - tp)))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
