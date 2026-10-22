"""A Madrid ribbon of 18 EMAs (5 to 90) against the EMA 100 with RSI 14 extremes, broker days: 13 or more "green" ribbons with RSI under 30 goes long, 9 or more "red" ribbons with RSI over 70 goes short, each with a 0.5 % target and a 1 % stop from the signal close; reversing.
Port of FMZ strategy #488034 "马德里带状RSI增强型多时框EMA趋势策略-Madrid-Ribbon-RSI-Enhanced-Multi-Timeframe-EMA-Trend-Strategy" (Madrid Ribbon Strategy with Backtesting).

FMZ source id: 488034

Source
    https://www.fmz.com/strategy/488034 (PineScript v5, FMZ last modified 2025-03-24 15:52:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 185-319), EMA 5..90 vs EMA 100; RSI 14; TP 0.5 %, SL 1 %; quantity 100000 / close
    for each ma in 5..90: change = ta.change(ma) (called in the loop);  green: change >= 0 and ma > ma100, or change >= 0 and ma < ma100 (not red);  red: change < 0 and ma > ma100, or change <= 0 and ma < ma100
    count_green >= 13 and rsi < 30 -> entry Buy + exit(limit = close x 1.005, stop = close x 0.99);  count_red >= 9 and rsi > 70 -> entry Sell + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.change sits in maColor, called from one place inside the for loop, so its history is that call
      site's: the previous value it sees is the one passed on the previous bar's last pass (the EMA 90);
      the port compares each EMA with the previous bar's EMA 90, as written (the reading is flagged). The
      bracket is set on the signal bar from its close and sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256). The conditions are states and repeat
      while held, each re-sending the bracket from the new close; the port keeps the opening levels, mark
      trailing_stop_pending (as #434428). An entry on the other side reverses (REVERSAL INTENDED). Stop
      module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The cash quantity
      is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, EMA ribbon counts with RSI extremes and a percent bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: cash quantity (100000 / close) stored, not ported.
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

NAME = "fmz_488034_madrid_ribbon_count_rsi_extreme_pct_bracket_reversal"
FAMILY = "ma_ribbon"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "long_take_profit_perc": [0.5, 2.0],
    "long_stop_loss_perc": [1.0, 3.0],
}
DEFAULT_PARAMS = {"long_take_profit_perc": 0.5, "long_stop_loss_perc": 1.0, "rsi_length": 14,
                  "green_min": 13, "red_min": 9}

LENGTHS = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90]


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


def _signals(bars_df, p):
    c = bars_df["close"]
    ref = c.ewm(span=100, adjust=False).mean()
    prev_last = c.ewm(span=LENGTHS[-1], adjust=False).mean().shift(1)   # the call site's previous value
    green = pd.Series(0, index=c.index)
    red = pd.Series(0, index=c.index)
    for n in LENGTHS:
        ma = c.ewm(span=n, adjust=False).mean()
        d = ma - prev_last
        green += (((d >= 0) & (ma > ref)) | ((d > 0) & (ma < ref))).astype(int)
        red += (((d < 0) & (ma > ref)) | ((d <= 0) & (ma < ref))).astype(int)
    r = _rsi(c, int(p["rsi_length"]))
    le = (green >= int(p["green_min"])) & (r < 30)
    se = (red >= int(p["red_min"])) & (r > 70)
    tp, sl = float(p["long_take_profit_perc"]) / 100, float(p["long_stop_loss_perc"]) / 100
    lvl = {"l_sl": c * (1 - sl), "l_tp": c * (1 + tp), "s_sl": c * (1 + sl), "s_tp": c * (1 - tp)}
    return le & ~se, se, lvl


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
