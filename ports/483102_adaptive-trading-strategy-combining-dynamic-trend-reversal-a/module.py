"""A 0.25 % percent-reversal zigzag line with Stochastic 9 / 3, broker days: the close over the zigzag's reversal line with %K under 30 goes long, under it with %K over 70 goes short, each with a 100-tick stop and a 300-tick target from the signal close read as percents; reversing.
Port of FMZ strategy #483102 "Adaptive Trading Strategy Combining Dynamic Trend Reversal and Stochastic Indicator" ([RS]ZigZag Percent Reversal with Stochastic Strategy).

FMZ source id: 483102

Source
    https://www.fmz.com/strategy/483102 (PineScript v5, FMZ last modified 2025-02-27 17:00:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-234), zigzag method MANUAL, 0.25 %; Stochastic K 9, smoothing 3; stop 100 ticks; target 300 ticks
    zigzag: track the high while up (reverse when close <= high track - pivot[1] x 0.25 %) and the low while down (reverse when close >= low track + pivot[1] x 0.25 %);  reverse_line = the current reversal level
    close > reverse_line and k < 30 -> entry Buy + exit(stop = close - 100 ticks, limit = close + 300 ticks);  close < reverse_line and k > 70 -> entry Sell + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The zigzag function is followed as written (the first pivot is na, so the first reversal range is
      0; both direction blocks can run on one bar). The method menu keeps MANUAL (the ATR choices are
      unused).
    * Criterion 2: the bracket is 100 / 300 ticks; on the header's BTC_USDT read at 42000 with a 0.1 tick
      (as #458242) that is 2.381e-04 / 7.143e-04 of the price, taken from the signal close and sent as
      fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256). The conditions are states and repeat while held, each re-sending the bracket from the new
      close; stops() keeps the first: mark trailing_stop_pending (as #434428). An entry on the other side
      reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars:
      mark coarse_bar_stop. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; tick bracket as fractions of the fill.
    2 generic: ADAPT, tick bracket read as fractions at BTC 42000.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483102_zigzag0_25pct_reverse_line_stoch9_tick_bracket_reversal"
FAMILY = "pivot_reversal"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "percent": [0.25, 1.0],
    "k_length": [9, 14],
}
DEFAULT_PARAMS = {"percent": 0.25, "k_length": 9, "k_smoothing": 3, "stop_frac": 2.381e-04,
                  "take_frac": 7.143e-04}


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


def _reverse_line(hv, lv, cv, pct):
    m = len(cv)
    out = np.full(m, np.nan)
    up = None
    ht = lt = pivot = line = np.nan
    for i in range(1, m):
        if up is None:
            up = True
        rr = (0.0 if np.isnan(pivot) else pivot) * pct      # nz(pivot[1]): pivot as it stood after the last bar
        if up:
            lt = np.nan
            if np.isnan(ht):
                ht = hv[i] if hv[i] > hv[i - 1] else hv[i - 1]
            elif hv[i] > ht:
                ht = hv[i]
            line = ht - rr
            if cv[i] <= line:
                pivot, up = ht, False
        if not up:
            ht = np.nan
            if np.isnan(lt):
                lt = lv[i] if lv[i] < lv[i - 1] else lv[i - 1]
            elif lv[i] < lt:
                lt = lv[i]
            line = lt + rr
            if cv[i] >= line:
                pivot, up = lt, True
        out[i] = line
    return out


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    rl = pd.Series(_reverse_line(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                                 float(p["percent"]) / 100), index=c.index)
    n = int(p["k_length"])
    rng = h.rolling(n).max() - lo.rolling(n).min()
    k = (100 * (c - lo.rolling(n).min()) / rng.where(rng > 0)).rolling(int(p["k_smoothing"])).mean()
    le = (c > rl) & (k < 30)
    se = (c < rl) & (k > 70)
    a, b = float(p["stop_frac"]), float(p["take_frac"])
    lvl = {"l_sl": c * (1 - a), "l_tp": c * (1 + b), "s_sl": c * (1 + a), "s_tp": c * (1 - b)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
