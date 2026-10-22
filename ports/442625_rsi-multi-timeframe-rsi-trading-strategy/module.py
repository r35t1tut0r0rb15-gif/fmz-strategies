"""RSI 14 on 15-minute, 1-hour and 4-hour bars read at the end of each day, daily bars: the three RSIs rising in order (15m > 1h > 4h, 4h over 30) go long, falling in order (4h under 70) go short; the 15m RSI
crossing back past the 1h RSI closes; reversing.
Port of FMZ strategy #442625 "多时间框架RSI交易策略Multi-Timeframe-RSI-Trading-Strategy" (Multi-Timeframe RSI Strategy).

FMZ source id: 442625

Source
    https://www.fmz.com/strategy/442625 (PineScript v5, FMZ last modified 2024-02-23 12:24:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 143-190), RSI 14 on 15 / 60 / 240 minutes via request.security on a daily chart
    buy = rsiM15 > rsiH1 and rsiH1 > rsiH4 and rsiH4 > 30 -> entry Buy;  sell = rsiH1 < rsiH4 and rsiM15 < rsiH1 and rsiH4 < 70 -> entry Sell
    rsiM15 < rsiH1 -> close Buy;  rsiM15 > rsiH1 -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The three requests are lower time frames than the daily chart: each returns its last bar inside
      the day (as #436765), built from minutes in precompute; the 15-minute and 1-hour bars are UTC
      bars inside the broker day, the 4-hour bars are counted from the broker day's start (six per day).
      Ported in call order with one position at a time; a close after a reversing entry leaves the
      reversal standing. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; lower-time-frame values ending with the daily bar.
    2 generic: PASS, multi-time-frame RSI ordering.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND438798 (2 members, best partner #438798, Jaccard 0.747); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442625_three_tf_rsi_order_daily_reversal"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "floor": [30, 40],
}
DEFAULT_PARAMS = {"rsi_len": 14, "floor": 30}


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
    n = int(p["rsi_len"])
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    for col, freq in (("rsi15", "15min"), ("rsi60", "1h")):
        cl = df["close"].resample(freq, label="left", closed="left").last().dropna()
        r = _rsi(cl, n)
        bars[col] = r.groupby(broker_day(cl.index)).last().reindex(bars.index).to_numpy()   # the day's last bar
    # 4-hour bars counted from each broker day's start (17:00 America/New_York): six per day
    ny = df.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)
    blk = np.asarray((ny - ny.normalize()) // pd.Timedelta(minutes=240))
    c4 = df["close"].groupby([lab, blk]).last()
    r4 = _rsi(pd.Series(c4.to_numpy(), index=pd.RangeIndex(len(c4))), n).to_numpy()
    day4 = c4.index.get_level_values(0)
    last4 = pd.Series(r4, index=day4)
    last4 = last4[~day4.duplicated(keep="last")]
    bars["rsi240"] = last4.reindex(bars.index).to_numpy()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a, b, c4 = bars_df["rsi15"], bars_df["rsi60"], bars_df["rsi240"]
    fl = float(p["floor"])
    buy = ((a > b) & (b > c4) & (c4 > fl)).to_numpy()
    sell = ((b < c4) & (a < b) & (c4 < 100.0 - fl)).to_numpy()
    xb = (a < b).to_numpy()
    xs = (a > b).to_numpy()
    m = len(a)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if xb[i] and held == 1 and new == 1:
            new = 0
        if xs[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
