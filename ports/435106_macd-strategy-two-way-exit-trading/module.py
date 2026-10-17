"""MACD crosses on the far side of zero with an EMA 200 filter, broker days, from flat: above the EMA, a MACD cross up while
the MACD is below zero goes long with the stop at the 7-bar low and a target twice that distance; below the EMA, a cross
down above zero goes short with the stop at the 7-bar high.
Port of FMZ strategy #435106 "MACD Strategy Two Way Exit Trading" (MACD Strategy).

FMZ source id: 435106

Source
    https://www.fmz.com/strategy/435106 (PineScript v5, FMZ last modified 2023-12-12 12:44:50).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 155-233), EMA 200; MACD 12 / 26 / 9 (EMA); swing 7 / 7; risk / reward 2; risk 2 % per trade (sizing)
    close > ema200 and crossover(macd, signal) and macd < 0 and flat -> risk = (close - lowest(low, 7)) / close, entry long
    long -> exit(stop = avg (1 - risk), limit = avg (1 + 2 risk));  shorts mirror with highest(high, 7)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is a fraction of the position's average price, with the risk fraction from the
      signal bar: sl_stop = risk, tp_stop = 2 x risk of the fill (shifted one bar inside stops()). A
      signal whose stop is not beyond the close places no entry. The lot size (2 % risk) is sizing.
    * Entries only from flat: "flat" follows the house bracket on bars. Opposite entries cannot
      occur. The date filter is off in the code. Stop module: portfolio_kwargs {} (driver D4). Stops
      on daily bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, MACD crosses, an average filter and swing-based exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based lot sizes and slippage stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_435106_macd_far_side_swing_bracket"
FAMILY = "macd_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [2.0, 1.0],
    "swing": [7, 14],
}
DEFAULT_PARAMS = {"ema_len": 200, "rr": 2.0, "swing": 7}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    lc = ((c > ema) & (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (macd < 0)).to_numpy()
    sc = ((c < ema) & (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (macd > 0)).to_numpy()
    k = int(p["swing"])
    cv = c.to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        rl = (cv - lo.rolling(k).min().to_numpy()) / cv
        rs = (h.rolling(k).max().to_numpy() - cv) / cv
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    rr = float(p["rr"])
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl = np.full(m, np.nan)
    pos, ei, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= ei:                          # the house bracket from the fill price
            e0 = ov[ei]
            if pos == 1 and (lv[i] <= e0 * (1 - s_) or hv[i] >= e0 * (1 + rr * s_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e0 * (1 + s_) or lv[i] <= e0 * (1 - rr * s_)):
                pos = 0
        if pos == 0 and lc[i] and rl[i] > 0:
            le[i], pos, ei, s_ = True, 1, i + 1, rl[i]
            sl[i] = s_
        elif pos == 0 and sc[i] and rs[i] > 0:
            se[i], pos, ei, s_ = True, -1, i + 1, rs[i]
            sl[i] = s_
    return le, se, sl, sl * rr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _run(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
