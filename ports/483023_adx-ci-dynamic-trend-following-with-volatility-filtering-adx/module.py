"""SMA 9 / 21 crosses traded only with ADX 7 above 20 and the choppiness index 7 at or below 50, every cross closing
the opposite position, daily (broker-day) bars.
Port of FMZ strategy #483023 "动态趋势跟踪与波动率过滤策略基于ADX与CI双重确认的均线交叉系统-Dynamic-Trend-Following-with-Volatility-Filtering-ADX-and-CI-Dual-Confirmed-Moving-Average-Crossover-System" (MA9/MA21 Cross with ADX & CHOP Filter).

FMZ source id: 483023

Source
    https://www.fmz.com/strategy/483023 (PineScript v6, FMZ last modified 2025-02-21 09:33:38).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 105-182), SMA 9 / 21, ADX 7 > 20, CHOP 7 <= 50
    tr, +DM, -DM with nz() on the previous bar; atr = rma(tr, 7); adx = rma(dx, 7)
    chop = 100 x log(sum tr 7 / (highest high 7 - lowest low 7)) / log(7) (0 when the range is 0)
    long cross and filter -> entry long; short cross and filter -> entry short; short cross -> close long; long cross
    -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The DMI is the source's own (nz() on the first bar), as written.
    * The closes come after the entries: they act on the position held at the bar's start and never undo that bar's
      entry (as #430850); a cross without the filter only closes the opposite position. Target-position state
      machine, exits only on going flat. Entries reverse (REVERSAL INTENDED). No stops.
    * Daily bars are broker days (17:00 America/New_York) stamped with their first minute (as #430984). FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages, ADX and the choppiness index.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (initial capital quoted in original_sizing.txt).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483023_sma9_21_cross_adx_chop_filter_1d"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_thresh": [20.0, 25.0],
    "chop_thresh": [50.0, 61.8],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "adx_len": 7, "adx_thresh": 20.0, "chop_len": 7, "chop_thresh": 50.0}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc, ph, pl = c.shift(1).fillna(0.0), h.shift(1).fillna(0.0), lo.shift(1).fillna(0.0)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    up, dn = h - ph, pl - lo
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    n = int(p["adx_len"])
    atr = _rma(tr, n)
    pdi, mdi = 100 * _rma(pdm, n) / atr, 100 * _rma(mdm, n) / atr
    adx = _rma(100 * (pdi - mdi).abs() / (pdi + mdi), n)
    k = int(p["chop_len"])
    rng = h.rolling(k).max() - lo.rolling(k).min()
    chop = (100 * np.log(tr.rolling(k).sum() / rng) / np.log(k)).where(rng != 0, 0.0)
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    x_up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    x_dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    ok = ((adx > p["adx_thresh"]) & (chop <= p["chop_thresh"])).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if x_up[i] and ok[i]:
            pos = 1
        if x_dn[i] and ok[i]:
            pos = -1
        if x_dn[i] and start == 1 and pos == 1:
            pos = 0
        if x_up[i] and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
