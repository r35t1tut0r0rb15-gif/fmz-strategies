"""Open / close SMA 8 crosses on the three-times-higher (nine-day) timeframe with a smoothed ADX above 13, always in,
three-day bars.
Port of FMZ strategy #482420 "开盘收盘均线交叉结合ADX动态指标的量化交易策略-Opening-and-Closing-Moving-Average-Crossover-Strategy-with-ADX-Dynamic-Indicator" (Open Close Cross Strategy R5.1).

FMZ source id: 482420

Source
    https://www.fmz.com/strategy/482420 (PineScript v6, FMZ last modified 2025-02-18 13:35:54).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 96-221), alternate resolution x 3 (9D on the 3D chart), basis "SMMA"
(= ta.sma here), length 8, ADX 14 > 13, SL / TP points 0 (off)
    close / open series = sma(close, 8) / sma(open, 8) requested on 9D with lookahead_on
    plusDM = max(high - high[1], 0), minusDM = max(low[1] - low, 0), then each zeroed unless larger than the other
    (plusDM first); DI = rma(DM, 14) / rma(atr(14), 14) x 100; adx = rma(dx, 14)
    crossover(closeAlt, openAlt) and adx > 13 -> entry long; crossunder and adx > 13 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * request.security(..., lookahead_on) on the higher timeframe reads each 9-day bar's final value on history (a
      look-ahead). House rule (#490787): only the last COMPLETED 9-day block is used (from the first chart bar of the
      next block), as #482785. Nine-day and three-day blocks are broker-day dates from 1970-01-01 (decision owed, as
      #426509).
    * The DM zeroing is sequential as written (minusDM compared with the already-zeroed plusDM); the true range is
      ATR 14 smoothed again by RMA 14 (as written). The 10000-bar window covers all history; SL / TP are off.
    * Entries reverse (REVERSAL INTENDED); always in. Signal module, no stops. FREQ = "3D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the higher timeframe without look-ahead.
    2 generic: PASS, SMAs of opens and closes and an ADX variant.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in three- and nine-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482420_open_close_sma_cross_htf9_adx_3d"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3D"  # backtest header period: 3d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "use_res": [True, False],
    "adx_filter": [13.0, 20.0],
}
DEFAULT_PARAMS = {"use_res": True, "int_res": 3, "basis_len": 8, "adx_len": 14, "adx_filter": 13.0}
CHART_DAYS = 3


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
    return _multiday(raw_1m_df, days=CHART_DAYS)


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


def _series(bars_df, p):
    n = int(p["basis_len"])
    if not p["use_res"]:
        return bars_df["close"].rolling(n).mean(), bars_df["open"].rolling(n).mean()
    k = CHART_DAYS * int(p["int_res"])
    key = np.asarray((broker_day(bars_df.index) - pd.Timestamp("1970-01-01")).days // k)
    g = bars_df.assign(_key=key).groupby("_key", sort=True).agg(open=("open", "first"), close=("close", "last"))
    cs, os_ = g["close"].rolling(n).mean(), g["open"].rolling(n).mean()
    pos = np.searchsorted(g.index.to_numpy(), key, side="left") - 1     # the block completed before this one
    ok = pos >= 0
    c_alt, o_alt = np.full(len(key), np.nan), np.full(len(key), np.nan)
    c_alt[ok], o_alt[ok] = cs.to_numpy()[pos[ok]], os_.to_numpy()[pos[ok]]
    return pd.Series(c_alt, index=bars_df.index), pd.Series(o_alt, index=bars_df.index)


def _adx(bars_df, n):
    h, lo = bars_df["high"], bars_df["low"]
    pdm = (h - h.shift(1)).clip(lower=0).fillna(0.0)
    mdm = (lo.shift(1) - lo).clip(lower=0).fillna(0.0)
    pdm = pdm.where(pdm > mdm, 0.0)
    mdm = mdm.where(mdm > pdm, 0.0)
    str_ = _rma(_atr(bars_df, n), n)
    pdi, mdi = _rma(pdm, n) / str_ * 100, _rma(mdm, n) / str_ * 100
    dx = (pdi - mdi).abs() / (pdi + mdi) * 100
    return _rma(dx, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ca, oa = _series(bars_df, p)
    strong = _adx(bars_df, int(p["adx_len"])) > p["adx_filter"]
    long_e = ((ca > oa) & (ca.shift(1) <= oa.shift(1)) & strong).astype(bool)
    short_e = ((ca < oa) & (ca.shift(1) >= oa.shift(1)) & strong).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
