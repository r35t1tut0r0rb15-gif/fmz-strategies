"""Three-candle momentum bursts with the trend, daily bars: three rising candles (the last bigger than the middle, the first bigger than the middle) with a wide range above the EMA 50 go long, the mirror goes short; a long closes when a close reaches the 20-bar high or falls to the 20-bar low noted at its signal, a short on the mirror; reversing.
Port of FMZ strategy #458270 "Dynamic Trend Following with Precision Take Profit and Stop Loss Strategy" (Scalp Slayer (i)).

FMZ source id: 458270

Source
    https://www.fmz.com/strategy/458270 (PineScript v5, FMZ last modified 2024-07-31 14:27:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 194-314), range = high - low vs 1.5 x EMA 50 of it; EMA 50 trend; 20-bar high / low (current bar included) as target / stop (close tests)
    buy pattern and close > ema50 -> entry Buy, target = highest(high, 20), stop = lowest(low, 20);  sell pattern and close < ema50 -> entry Sell, target = lowest, stop = highest
    close >= long target or close <= long stop -> close Buy, clear;  close <= short target or close >= short stop -> close Sell, clear

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long and short levels are kept per side as written and cleared when hit; a close acts only on
      a position held into the bar and not being reversed (#437773), so a level hit on the signal bar
      itself clears the levels and the new trade waits for the opposite entry. The exits are bar-close
      tests filled at the next open. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the target and stop are close tests.
    2 generic: PASS, three-candle bursts with range and trend filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_458270_three_candle_burst_range_levels_close_tests_reversal"
FAMILY = "momentum_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "filter_number": [1.5, 1.0],
    "trend_len": [50, 100],
    "lookback": [20, 10],
}
DEFAULT_PARAMS = {"filter_number": 1.5, "trend_len": 50, "lookback": 20}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    rng = h - lo
    wide = rng > float(p["filter_number"]) * rng.ewm(span=50, adjust=False).mean()
    tr_ema = c.ewm(span=int(p["trend_len"]), adjust=False).mean()
    body = (c - o).abs()
    b1, b2 = body.shift(1), body.shift(2)
    sizes = (b2 > b1) & (body > b1)
    up = (c.shift(2) > o.shift(2)) & (c.shift(1) > o.shift(1)) & (c > o) & (c > c.shift(1)) & (c.shift(1) > c.shift(2))
    dn = (c.shift(2) < o.shift(2)) & (c.shift(1) < o.shift(1)) & (c < o) & (c < c.shift(1)) & (c.shift(1) < c.shift(2))
    buy = ((c > tr_ema) & up & sizes & wide).to_numpy()
    sell = ((c < tr_ema) & dn & sizes & wide).to_numpy()
    k = int(p["lookback"])
    hh, ll = h.rolling(k).max().to_numpy(), lo.rolling(k).min().to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    lt = ls = st = ss = np.nan
    for i in range(m):
        cur = pos
        if buy[i]:
            cur, lt, ls = 1, hh[i], ll[i]
        if sell[i]:
            cur, st, ss = -1, ll[i], hh[i]
        close_l = cv[i] >= lt or cv[i] <= ls
        close_s = cv[i] <= st or cv[i] >= ss
        if close_l:
            lt = ls = np.nan
            if pos == 1 and cur == 1:
                cur = 0                          # the close acts only on a long held, not reversed
        if close_s:
            st = ss = np.nan
            if pos == -1 and cur == -1:
                cur = 0
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
