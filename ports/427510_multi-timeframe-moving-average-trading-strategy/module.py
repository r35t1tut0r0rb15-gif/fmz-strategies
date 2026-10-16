"""CM Ultimate MA on weekly bars: the SMA 20 turning down against its value 2 weeks earlier goes short,
turning back up goes long (always in the market after the first turn).
Port of FMZ strategy #427510 "Multi-Timeframe Moving Average Trading Strategy".

FMZ source id: 427510

Source
    https://www.fmz.com/strategy/427510 (PineScript v2, FMZ last modified 2023-09-21 20:45:38).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 198-262), current resolution on, SMA 20 (type 1), smoothing 2
    out1 = security(ticker, timeframe.period, avg) = avg; ma_down = out1 < out1[2]
    chk = ma_down ? 1 : 0 (the red colour); chk turns 0 -> entry long; chk turns 1 -> entry short
    strategy.exit("RsiLE") / ("RsiSE") with no levels (no effect)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Use Current Chart Resolution" is on: security(..., timeframe.period, x) is x itself.
    * `ma_type` is the source's type input: 1 SMA, 2 EMA, 3 WMA, 4 Hull, 6 RMA, 7 TEMA; 5 (VWMA)
      uses volume and is not ported (check 8). The optional second MA only plots.
    * The strategy.exit calls give no level: they never act. REVERSAL INTENDED.
    * Weekly bars as worker A's 7-day ports: calendar weeks (Monday-Sunday) of broker-day dates,
      each stamped with its first session start. FREQ = "1W" (backtest header period 7d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: ND427510 (3 members, best partner #438047, Jaccard 0.764); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8); the VWMA type is excluded.
Session open: broker day (17:00 America/New_York, DST by the zone); weeks of broker-day dates; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427510_cm_ultimate_ma_weekly"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1W"  # backtest header period: 7d (weeks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10, 40],
    "ma_type": [1, 2],
}
DEFAULT_PARAMS = {"length": 20, "ma_type": 1, "smoothe": 2}
MA_TYPES = (1, 2, 3, 4, 6, 7)   # 5 (vwma) uses volume: not ported


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


def _weekly(raw_1m_df):
    """Calendar weeks (Monday-Sunday) of the broker-day dates (as worker A's 7-day ports), each stamped
    with the session start of its first broker day."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray(day - pd.to_timedelta(day.weekday, unit="D"))
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _rma(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _ma(x, n, t):
    if t == 1:
        return x.rolling(n).mean()
    if t == 2:
        return x.ewm(span=n, adjust=False).mean()
    if t == 3:
        return _wma(x, n)
    if t == 4:
        return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(round(np.sqrt(n))))
    if t == 6:
        return _rma(x, n)
    if t == 7:
        e1 = x.ewm(span=n, adjust=False).mean()
        e2 = e1.ewm(span=n, adjust=False).mean()
        return 3 * (e1 - e2) + e2.ewm(span=n, adjust=False).mean()
    raise ValueError(f"ma_type {t} not ported (choices {MA_TYPES})")


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _weekly(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    out = _ma(bars_df["close"], int(p["length"]), int(p["ma_type"]))
    chk = (out < out.shift(int(p["smoothe"]))).astype(int).to_numpy()
    valid = out.notna().to_numpy() & out.shift(int(p["smoothe"])).notna().to_numpy()
    m = len(chk)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(1, m):
        if valid[i] and valid[i - 1]:
            if chk[i - 1] == 1 and chk[i] == 0:
                pos = 1
            elif chk[i - 1] == 0 and chk[i] == 1:
                pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
