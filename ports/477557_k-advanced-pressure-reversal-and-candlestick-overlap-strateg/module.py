"""3-hour bars: a red candle on volume above its 20-bar average (selling pressure) or a green candle covering the previous coloured candle's body goes long; a green high-volume candle or a red candle covering the previous body goes short (the later short call wins on a bar with both); each trade gets a 20 % target from the signal close and no stop; reversing.
Port of FMZ strategy #477557 "高级压力反转与K线重叠策略Advanced-Pressure-Reversal-and-Candlestick-Overlap-Strategy" (Pressure Reversal & Candle Overlap).

FMZ source id: 477557

Source
    https://www.fmz.com/strategy/477557 (PineScript v5, FMZ last modified 2025-01-06 13:54:56).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 91-132), volume SMA 20; overlap vs the previous non-doji candle (valuewhen ... 1); TP 20 %; qty 0.1
    long = selling_pressure (red and volume > sma(volume, 20)) or green_overlaps_red -> entry Buy Long, exit(limit = close x 1.2)
    short = buying_pressure (green and high volume) or red_overlaps_green -> entry Sell Short, exit(limit = close x 0.8)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Contrarian, as written: high volume on a red bar buys and on a green bar sells. prev_open /
      prev_close are those of the previous coloured candle (valuewhen(green or red, ..., 1)). A green
      high-volume candle that also covers the previous red body makes both calls; the short comes later
      and wins. The target is sent on signal bars as a level from that close: ported as a fraction of the
      fill, exact (1e-6 floor); repeated signals while in the trade re-send it from the new close (not
      followed: trailing_stop_pending). qty 0.1 BTC is sizing. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 3-hour bars: coarse_bar_stop. FREQ = "3h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 20 % target at the signal close as a fraction of the fill.
    2 generic: PASS, contrarian volume-pressure and body-overlap candles.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 0.1 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_477557_pressure_reversal_candle_overlap_20pct_target_3h_reversal"
FAMILY = "candlestick_pattern"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.2, 0.05],
    "vol_len": [20, 50],
}
DEFAULT_PARAMS = {"tp": 0.2, "vol_len": 20}


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


def _prev_when(cond, src):
    """ta.valuewhen(cond, src, 1): src at the second most recent bar (up to now) where cond held."""
    cv, sv = cond.to_numpy(), src.to_numpy(dtype=float)
    out = np.full(len(sv), np.nan)
    last = prev = np.nan
    for i in range(len(sv)):
        if cv[i]:
            prev, last = last, sv[i]
        out[i] = prev
    return pd.Series(out, index=src.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    green, red = c > o, c < o
    coloured = green | red
    po, pcl = _prev_when(coloured, o), _prev_when(coloured, c)
    g_ov = green & (c >= po) & (o <= pcl)
    r_ov = red & (c <= po) & (o >= pcl)
    hv = v > v.rolling(int(p["vol_len"])).mean()
    sell = (green & hv) | r_ov
    buy = ((red & hv) | g_ov) & ~sell      # the later short call wins on a two-sided bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o
    tp = float(p["tp"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, k * (1 + tp) - 1)
            .mask(sf, 1 - k * (1 - tp)))
    return {"tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
