"""MACD crosses above the signal with the close above EMA 20, long only, with a 2 ATR ratcheting stop, closed on the
MACD cross down, 2-hour bars.
Port of FMZ strategy #483072 "动态波动率止损的趋势动量交易策略-Dynamic-Volatility-Based-Stop-Loss-Trend-Momentum-Trading-Strategy" (MACD + ATR Dynamic Stop-Loss Strategy).

FMZ source id: 483072

Source
    https://www.fmz.com/strategy/483072 (PineScript v5, FMZ last modified 2025-02-21 11:39:56).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 97-142), MACD 12 / 26 / 9, EMA 20, ATR 14, SL 1 ATR, trail 2 ATR (on)
    buy = crossover(macd, signal) and close > ema20: stopLoss = close - 1 ATR, trailing = close - 2 ATR; entry long
    while long: trailing = max(trailing, close - 2 ATR); stop = trailing; exit(stop = stop)
    sell = crossunder(macd, signal) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * While held the stop is replaced by the trailing level before any exit is placed, so the 1 ATR stop is never
      used. The trailing level ratchets on closes minus each bar's own 2 ATR: not expressible by the house trail (its
      volatility trail is the best price minus the CURRENT ATR and may retreat), so the port fixes the stop at entry
      as 2 ATR / close of the signal bar (shifted one bar inside stops(), re-based on the fill) and marks
      trailing_stop_pending.
    * The sell close is an exit signal (never on a buy bar). Long only; the source has no shorts.
    * Stop module: portfolio_kwargs {} (D4). Stops on 2-hour bars: coarse_bar_stop. FREQ = "2h" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the ratchet fixed at entry (marked).
    2 generic: PASS, MACD, an EMA and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the stop ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483072_macd_cross_ema20_long_atr_ratchet"
FAMILY = "macd"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_mult": [2.0, 3.0],
    "ema_len": [20, 50],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "atr_len": 14, "trail_mult": 2.0, "ema_len": 20}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    buy = ((macd > sig) & (macd.shift(1) <= sig.shift(1)) & (c > ema)).astype(bool)
    sell = ((macd < sig) & (macd.shift(1) >= sig.shift(1)) & ~buy).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return buy, sell, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["trail_mult"] * a}


def portfolio_kwargs(**params):
    return {}
