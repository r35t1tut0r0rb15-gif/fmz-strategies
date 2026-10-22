"""Three red days in a row while ATR 12 is above its 30-day average, broker days, long only from flat: the signal goes long; three green days or 22 bars since the signal close.
Port of FMZ strategy #483676 "Counter Trend Breakout Trading System A Quantitative Strategy Based on Multi Day Price Patterns and Volatility Filtering" (3 Red / 3 Green Strategy with Volatility Check).

FMZ source id: 483676

Source
    https://www.fmz.com/strategy/483676 (PineScript v6, FMZ last modified 2025-02-25 10:49:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 204-255), maximum duration 22; three-green exit on; ATR 12 vs SMA 30 filter; capital 100000
    flat and red[0..2] and atr12 > sma(atr12, 30) -> entry Long, entryBarIndex := bar_index
    long and (green[0..2] or bar_index - entryBarIndex >= 22) -> close Long;  a position closed on this bar -> entryBarIndex := na

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flat gate, the bar count and the reset are followed in a loop as written: an entry signalled on
      the bar a previous trade's close filled has its entryBarIndex cleared by the reset line on that same
      bar, so that trade has no 22-bar limit (only the green-day exit). Long only. The capital is sizing.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, red-day runs with a volatility filter and a bar-count exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital stored, not ported.
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

NAME = "fmz_483676_three_red_days_atr_filter_three_green_or_22_bar_exit_long"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "max_trade_duration": [22, 10],
    "atr_period": [12, 20],
}
DEFAULT_PARAMS = {"max_trade_duration": 22, "atr_period": 12, "atr_avg": 30}


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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    red, green = c < o, c > o
    three_red = (red & red.shift(1, fill_value=False) & red.shift(2, fill_value=False)).to_numpy()
    three_green = (green & green.shift(1, fill_value=False) & green.shift(2, fill_value=False)).to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["atr_period"]))
    avg = atr.rolling(int(p["atr_avg"])).mean()
    atr_ok = ((atr > avg) | ~((atr > 0) & (avg > 0))).to_numpy()     # true while either is not yet positive
    md = int(p["max_trade_duration"])
    m = len(three_red)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = pend_in = pend_out = False
    eb = None
    for i in range(m):
        prev_pos = pos
        if pend_in:
            pos, pend_in = True, False
        if pend_out:
            pos, pend_out = False, False
        if not pos and not pend_in and three_red[i] and atr_ok[i]:
            le[i], pend_in, eb = True, True, i
        dur = (i - eb) if eb is not None else 0
        if pos and not pend_out and (three_green[i] or dur >= md):
            lx[i], pend_out = True, True
        if prev_pos and not pos:
            eb = None                         # the reset line, as written
    false = pd.Series(False, index=c.index)
    return pd.Series(le, index=c.index), pd.Series(lx, index=c.index), false, false.copy()


def portfolio_kwargs(**params):
    return {}
