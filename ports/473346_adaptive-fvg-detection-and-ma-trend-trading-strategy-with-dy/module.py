"""Two-bar reversal candles beyond the last fair-value gap, with the SMA 20 trend, daily bars: a bullish reversal closing over the gap's top above the SMA buys with a 2 % stop under the signal close and the 50-bar high as target. The bearish mirror's short carries a buy limit at the 50-bar high, above the market, so it closes at its own fill open: it is sent as the long's exit (as #452827).
Port of FMZ strategy #473346 "Adaptive-FVG-Detection-and-MA-Trend-Trading-Strategy-with-Dynamic-Resistance-基于时适-FVG-检测与移动平均趋势的动态阻力交易策略" (SMC FVG Entry Strategy with Retest).

FMZ source id: 473346

Source
    https://www.fmz.com/strategy/473346 (PineScript v5, FMZ last modified 2024-11-29 14:50:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-169), stop 2 %; resistance = highest(high, 50); FVG timeframe "60"; SMA 20
    change(time("60")) -> bull gap: low > high[2] and close[1] > high[2] -> fvgLow = low[2], fvgHigh = high;  bear gap: high < low[2] and close[1] < low[2] -> fvgLow = low, fvgHigh = high[2];  bullish reversal and close > fvgHigh and close > sma -> entry Long, exit(limit = highest(high, 50), stop = close x 0.98);  bearish mirror and close < sma -> entry Short, exit(limit = highest(high, 50), stop = close x 1.02)

Interpretation choices (Pine rules in SURVEY_README.md)
    * time("60") on daily bars changes on every bar, so the gap test runs on every bar; the gap levels
      are kept from the last gap (a loop) and "filled" stays true after the first gap. The long's
      levels come from the signal bar (stop 2 % under its close, target its 50-bar high, which includes
      that bar) and are sent as fractions of the fill open; a level at or through it is marketable and
      closed one bar late (as #458256). The short's take-profit is a buy limit at the 50-bar high, never
      under the signal close, so it is marketable at the fill (unless the open gaps over it) and the short closes at its own fill
      open: that side is no trade, and its signal is the long's exit (as #452827). A repeat long signal
      re-sends the bracket from its own bar: the opening levels are kept (mark trailing_stop_pending).
      Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, gap-retest reversal candles with an SMA filter and a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent stop stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_473346_fvg_reversal_candle_sma20_high50_target_long"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_pct": [0.02, 0.04],
    "lookback": [50, 100],
    "ma_period": [20, 50],
}
DEFAULT_PARAMS = {"stop_pct": 0.02, "lookback": 50, "ma_period": 20}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _signals(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    hv, lv, cv = (x.to_numpy(dtype=float) for x in (h, lo, c))
    m = len(cv)
    fh, fl = np.full(m, np.nan), np.full(m, np.nan)
    top, bot = np.nan, np.nan
    for i in range(m):
        if i >= 2:
            if lv[i] > hv[i - 2] and cv[i - 1] > hv[i - 2]:
                bot, top = lv[i - 2], hv[i]
            elif hv[i] < lv[i - 2] and cv[i - 1] < lv[i - 2]:
                bot, top = lv[i], hv[i - 2]
        fh[i], fl[i] = top, bot
    fh, fl = pd.Series(fh, index=c.index), pd.Series(fl, index=c.index)
    ma = c.rolling(int(p["ma_period"])).mean()
    bull = (c > o) & (c.shift(1) < o.shift(1)) & (c > fh) & (c > ma)
    bear = (c < o) & (c.shift(1) > o.shift(1)) & (c < fl) & (c < ma)
    lvl_sl = c * (1 - float(p["stop_pct"]))
    lvl_tp = h.rolling(int(p["lookback"])).max()
    return bull, bear, lvl_sl, lvl_tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, bear, lvl_sl, lvl_tp = _signals(bars_df, p)
    o = bars_df["open"]
    through = (lvl_sl.shift(1) >= o) | (lvl_tp.shift(1) <= o)   # marketable at the fill
    lx = (bear | (le.shift(1, fill_value=False) & through)) & ~le
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, bear, lvl_sl, lvl_tp = _signals(bars_df, p)
    o = bars_df["open"]
    sl_f = 1 - lvl_sl.shift(1) / o
    tp_f = lvl_tp.shift(1) / o - 1
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
