"""RSI 2 crossing up through 5 above the SMA 200, broker days, long only: the cross goes long and a close over the SMA 5 closes.
Port of FMZ strategy #488288 "RSI动量反转短期趋势跟踪策略与移动平均线聚合-RSI-Momentum-Reversal-Short-Term-Trend-Following-Strategy-with-Moving-Average-Confluence" (_Rerun's Dip Bonanza).

FMZ source id: 488288

Source
    https://www.fmz.com/strategy/488288 (PineScript v5, FMZ last modified 2025-03-26 16:13:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 199-250), RSI 2 / 5; SMA 200; exit SMA 5; emergency stop 0 % (off); capital 100000
    close > sma200 and crossover(rsi2, 5) -> entry Long;  long and close > sma5 -> close Long;  stop (off by default)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close is tested only while a long is held (from the bar after the entry signal), so a loop
      follows the position: a signal while held is refused and does not block that bar's close, as
      written. The emergency stop is off (0 %). Long only. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, short-RSI dip entries in an uptrend with an SMA exit.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: strategy(): capital 100000 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488288_rsi2_dip_cross5_sma200_sma5_exit_long"
FAMILY = "rsi_threshold"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsiBuyLevel": [5.0, 10.0],
    "exitMaLen": [5, 10],
}
DEFAULT_PARAMS = {"rsiBuyLevel": 5.0, "exitMaLen": 5, "rsiLength": 2, "trendMaLen": 200}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsiLength"]))
    lvl = float(p["rsiBuyLevel"])
    sig = ((c > c.rolling(int(p["trendMaLen"])).mean()) & (r > lvl) & (r.shift(1) <= lvl)).to_numpy()
    ex = (c > c.rolling(int(p["exitMaLen"])).mean()).to_numpy()
    m = len(sig)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend = 0, 0
    for i in range(m):
        if pend == 1:
            pos = 1
        elif pend == -1:
            pos = 0
        pend = 0
        if pos == 0 and sig[i]:
            le[i], pend = True, 1
        elif pos == 1 and ex[i]:
            lx[i], pend = True, -1
    false = pd.Series(False, index=c.index)
    return pd.Series(le, index=c.index), pd.Series(lx, index=c.index), false, false.copy()


def portfolio_kwargs(**params):
    return {}
