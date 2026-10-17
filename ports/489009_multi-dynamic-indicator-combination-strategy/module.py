"""SuperTrend (22, 3, wicks) flips with Bollinger-band take-profit closes, two-day bars: a SuperTrend flip up goes long
(closing a short), a flip down goes short; a close at or above the upper band closes a long, at or below the lower
band closes a short.
Port of FMZ strategy #489009 "多重动态指标组合策略-Multi-Dynamic-Indicator-Combination-Strategy" (Combined BB & New SuperTrend Strategy).

FMZ source id: 489009

Source
    https://www.fmz.com/strategy/489009 (PineScript v6, FMZ last modified 2025-04-01 10:12:19).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 130-246), BB 20 x 2 (SMA basis), SuperTrend ATR 22 x 3 on hl2, wicks on
    longStop = hl2 - 3 ATR, ratcheted up while low[1] > its previous value (doji4price keeps it); shortStop mirrored
    dir flips up when high > previous shortStop, down when low < previous longStop
    flip up -> close short, entry long;  flip down -> close long, entry short
    long held and close >= upperBB -> close;  short held and close <= lowerBB -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SuperTrend as written (wicks: highs / lows; a four-price doji keeps the previous stop; nz seeds).
    * The band closes are written after the entries: they act on the position held at the bar's start (as #430850).
      Entries reverse (REVERSAL INTENDED).
    * The basis MA type defaults to SMA (the VWMA option, a volume weighting, is not used: check 8).
    * FREQ = "2D" from the backtest header (period 2d): two-day bars from broker days in fixed blocks counted from
      1970-01-01 (block phase: decision owed), as #426509.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR stops and bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8; the VWMA option of the basis input is not used).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489009_supertrend_flip_bb_take_profit_2d"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "st_length": [22, 10],
    "st_mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"bb_length": 20, "bb_mult": 2.0, "st_length": 22, "st_mult": 3.0, "wicks": True}


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


def _supertrend_dir(bars_df, n, mult, wicks):
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    atr = mult * _atr(bars_df, n).to_numpy(dtype=float)
    src = (h + lo) / 2
    hp, lp = (h, lo) if wicks else (c, c)
    doji = (o == c) & (o == lo) & (o == h)
    m = len(c)
    d = np.ones(m, dtype=np.int8)
    ls_prev = ss_prev = np.nan
    cur = 1
    for i in range(m):
        ls, ss = src[i] - atr[i], src[i] + atr[i]
        lsp = ls if np.isnan(ls_prev) else ls_prev
        ssp = ss if np.isnan(ss_prev) else ss_prev
        if ls > 0:
            ls = lsp if doji[i] else (max(ls, lsp) if (i > 0 and lp[i - 1] > lsp) else ls)
        else:
            ls = lsp
        if ss > 0:
            ss = ssp if doji[i] else (min(ss, ssp) if (i > 0 and hp[i - 1] < ssp) else ss)
        else:
            ss = ssp
        if cur == -1 and hp[i] > ssp:
            cur = 1
        elif cur == 1 and lp[i] < lsp:
            cur = -1
        d[i] = cur
        ls_prev, ss_prev = ls, ss
    return d


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = p["bb_mult"] * c.rolling(n).std(ddof=0)
    up_b, lo_b = (basis + dev).to_numpy(), (basis - dev).to_numpy()
    d = _supertrend_dir(bars_df, int(p["st_length"]), float(p["st_mult"]), bool(p["wicks"]))
    prev_d = np.concatenate(([d[0]], d[:-1]))
    buy, sell = (d == 1) & (prev_d == -1), (d == -1) & (prev_d == 1)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if buy[i]:
            pos = 1
        if sell[i]:
            pos = -1
        if start == 1 and pos == 1 and cv[i] >= up_b[i]:
            pos = 0
        if start == -1 and pos == -1 and cv[i] <= lo_b[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
