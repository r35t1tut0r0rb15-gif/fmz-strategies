"""Broker days: a green bar on above-average volume closing over the 5-bar high of two bars back, with the MACD above its signal and above 0, while the bar overlaps the last stored 3-bar fair-value gap, goes long; the bearish mirror goes short; reversing.
Port of FMZ strategy #484579 "量化交易VSA体积分析与MACD动量指标结合公平价值缺口策略-Quantitative-Trading-Strategy-Combining-VSA-Volume-Analysis-MACD-Momentum-Indicator-and-Fair-Value-Gap-Detection" (VSA+MACD+FVG Strategy).

FMZ source id: 484579

Source
    https://www.fmz.com/strategy/484579 (PineScript v5, FMZ last modified 2025-03-03 09:52:54).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 167-250), MACD 12 / 26 / 9; VSA (volume SMA 20, highest(high, 5)[2]); FVG low > high[3] (with a green previous bar) stored in var levels
    vsaBullish = close > open and volume > sma(volume, 20) and close > highest(high, 5)[2];  FVG up: low > high[3] and close[1] > open[1] -> fvgTop := low, fvgBottom := high[3] (down mirrored)
    buySignal = vsaBullish and macd > signal and macd > 0 and high >= fvgBottom and low <= fvgTop and not long -> entry Buy;  sellSignal mirrored and not short -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The same logic as #484089 with the price lookback shifted 2 bars and a 3-bar gap. The gap levels
      start at 0 and keep the latest gap until a new one. The entries skip the side already held; an
      opposite entry reverses. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume-spread breakouts with MACD momentum inside fair-value gaps.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_484579_vsa_macd_fvg3_overlap_reversal"
FAMILY = "gap"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "price_lb": [5, 10],
    "fvg_lb": [3, 2],
}
DEFAULT_PARAMS = {"price_lb": 5, "fvg_lb": 3, "vsa_shift": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _fvg_signals(bars_df, p):
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    vol_ok = v > v.rolling(20).mean()
    n, s, g = int(p["price_lb"]), int(p["vsa_shift"]), int(p["fvg_lb"])
    vsa_b = (c > o) & vol_ok & (c > h.rolling(n).max().shift(s))
    vsa_s = (c < o) & vol_ok & (c < lo.rolling(n).min().shift(s))
    up = ((lo > h.shift(g)) & (c.shift(1) > o.shift(1))).to_numpy()
    dn = ((h < lo.shift(g)) & (c.shift(1) < o.shift(1))).to_numpy()
    hn, ln = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    hg, lg = h.shift(g).to_numpy(dtype=float), lo.shift(g).to_numpy(dtype=float)
    top, bot = np.zeros(len(hn)), np.zeros(len(hn))
    t = b = 0.0
    for i in range(len(hn)):
        if up[i]:
            t, b = ln[i], hg[i]
        elif dn[i]:
            t, b = lg[i], hn[i]
        top[i], bot[i] = t, b
    inside = (hn >= bot) & (ln <= top)
    buy = (vsa_b & (macd > sig) & (macd > 0)).to_numpy() & inside
    sell = (vsa_s & (macd < sig) & (macd < 0)).to_numpy() & inside
    return buy, sell


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell = _fvg_signals(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(buy, index=ix), false, pd.Series(sell, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
