"""The gap between an RSI 42 and an RSI 21, daily bars: the RSI 42 more than 5 points under the RSI 21 goes long, more than 5 points over it goes short; each side closes 5 days after the last bar its condition held, or on the opposite condition; reversing.
Port of FMZ strategy #451490 "RSI双重差分策略-Dual-RSI-Differential-Strategy" (Dual RSI Differential - Strategy [presentTrading]).

FMZ source id: 451490

Source
    https://www.fmz.com/strategy/451490 (PineScript v5, FMZ last modified 2024-05-15 10:41:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 83-170), RSI 21 / 42; level 5; hold 5 days; TP / SL off ('None'); 10 % of equity, commission 0.1 %, slippage 1
    diff = rsi42 - rsi21;  diff < -5 -> entry Long, longEntryTime = time;  long and (time - longEntryTime >= 5 days or diff > 5) -> close Long
    diff > 5 -> entry Short, shortEntryTime = time;  short and (time - shortEntryTime >= 5 days or diff < -5) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry time is reset on EVERY bar the condition holds, also while that side is already held,
      so the hold counts from the last such bar. The long block runs before the short block: a long
      meeting diff > 5 is closed and then reversed into the short (one reversal); a short meeting
      diff < -5 is reversed by the long entry, and the short block's close then finds the trade
      already reversed and does nothing. The day count uses the broker-day labels of the bars (Pine's
      daily time is the session start). TPSL 'None' places no bracket. REVERSAL INTENDED. The 10 % of
      equity, commission and slippage are stored. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI-difference extremes with a time exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity sizing, commission and slippage stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451490_dual_rsi_difference_hold_days_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [21, 14],
    "long_len": [42, 28],
    "diff_lvl": [5, 10],
}
DEFAULT_PARAMS = {"short_len": 21, "long_len": 42, "diff_lvl": 5.0, "hold_days": 5}


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
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    diff = _rsi(c, int(p["long_len"])) - _rsi(c, int(p["short_len"]))
    lvl = float(p["diff_lvl"])
    lc = (diff < -lvl).to_numpy()
    sc = (diff > lvl).to_numpy()
    day = ((broker_day(bars_df.index) - pd.Timestamp("1970-01-01")) // pd.Timedelta(days=1)).to_numpy()
    hold = int(p["hold_days"])
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, lt, st = 0, None, None
    for i in range(m):
        cur = pos
        if lc[i]:
            lt = day[i]
            if cur != 1:
                cur = 1
        if ((lt is not None and day[i] - lt >= hold) or sc[i]) and pos == 1 and cur == 1:
            cur = 0                          # close Long acts on the long held into the bar
        if sc[i]:
            st = day[i]
            if cur != -1:
                cur = -1
        if ((st is not None and day[i] - st >= hold) or lc[i]) and pos == -1 and cur == -1:
            cur = 0                          # a short already reversed this bar is left alone
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
