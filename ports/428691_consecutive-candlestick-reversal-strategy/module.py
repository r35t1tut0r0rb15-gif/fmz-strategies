"""Two-candle reversal with RVI, 3-day bars: from flat, two big red candles in a row with the RVI signal
above the RVI go long; two big green candles with the signal below go short. A long closes when the
RVI rises above its signal, a short when it falls below.
Port of FMZ strategy #428691 "Consecutive Candlestick Reversal Strategy".

FMZ source id: 428691

Source
    https://www.fmz.com/strategy/428691 (PineScript v4, FMZ last modified 2023-10-08 13:56:39).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 186-278), minimum body 42 ticks, RVI 55
    RVI = sum(swma(close - open), 55) / sum(swma(high - low), 55); signal = swma(RVI) (1-2-2-1 / 6)
    long (flat): two red bodies >= 42 ticks and signal > RVI; close long when RVI > signal
    short (flat): two green bodies >= 42 ticks and signal < RVI; close short when RVI < signal

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the body size in ticks becomes `body_atr` x Wilder ATR(14) (4.2 USD on 3-day BTC
      with a 0.1 tick is about 0.002 ATR: nearly any body; judgement before any backtest).
    * Entries need no open trade. Opposite entries cannot occur. The date switch is off.
    * 3-day bars are blocks of broker days counted from 1970-01-01 (as worker A's 3-day ports),
      stamped with the session start. FREQ = "3D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, tick body size -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428691_two_candle_rvi_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3D"  # backtest header period: 3d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "body_atr": [0.002, 0.3],
    "rvi_period": [55, 20],
}
DEFAULT_PARAMS = {"body_atr": 0.002, "rvi_period": 55, "atr_length": 14}


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


def _multiday(raw_1m_df, weekly=False, days=1):
    """Multi-day bars built from broker days: calendar weeks (Monday-Sunday) of the broker-day
    dates when weekly, else blocks of `days` broker-day dates counted from 1970-01-01. Each bar
    is stamped with the session start of its first broker day."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    if weekly:
        key = np.asarray(day - pd.to_timedelta(day.weekday, unit="D"))
    else:
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


def _swma(x):
    return (x + 2 * x.shift(1) + 2 * x.shift(2) + x.shift(3)) / 6


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=3)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["rvi_period"])
    num = _swma(c - o).rolling(n).sum()
    den = _swma(h - lo).rolling(n).sum()
    rvi = (num / den).where(den != 0, 0.0).where(den.notna())
    sig = _swma(rvi)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    big = (c - o).abs() >= p["body_atr"] * _rma(tr, int(p["atr_length"]))
    red, green = o > c, o < c
    two_red = (big & red & big.shift(1, fill_value=False) & red.shift(1, fill_value=False)).to_numpy()
    two_green = (big & green & big.shift(1, fill_value=False) & green.shift(1, fill_value=False)).to_numpy()
    s_gt, s_lt = (sig > rvi).to_numpy(), (sig < rvi).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if start == 1 and s_lt[i]:              # RVI > signal
            pos = 0
        if start == -1 and s_gt[i]:             # RVI < signal
            pos = 0
        if start == 0:
            if two_red[i] and s_gt[i]:
                pos = 1
            elif two_green[i] and s_lt[i]:
                pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
