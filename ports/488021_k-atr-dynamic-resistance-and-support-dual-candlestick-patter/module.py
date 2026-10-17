"""Engulfing candles inside the 50-bar range with a 1.5 ATR stop and a 3 ATR target, three-day bars: a bullish engulfing
bar closing above the 50-bar low goes long; a bearish engulfing bar closing below the 50-bar high goes short.
Port of FMZ strategy #488021 "动态阻力与支撑的双K线形态ATR风险控制量化交易策略-Dynamic-Resistance-and-Support-Dual-Candlestick-Pattern-ATR-Risk-Management-Quantitative-Trading-Strategy" (Ai ProSR V.1).

FMZ source id: 488021

Source
    https://www.fmz.com/strategy/488021 (PineScript v5, FMZ last modified 2025-03-24 14:24:55).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 165-205), lookback 50, ATR 14 x 1.5, target 2 x the stop
    bullishEngulfing = prev red, green, close > open[1], open < close[1];  buy = it and close > lowest(low, 50)
    sell = bearishEngulfing and close < highest(high, 50)
    entry + exit(stop = close -+ 1.5 ATR, limit = close +- 3 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The windows include the current bar, as written. The bracket is fixed at the signal bar: sl_stop = atr_mult x
      ATR / close, tp_stop = 2 x that, shifted one bar inside stops() and re-based on the fill (house rule).
    * A same-side signal while held re-places the bracket from the new bar: mark trailing_stop_pending; the port keeps
      the entry's bracket.
    * Entries reverse (REVERSAL INTENDED); the two patterns cannot fall on one bar. Stop module: portfolio_kwargs {}
      (D4). Three-day bars are blocks of broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "3D"
      from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, candle patterns, rolling extremes and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in three-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488021_engulfing_in_range_atr_bracket"
FAMILY = "candlestick_pattern"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3D"  # backtest header period: 3d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 2.5],
    "lookback": [50, 20],
}
DEFAULT_PARAMS = {"lookback": 50, "atr_len": 14, "atr_mult": 1.5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=3):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=3)


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["lookback"])
    o1, c1 = o.shift(1), c.shift(1)
    bull = (c1 < o1) & (c > o) & (c > o1) & (o < c1)
    bear = (c1 > o1) & (c < o) & (c < o1) & (o > c1)
    long_e = (bull & (c > lo.rolling(n).min())).astype(bool)
    short_e = (bear & (c < h.rolling(n).max())).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": 2 * sl}


def portfolio_kwargs(**params):
    return {}
