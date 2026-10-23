"""Broker days: a bar whose high is under the low of two bars earlier (the script's "bullish FVG") on volume over 1.5 x its 20-day average with a body above its 20-bar average and the EMA 50 above the EMA 200 goes long; the mirror (low above the high of two bars earlier, EMA 50 under EMA 200) goes short; each trade gets a 1.2 ATR 14 stop and a 2 ATR target from the signal close; reversing.
Port of FMZ strategy #482850 "高频价格失衡区域动量交易策略基于指数均线和ATR动态止盈止损-High-Frequency-Fair-Value-Gap-Momentum-Trading-Strategy-with-EMA-and-ATR-Based-Dynamic-Exit" (Effective FVG Strategy - Forex).

FMZ source id: 482850

Source
    https://www.fmz.com/strategy/482850 (PineScript v5, FMZ last modified 2025-02-20 15:18:11).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 107-151), EMA 50 / 200; volume SMA 20 x 1.5; body vs its SMA 20; FVG low[2] > high / high[2] < low; ATR 14; TP 2, SL 1.2 ATR
    fvgUp = low[2] > high[0];  validBullFVG = fvgUp and highVolume and strongImbalance and ema50 > ema200 -> entry Long, exit(limit = close + 2 atr, stop = close - 1.2 atr)
    fvgDown = high[2] < low[0];  validBearFVG = fvgDown and ... and ema50 < ema200 -> entry Short, exit(limit = close - 2 atr, stop = close + 1.2 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "bullish" gap is a gap DOWN (the current high under the low two bars back) and the "bearish"
      one a gap up, as written (weird case): it buys sharp drops in an uptrend and sells sharp rises in a
      downtrend. The bracket is sent on signal bars, as levels from that close: ported as fractions of the
      fill, exact (1e-6 floor). REVERSAL INTENDED. 10 % of equity is sizing. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-day bars: coarse_bar_stop. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, three-bar gaps on high volume with a trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only ("Forex" in the title)).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482850_fvg_gap_volume_imbalance_trend_atr_bracket_reversal"
FAMILY = "gap"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [2.0, 3.0],
    "sl_atr": [1.2, 2.0],
}
DEFAULT_PARAMS = {"tp_atr": 2.0, "sl_atr": 1.2}


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
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def simulate(bars_df, **params):
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    e50, e200 = c.ewm(span=50, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    body = (c - o).abs()
    common = (v > v.rolling(20).mean() * 1.5) & (body > body.rolling(20).mean())
    buy = (lo.shift(2) > h) & common & (e50 > e200)
    sell = (h.shift(2) < lo) & common & (e50 < e200)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    atr = _atr(bars_df, 14)
    sl_d, tp_d = float(p["sl_atr"]) * atr, float(p["tp_atr"]) * atr
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - sl_d).shift(1) / o)
            .mask(sf, (c + sl_d).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (c + tp_d).shift(1) / o - 1)
            .mask(sf, 1 - (c - tp_d).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
