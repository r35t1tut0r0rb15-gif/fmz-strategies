"""Price outside the (undisplaced) Ichimoku cloud with the MACD histogram side, a weekly close-above-SMA-50 trend and
wide Bollinger bands, with a 1.5 ATR stop, two-day bars: close above both spans, histogram above 0, the last completed
week's close above its 50-week SMA and BB width above 2 % goes long; the mirror (week below) goes short.
Port of FMZ strategy #483044 "动态多指标优化趋势追踪策略-Dynamic-Multi-Indicator-Optimized-Trend-Following-Strategy" (Momentum Edge Strategy - 1D BTC Optimized).

FMZ source id: 483044

Source
    https://www.fmz.com/strategy/483044 (PineScript v6, FMZ last modified 2025-02-21 10:46:28).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 89-131), ATR 14 x 1.5, BB width threshold 0.02
    spanA = (tenkan 9 + kijun 26) / 2, spanB = donchian mid 52 (no displacement); higherTF = security("W", close >
    sma(close, 50)); bbWidth = 4 stdev 20 / sma 20
    long = close above both spans and hist > -0.05 and higherTF and bbWidth > 0.02 -> entry + exit(stop = close - 1.5 ATR)
    short = close below both spans and hist < 0 and not higherTF and bbWidth > 0.02 -> mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The weekly trend is the last COMPLETED week (house request.security rule): weeks of broker days (17:00
      America/New_York) built from the port's own bars, each two-day block assigned by its first session; close >
      SMA 50 of the weekly closes.
    * hist > -0.05 is a price-unit threshold: about 0 against ETH's two-day MACD histogram (tens of USD), so it is read
      as hist > 0 (criterion 2).
    * The stop: with bbWidth above the threshold at every signal, the stop is the ATR branch, 1.5 ATR / close of the
      signal bar (shifted one bar inside stops(), re-based on the fill). Every bar in the condition re-places it: mark
      trailing_stop_pending; the port keeps the entry's stop. No target.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Two-day bars are blocks of broker-day
      dates from 1970-01-01 (decision owed, as #426509); FREQ = "2D" from the backtest header; coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; completed weekly values; the stop from the signal bar (marked).
    2 generic: PASS, Ichimoku spans, MACD, Bollinger width, a weekly SMA and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the stop ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in two-day blocks and weeks; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483044_cloud_macd_weekly_trend_bbwidth_2d"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 2.5],
    "bbw_min": [0.02, 0.05],
}
DEFAULT_PARAMS = {"atr_len": 14, "atr_mult": 1.5, "bbw_min": 0.02, "week_sma": 50}


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


def _multiday(raw_1m_df, days=2):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


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


def _mid(h, lo, n):
    return (h.rolling(n).max() + lo.rolling(n).min()) / 2


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    span_a = (_mid(h, lo, 9) + _mid(h, lo, 26)) / 2
    span_b = _mid(h, lo, 52)
    above = (c > span_a) & (c > span_b)
    below = (c < span_a) & (c < span_b)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    wk = pd.DatetimeIndex(broker_day(bars_df.index)).to_period("W")
    weekly = pd.Series(c.to_numpy(), index=wk).groupby(level=0).last()
    up_w = (weekly > weekly.rolling(int(p["week_sma"])).mean()).astype(float)
    up_w[weekly.rolling(int(p["week_sma"])).mean().isna()] = np.nan
    prev_w = up_w.shift(1).reindex(wk).to_numpy()            # the last completed week
    htf_up = pd.Series(prev_w == 1.0, index=c.index)
    htf_dn = pd.Series(prev_w == 0.0, index=c.index)
    basis = c.rolling(20).mean()
    bbw = 4 * c.rolling(20).std(ddof=0) / basis
    wide = bbw > p["bbw_min"]
    long_e = (above & (hist > 0) & htf_up & wide).astype(bool)
    short_e = (below & (hist < 0) & htf_dn & wide).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": a}


def portfolio_kwargs(**params):
    return {}
