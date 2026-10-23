"""A SuperTrend (1 x ATR 10) around an EMA 7 of a volume-price-trend shadow line, with an EMA 7 of the open as filter, broker days, long only (the direction input allows longs): the close crossing over the SuperTrend line above the open EMA goes long; crossing under it below the open EMA closes.
Port of FMZ strategy #429579 "超趋势V策略Super-Trend-V-Strategy" (Super trend V Strategy version).

FMZ source id: 429579

Source
    https://www.fmz.com/strategy/429579 (PineScript v4, FMZ last modified 2023-10-18 12:35:53).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 148-297), direction long; VPT shadow (28 / 14); EMA length 7 on daily bars; SuperTrend 1 x ATR 10; VWAP TP lines only plotted
    out = VPT shadow line;  vpt = ema(out, 7);  up / down trend of vpt -/+ atr(10), trend flips on the close;  st_line = trend == 1 ? up_trend : down_trend
    buy = crossover(close, st_line) and close > ema(open, 7) -> entry buy;  sell = crossunder(close, st_line) and close < ema(open, 7) -> entry sell (closes the long: allow_entry_in long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.risk.allow_entry_in(long) turns the short entries into closes of the long, so the strategy is
      long only with the sell signal as its exit. The EMA length is 7 on a daily chart (the intraday
      formula is not used). The VPT line adds the bar's spread volume to its running sum (as #428617); a
      zero-range bar gives na there. The VWAP regression TP lines only feed plots. The 2016 .. 2030 window
      is dropped. Long only. The 100 % of equity size and commission are sizing / costs. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend crossings of a volume-price line with an open-EMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, capital 1000, commission 0.075 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the VPT shadow line the SuperTrend is built on; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429579_vpt_shadow_supertrend_open_ema_filter_long"
FAMILY = "supertrend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "st_mult": [1.0, 2.0],
    "st_period": [10, 20],
}
DEFAULT_PARAMS = {"st_mult": 1.0, "st_period": 10, "ema_len": 7}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    hilow = (h - lo) * 100
    sv = (c - o) * 100 * (v / hilow.where(hilow != 0))
    vp = sv + sv.fillna(0.0).cumsum()
    dvp = vp - vp.rolling(14).mean()
    shadow = dvp / dvp.rolling(28).std(ddof=0) * (h - lo).rolling(28).std(ddof=0)
    out = (h + shadow).where(shadow > 0, lo + shadow)
    n = int(p["ema_len"])
    vpt = out.ewm(span=n, adjust=False).mean()
    oe = o.ewm(span=n, adjust=False).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # atr(): first bar high - low
    atr = _rma(tr, int(p["st_period"]))
    k = float(p["st_mult"])
    up_lev, dn_lev = (vpt - k * atr).to_numpy(), (vpt + k * atr).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    st = np.full(m, np.nan)
    ut_p = dt_p = np.nan
    tr_p = np.nan
    for i in range(m):
        c1 = cv[i - 1] if i else np.nan
        ut = max(up_lev[i], ut_p) if c1 > ut_p else up_lev[i]
        dt = min(dn_lev[i], dt_p) if c1 < dt_p else dn_lev[i]
        t = 1.0 if cv[i] > dt_p else (-1.0 if cv[i] < ut_p else (1.0 if np.isnan(tr_p) else tr_p))
        st[i] = ut if t == 1 else dt
        ut_p, dt_p, tr_p = ut, dt, t
    sts = pd.Series(st, index=c.index)
    le = (c > sts) & (pc <= sts.shift(1)) & (c > oe)
    lx = (c < sts) & (pc >= sts.shift(1)) & (c < oe)
    false = pd.Series(False, index=c.index)
    return le, lx & ~le, false, false.copy()


def portfolio_kwargs(**params):
    return {}
