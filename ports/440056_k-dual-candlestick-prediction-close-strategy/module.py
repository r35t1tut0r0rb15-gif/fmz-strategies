"""Two-candle 30-minute projection against the daily close, broker days: when the two 30-minute candles before the day's last one share a colour, the projected close extends the later one by its body, otherwise
it is that candle's close; a projection above the daily close holds a long, below it a short; reversing.
Port of FMZ strategy #440056 "双K线预测闭合策略Dual-Candlestick-Prediction-Close-Strategy" (Predict Next Candle Close Strategy).

FMZ source id: 440056

Source
    https://www.fmz.com/strategy/440056 (PineScript v5, FMZ last modified 2024-01-26 10:58:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 167-201), 30-minute open[1] / close[1] / open[2] / close[2] via security on the daily chart
    open1 / close1 / open2 / close2 = security("30", open[1] / close[1] / open[2] / close[2]);  predicted = same colour ? close1 +/- body1 : close1
    predicted > close -> entry Buy;  predicted < close -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * A lower time frame requested from a daily chart returns its last bar inside the chart bar (as
      #436765): the [1] and [2] values are the 30-minute bars just before the broker day's last one,
      built from the module's minutes and counted from the broker day's start. A same-side entry while
      in the position is ignored. strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; lower-time-frame values from the day's last bar.
    2 generic: PASS, candle colours and a projected close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440056_two_candle_30m_projection_daily"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ltf": ["30min", "60min"],
}
DEFAULT_PARAMS = {"ltf": "30min"}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    day_lab = bars.index
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    b = _resample(df, str(p["ltf"]))
    o1, c1, o2, c2 = b["open"].shift(1), b["close"].shift(1), b["open"].shift(2), b["close"].shift(2)
    same_up = (c1 > o1) & (c2 > o2)
    same_dn = (c1 < o1) & (c2 < o2)
    pred = (c1 + (c1 - o1)).where(same_up | same_dn, c1)
    bl = broker_day(b.index)
    last = ~bl.duplicated(keep="last")                    # the broker day's last bar of that size
    v = pd.Series(pred.to_numpy()[last], index=bl[last])
    bars["pred"] = v.reindex(day_lab).to_numpy()
    return bars


def simulate(bars_df, **params):
    c = bars_df["close"].to_numpy(dtype=float)
    pr = bars_df["pred"].to_numpy(dtype=float)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pr[i] > c[i]:
            pos = 1
        elif pr[i] < c[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
