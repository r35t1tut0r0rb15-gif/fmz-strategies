"""Donchian breakout longs with an ATR stop and a trailing close, 1-minute bars, long only: a high crossing over the previous 20-bar high enters long (only the first breakout since the last downside breakout); the stop sits 2 ATR
under the signal close; a low crossing under the 4-bar high of closes minus 3.5 ATR closes the long, as long as the close rule's order ids still reach the entry.
Port of FMZ strategy #436650 "基于ATR和突破的ETF交易策略An-ATR-and-Breakout-based-ETF-Trading-Strategy" (ETF tradedr (ATR breakout)).

FMZ source id: 436650

Source
    https://www.fmz.com/strategy/436650 (PineScript v4, FMZ last modified 2023-12-26 16:05:55).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 187-293), lookback 20, ATR 14, stop 2 ATR, trailing 3.5 ATR over 4 bars, max sequel trades 1, long on / short off
    long_condition = crossover(high, highest(high, 20)[1]);  short_condition = crossunder(low, lowest(low, 20)[1]);  count_open_longs = prior + 1 on long_condition, reset to 0 on short_condition
    entry "Long<count>" when long_condition and count <= 1 and trade_long, with exit(stop = close - 2 ATR);  trailing_SL_long_signal = crossunder(low, (highest(close, 4) - 3.5 ATR)[1]) -> close "Long<count>", "Long<count-1>", -2, -4 ... -9 (the id count-3 is skipped)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the stop is already an ATR amount, re-based as sl_stop = 2 x ATR / signal close (shifted one
      bar inside stops(), re-based on the fill). The count of long breakouts since the last downside
      breakout (which also resets it when shorts are off) lets only the first one trade; the trailing
      close names the entry ids count, count-1, count-2, count-4 ... count-9, so it reaches the entry id
      only when the count minus the entry id is one of those offsets (a count of exactly 3 above the
      entry id, or more than 9, cannot close it); that is ported as written. The take profit distance
      is unused. The short side is off by default and not ported. Long only. Stop module:
      portfolio_kwargs {} (driver D4). The percent-of-equity size with pyramiding 100 is sizing. FREQ =
      "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, channel breakout with ATR levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and pyramiding stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436650_donchian_atr_stop_trail"
FAMILY = "donchian_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [20, 40],
    "atr_sl_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"lookback": 20, "atr_len": 14, "atr_sl_mult": 2.0, "trail_mult": 3.5, "trail_lookback": 4,
                  "max_sequel": 1}
CLOSE_OFFSETS = (0, 1, 2, 4, 5, 6, 7, 8, 9)       # the ids the trailing close names (count - offset)


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["lookback"])
    hh1 = h.rolling(n).max().shift(1)
    ll1 = lo.rolling(n).min().shift(1)
    long_c = ((h > hh1) & (h.shift(1) <= hh1.shift(1))).to_numpy()
    short_c = ((lo < ll1) & (lo.shift(1) >= ll1.shift(1))).to_numpy()
    atr = _atr(bars_df, p["atr_len"])
    tl = c.rolling(int(p["trail_lookback"])).max() - float(p["trail_mult"]) * atr
    trail_sig = ((lo < tl.shift(1)) & (lo.shift(1) >= tl.shift(2))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    cnt = 0
    entry_id = None
    max_seq = float(p["max_sequel"])
    for i in range(m):
        if long_c[i]:
            cnt += 1
        if short_c[i]:
            cnt = 0
        if long_c[i] and cnt <= max_seq:
            le[i] = True
            entry_id = cnt
        if trail_sig[i] and entry_id is not None and (cnt - entry_id) in CLOSE_OFFSETS:
            lx[i] = True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = float(p["atr_sl_mult"]) * _atr(bars_df, p["atr_len"]) / c
    return {"sl_stop": f.shift(1)}


def portfolio_kwargs(**params):
    return {}
