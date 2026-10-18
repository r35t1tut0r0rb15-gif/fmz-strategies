"""Buy-only average cross with re-entry, broker days: the SMA 20 crossing over the SMA 30 with the weekly CCI over 100 or the ADX over 25 goes
long; a close under the SMA 100 closes it; when flat, a close over all three averages with the weekly CCI over 100 buys again.
Port of FMZ strategy #435867 "Dynamic Re entry Buy only Strategy" (Buy Only Strategy with Dynamic Re-Entry and Exit).

FMZ source id: 435867

Source
    https://www.fmz.com/strategy/435867 (PineScript v5, FMZ last modified 2023-12-19 13:56:55).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 154-200), SMA 20 / 30 / 100; weekly CCI 14; ADX 14 (directional index of hlc3 changes) over 25
    long_condition = crossover(sma20, sma30) and (weekly_cci > 100 or adx > 25);  exit = close < sma100;  re_entry = close > sma20 and close > sma30 and close > sma100 and weekly_cci > 100
    entry long (long_condition);  close long (exit);  flat and re_entry -> entry long;  long and close < sma100 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The weekly CCI is request.security(tickerid, "W", cci(close, 14)) without lookahead: the CCI of
      the last COMPLETED week (weeks of broker days, Monday to Sunday), built inside simulate and
      shifted one week. The ADX is the script's own: +DM / -DM from changes of hlc3, a Wilder RMA of
      the true range and of the moves, DX over their sum. The orders of one bar are filled in the
      script's call order at the next open (entry, close, re-entry only when the position at the bar's
      open was flat, close). Long only. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the weekly value from completed weeks.
    2 generic: PASS, average cross, CCI and a directional index.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_435867_sma_cross_weekly_cci_reentry_long"
FAMILY = "cci_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "adx_threshold": [25, 20],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 30, "third": 100, "cci_period": 14, "adx_length": 14, "adx_threshold": 25}


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
    wk = pd.Series(bars.index, index=bars.index)
    bars["wk"] = pd.PeriodIndex(wk.values, freq="W-SUN").asi8     # week number (Monday to Sunday) of the broker-day label
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _rma(s, n):
    return s.ewm(alpha=1 / n, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    # weekly CCI of the last completed week
    wk = bars_df["wk"]
    wclose = c.groupby(wk.values).last()
    n = int(p["cci_period"])
    ma = wclose.rolling(n).mean()
    md = wclose.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        wcci = (wclose - ma) / (0.015 * md)
    wcci_prev = wcci.shift(1)                                   # the last completed week
    weekly_cci = pd.Series(wcci_prev.reindex(wk.values).to_numpy(), index=c.index)
    # the script's directional index
    hlc3 = (h + lo + c) / 3
    chg = hlc3.diff()
    plus = chg.where(chg > 0, 0.0).where(chg.notna())
    minus = (-chg).where(chg < 0, 0.0).where(chg.notna())
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    L = int(p["adx_length"])
    trur = _rma(tr, L)
    plus_di, minus_di = _rma(plus, L) / trur * 100, _rma(minus, L) / trur * 100
    s = plus_di + minus_di
    dx = ((plus_di - minus_di).abs() / s * 100).where(s != 0, 0.0)
    adx = _rma(dx, L)
    fast = c.rolling(int(p["fast"])).mean()
    slow = c.rolling(int(p["slow"])).mean()
    third = c.rolling(int(p["third"])).mean()
    cci_ok = weekly_cci > 100
    long_cond = ((fast > slow) & (fast.shift(1) <= slow.shift(1)) & (cci_ok | (adx > float(p["adx_threshold"])))).fillna(False).to_numpy()
    exit_cond = (c < third).fillna(False).to_numpy()
    re_entry = ((c > fast) & (c > slow) & (c > third) & cci_ok).fillna(False).to_numpy()
    m = len(long_cond)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    ops = []
    for i in range(m):
        if i > 0:                            # fills at this bar's open, in the order the script sent them
            for op in ops:
                if op == "eL" and pos <= 0:
                    pos = 1
                elif op == "cL" and pos == 1:
                    pos = 0
        held[i] = pos
        ops = []
        if long_cond[i]:
            ops.append("eL")
        if exit_cond[i]:
            ops.append("cL")
        if pos == 0 and re_entry[i]:
            ops.append("eL")
        if pos > 0 and exit_cond[i]:
            ops.append("cL")
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
