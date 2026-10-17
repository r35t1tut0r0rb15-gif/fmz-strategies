"""Ichimoku cloud regime with MACD, RSI and stochastic filters: trend entries beside the cloud, range reversals inside
it, each with a stop 2 ATR beyond the signal bar's extreme, two-day bars.
Port of FMZ strategy #482841 "动态自适应多时间周期趋势跟踪与震荡反转复合策略-Dynamic-Adaptive-Multi-Timeframe-Trend-Following-and-Range-Reversal-Hybrid-Strategy" (Refined Ichimoku with MACD and RSI Strategy).

FMZ source id: 482841

Source
    https://www.fmz.com/strategy/482841 (PineScript v6, FMZ last modified 2025-02-20 14:48:41).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 104-177), Ichimoku 9 / 26 / 52, MACD 12 / 26 / 9 (SMA signal), RSI 14,
stochastic 14 smoothed 3 / 3, ATR 14 x 2
    spanA = (conversion + base) / 2, spanB = 52-bar mid (not displaced, as written)
    above = close >= spanA and close >= spanB; below mirrored; near = spanB < close < spanA
    trend long = above and rsi > 55 and macd hist > 0 and K > D; trend short mirrored (rsi < 45)
    range long = near and rsi < 30 and K < 20; range short = near and rsi > 70 and K > 80
    each entry with exit(stop = low - 2 ATR) (short: high + 2 ATR) placed on the signal bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "Stochastic RSI" is ta.stoch of the close (as written), smoothed by SMA 3 (K) and SMA 3 (D).
    * The stop is placed with the entry from the signal bar: (close - low + 2 ATR) / close for longs,
      (high - close + 2 ATR) / close for shorts, picked by the signal's side, shifted one bar inside stops() and
      re-based on the fill (house rule). A later signal of the same entry while held re-places the stop at the new
      bar's level: fixed at entry, mark trailing_stop_pending (as #491506).
    * Trend and range entries of one side share the position (pyramiding 1); the two sides cannot fall on one bar.
      Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Two-day bars are blocks of
      broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-placed stop fixed at entry (marked).
    2 generic: PASS, rolling mid-points, MACD, RSI, stochastic and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the stop via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in two-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482841_ichimoku_regime_macd_rsi_stoch_atr_stop_2d"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [2.0, 3.0],
    "base_len": [26, 20],
}
DEFAULT_PARAMS = {"conv_len": 9, "base_len": 26, "span_b_len": 52, "macd_fast": 12, "macd_slow": 26, "macd_sig": 9,
                  "rsi_len": 14, "stoch_len": 14, "k_smooth": 3, "d_smooth": 3, "atr_len": 14, "atr_mult": 2.0}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _mid(bars_df, n):
    return (bars_df["high"].rolling(n).max() + bars_df["low"].rolling(n).min()) / 2


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    a = (_mid(bars_df, int(p["conv_len"])) + _mid(bars_df, int(p["base_len"]))) / 2
    b = _mid(bars_df, int(p["span_b_len"]))
    above, below = (c >= a) & (c >= b), (c <= a) & (c <= b)
    near = (c > b) & (c < a)
    macd = c.ewm(span=int(p["macd_fast"]), adjust=False).mean() - c.ewm(span=int(p["macd_slow"]), adjust=False).mean()
    hist = macd - macd.rolling(int(p["macd_sig"])).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    n = int(p["stoch_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["k_smooth"])).mean()
    d = k.rolling(int(p["d_smooth"])).mean()
    long_e = (above & (rsi > 55) & (hist > 0) & (k > d)) | (near & (rsi < 30) & (k < 20))
    short_e = (below & (rsi < 45) & (hist < 0) & (k < d)) | (near & (rsi > 70) & (k > 80))
    return long_e.astype(bool), short_e.astype(bool)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k_atr = p["atr_mult"] * _atr(bars_df, int(p["atr_len"]))
    long_e, _ = _signals(bars_df, p)
    sl = ((c - lo + k_atr) / c).where(long_e, (h - c + k_atr) / c)   # picked by the signal's side
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
