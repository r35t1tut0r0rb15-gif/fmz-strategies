"""Triple Supertrend alignment, broker days, long only, from flat: all three Supertrends turning up together while their lines sit over the EMA 233 buys; the position is closed
by a close-based ATR ratchet (2 ATR under the close, never lowered) or, when a 3 ATR x 2 profit has been reached, by a low under the lowest Supertrend line.
Port of FMZ strategy #436110 "Triple Supertrend Breakout Strategy" (ms hypertrender).

FMZ source id: 436110

Source
    https://www.fmz.com/strategy/436110 (PineScript v5, FMZ last modified 2023-12-21 12:05:07).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 197-358), Supertrends (1, 10), (2, 11), (3, 12); EMA 233; ATR 26 x 2; trailing stop on; reward mode off
    extremebullish = direction1 < 0 and direction2 < 0 and direction3 < 0 and generaluptrend (all three lines over the EMA);  openlong = extremebullish and not extremebullish[1] and the lines over the EMA
    exitlong = low < lowest supertrend line (when strictly the lowest) x 0.999;  entry long when flat;  ratchet: stop = max(stop, close - 2 ATR at entry); long and close <= stop -> close;  long and exitlong -> close only if low > entry + 3 x 2 ATR (take_profit_long)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Supertrend lines and directions are Pine's built-in (the "up" direction is -1). The ratchet
      and the profit-gated exit are rules on closes and lows tested at the bar's close and filled at the next
      open: close-based exit signals, not broker stops (no mark). While flat the level is close minus the
      current buffer. The pyramiding branch only relabels an entry while long. Long only. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exits on closes.
    2 generic: PASS, Supertrend alignment, an EMA filter and an ATR ratchet.
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

NAME = "fmz_436110_triple_supertrend_alignment_long"
FAMILY = "supertrend"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_multi": [2, 3],
    "ema_len": [233, 100],
}
DEFAULT_PARAMS = {"atr_multi": 2, "ema_len": 233, "atr_len": 26, "reward": 3}
ST_SETTINGS = ((1.0, 10), (2.0, 11), (3.0, 12))   # (factor, ATR length)


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


def _supertrend(h, lo, c, factor, n):
    """Pine's built-in supertrend(factor, atrPeriod): (direction -1 up / 1 down, line)."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    dr = np.ones(m)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
        if i == 0 or np.isnan(atr[i - 1]):
            dr[i] = 1
        elif st[i - 1] == ub[i - 1]:
            dr[i] = -1 if cv[i] > ub[i] else 1
        else:
            dr[i] = 1 if cv[i] < lb[i] else -1
        st[i] = lb[i] if dr[i] == -1 else ub[i]
    return dr, st


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    d, s = zip(*(_supertrend(h, lo, c, f, n) for f, n in ST_SETTINGS))
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean().to_numpy()
    cv, lv = c.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        up_trend = (s[0] > ema) & (s[1] > ema) & (s[2] > ema)
        extreme = (d[0] < 0) & (d[1] < 0) & (d[2] < 0) & up_trend
    ext1 = np.concatenate(([False], extreme[:-1]))
    open_long = extreme & ~ext1 & up_trend
    s0, s1, s2 = s
    with np.errstate(invalid="ignore"):
        stop_up = np.where((s0 < s1) & (s0 < s2), s0, np.where((s1 < s0) & (s1 < s2), s1, np.where((s2 < s0) & (s2 < s1), s2, np.nan)))
    exit_long = lv < (stop_up - (stop_up / 100) * 0.1)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean().to_numpy()
    buf_now = atr * float(p["atr_multi"])
    rr_buf = buf_now * float(p["reward"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend = 0, None
    entry_price, trailing, stop = 0.0, 0.0, 0.0
    for i in range(m):
        if pend == "enter":
            pos = 1
        elif pend == "exit":
            pos = 0
        pend = None
        stop = max(stop, cv[i] - trailing)
        if pos == 0:
            stop = cv[i] - trailing
        if open_long[i]:
            if pos == 0 and not np.isnan(buf_now[i]):
                entry_price, trailing, stop = cv[i], buf_now[i], cv[i] - buf_now[i]
                le[i], pend = True, "enter"
        if pos > 0 and cv[i] <= stop:
            lx[i], pend = True, "exit"
        if pos > 0 and exit_long[i] and lv[i] > entry_price + rr_buf[i]:
            lx[i], pend = True, "exit"
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
