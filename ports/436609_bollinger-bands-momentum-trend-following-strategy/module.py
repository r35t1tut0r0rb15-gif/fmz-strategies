"""Hourly bars: a close at or above the upper Bollinger band (20 x 2) above the WMA 99 goes long, closed at or under the lower band; a close at or under the lower band below the WMA goes short, closed at or above the upper band; a stop 2 ATR 14 from the entry; reversing.
Port of FMZ strategy #436609 "Bollinger Bands Momentum Trend Following Strategy" (Bollinger Band | Trend Following (sosacur01)).

FMZ source id: 436609

Source
    https://www.fmz.com/strategy/436609 (PineScript v5, FMZ last modified 2023-12-26 11:21:10).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 242-422), MA WMA 99; BB 20 x 2; volume filter off; ATR 14, stop 2 x ATR; risk 2 % of equity
    long_entry = close > wma(99) and close >= upper -> entry Long;  long_exit = close <= lower -> close Long;  short_entry = close < wma and close <= lower -> entry Short;  short_exit = close >= upper
    sl := entry price - 2 atr(14) when the position changes -> exit(stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The volume filter is off (v_trigger = true), so volume is not used. The stop is set when the
      position changes, from the fill price and the ATR at that bar; the port takes the ATR up to the
      signal bar (known at the fill open) as a fraction of the fill (as #434677). The entries are sent as
      the conditions fire (an entry while in the same side adds nothing); a lower-band close without the
      MA filter closes the long. REVERSAL INTENDED. The risk-based size is sizing. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop from the fill.
    2 generic: PASS, Bollinger breakouts with a WMA trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity x 2 % / (2 x ATR 14), commission 0.2 %, not ported.
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

NAME = "fmz_436609_bb20_breakout_wma99_atr_stop_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bb_len": [20, 50],
    "ma_len": [99, 200],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 2.0, "ma_len": 99, "atr_len": 14, "atr_mult": 2.0}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    ma = _wma(c, int(p["ma_len"]))
    le = (c > ma) & (c >= up)
    se = (c < ma) & (c <= dn)
    lx = (c <= dn) & ~se
    sx = (c >= up) & ~le
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, o = (bars_df[k] for k in ("high", "low", "close", "open"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = _rma(tr, int(p["atr_len"]))
    sl_f = (float(p["atr_mult"]) * atr).shift(1) / o      # the ATR up to the signal bar, known at the fill open
    return {"sl_stop": sl_f.where(sl_f > 0)}


def portfolio_kwargs(**params):
    return {}
