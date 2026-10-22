"""SMA 9 / 21 crossings filtered by a hand-built ADX 7 over 20 and Choppiness 7 at or under 50, broker days: a filtered up-cross goes long and a filtered down-cross goes short; any down-cross closes a long and any up-cross closes a short; reversing.
Port of FMZ strategy #483023 "动态趋势跟踪与波动率过滤策略基于ADX与CI双重确认的均线交叉系统-Dynamic-Trend-Following-with-Volatility-Filtering-ADX-and-CI-Dual-Confirmed-Moving-Average-Crossover-System" (MA9/MA21 Cross with ADX & CHOP Filter).

FMZ source id: 483023

Source
    https://www.fmz.com/strategy/483023 (PineScript v6, FMZ last modified 2025-02-21 09:33:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-182), SMA 9 / 21; ADX / DI 7 (rma); threshold 20; CHOP 7, maximum 50; capital 10000
    tr = max(high - low, |high - nz(close[1])|, |low - nz(close[1])|);  adx = rma(dx, 7) from rma(+DM, 7) / rma(tr, 7);  chop = 100 log(sum(tr, 7) / (highest(high, 7) - lowest(low, 7))) / log(7)
    crossover(sma9, sma21) and adx > 20 and chop <= 50 -> entry Long;  crossunder and filter -> entry Short;  crossunder -> close Long;  crossover -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The true range and directional moves read nz() of the previous bar, so the very first bar uses 0
      for it, as written. CHOP is 0 when the 7-bar range is 0. A close on the bar of an entry is masked by
      the entry; a filtered entry on the other side reverses (REVERSAL INTENDED). The CHOP offset is not
      applied (as the source says). The capital is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with ADX / Choppiness filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483023_sma9_21_cross_adx7_20_chop7_50_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_thresh": [20.0, 25.0],
    "chop_thresh": [50.0, 61.8],
}
DEFAULT_PARAMS = {"adx_thresh": 20.0, "chop_thresh": 50.0, "ma_fast": 9, "ma_slow": 21, "adx_length": 7,
                  "chop_length": 7}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1, fill_value=0.0)                     # nz(close[1])
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    up = h - h.shift(1, fill_value=0.0)
    dn = lo.shift(1, fill_value=0.0) - lo
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    n = int(p["adx_length"])
    atr = _rma(tr, n)
    pdi, mdi = 100 * _rma(pdm, n) / atr, 100 * _rma(mdm, n) / atr
    adx = _rma(100 * (pdi - mdi).abs() / (pdi + mdi), n)
    k = int(p["chop_length"])
    rng = h.rolling(k).max() - lo.rolling(k).min()
    chop = (100 * np.log(tr.rolling(k).sum() / rng.where(rng != 0)) / np.log(k)).where(rng != 0, 0.0)
    f, s = c.rolling(int(p["ma_fast"])).mean(), c.rolling(int(p["ma_slow"])).mean()
    xu = (f > s) & (f.shift(1) <= s.shift(1))
    xd = (f < s) & (f.shift(1) >= s.shift(1))
    filt = (adx > float(p["adx_thresh"])) & (chop <= float(p["chop_thresh"]))
    le, se = xu & filt, xd & filt
    return le, xd & ~se & ~le, se, xu & ~le & ~se


def portfolio_kwargs(**params):
    return {}
