"""RSI 14 of the day's last 15-minute bar against the 1-hour and 4-hour RSIs, broker days: the 15-minute RSI above both goes long, under both goes short; a long closes when it drops under the 1-hour RSI, a
short when it rises above it; reversing.
Port of FMZ strategy #438798 "多时间框架RSI策略Multi-Timeframe-RSI-Strategy" (Multi-Timeframe RSI).

FMZ source id: 438798

Source
    https://www.fmz.com/strategy/438798 (PineScript v5, FMZ last modified 2024-01-15 14:15:32).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 113-162), RSI 14 on 15 / 60 / 240 minutes (on a 1-day chart)
    rsiM15 / rsiH1 / rsiH4 = security(tickerid, "15" / "60" / "240", rsi(close, 14));  m15 > h1 and m15 > h4 -> entry Buy;  m15 < h1 and m15 < h4 -> entry Sell;  m15 < h1 -> close Buy;  m15 > h1 -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 15-minute, 1-hour and 4-hour values requested from a daily chart are the day's LAST bar of each
      size (as #436765), counted from the broker day's start (17:00 America/New_York); the RSI 14 runs on
      each such series. The close of the opposite side on an entry bar acts on a trade the reversing
      entry already closed, so the reversal stands (as #438020). strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. Daily bars are broker days, stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSIs on three bar sizes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND438798 (2 members, best partner #442625, Jaccard 0.747); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438798_mtf_rsi_15_60_240"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "tf_mid": [60, 30],
}
DEFAULT_PARAMS = {"rsi_len": 14, "tf_mid": 60, "tf_fast": 15, "tf_slow": 240}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    ny = df.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)
    since = ny - ny.normalize()
    for key in ("tf_fast", "tf_mid", "tf_slow"):
        # bars of that size counted from each broker day's start (17:00 America/New_York)
        mos = since // pd.Timedelta(minutes=int(p[key]))
        cl = df["close"].groupby([lab, np.asarray(mos)]).last()
        r = _rsi(cl, int(p["rsi_len"]))
        day = r.index.get_level_values(0)
        r = r[~day.duplicated(keep="last")]              # the day's last bar of that size
        r.index = r.index.get_level_values(0)
        bars["rsi_" + key] = r
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    f = bars_df["rsi_tf_fast"].to_numpy(dtype=float)
    md = bars_df["rsi_tf_mid"].to_numpy(dtype=float)
    sl = bars_df["rsi_tf_slow"].to_numpy(dtype=float)
    m = len(f)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if f[i] > md[i] and f[i] > sl[i] and i + 1 < m:
            if pos != 1:
                le[i], pos = True, 1
        elif f[i] < md[i] and f[i] < sl[i] and i + 1 < m:
            if pos != -1:
                se[i], pos = True, -1
        elif pos == 1 and f[i] < md[i]:
            lx[i], pos = True, 0
        elif pos == -1 and f[i] > md[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
