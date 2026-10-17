"""Momentum pullbacks, broker days: within 6 bars of an RSI 6 reading of 90 or more, a low dipping to the EMA 5 of lows (from
above) goes long; within 6 bars of an RSI 6 of 10 or less, a high reaching the EMA 5 of highs (from below) goes short
(reversing). A long takes profit at the 12-bar high and is closed when a low crosses under the fill price less 2.75 ATR
10; shorts mirror.
Port of FMZ strategy #435147 "Momentum Pullback Strategy" (M0PB).

FMZ source id: 435147

Source
    https://www.fmz.com/strategy/435147 (PineScript v5, FMZ last modified 2023-12-12 16:34:52).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 155-276), RSI 6, 90 / 10; EMA 5 of low / high; target highest / lowest 12; stop 2.75 ATR 10 from the average price
    trade_l = barssince(rsi >= 90) < 6 and low[1] > el[1] and low <= el -> entry long (qty 2);  trade_s mirror
    long: exit(limit = highest(12)) every bar;  low[1] > stop_l[1] and low <= stop_l (stop_l = avg - 2.75 atr) -> close_all;  shorts mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target is re-placed every bar at the rolling 12-bar high: stops() cannot express that
      (mark trailing_stop_pending); the port fixes the signal bar's 12-bar high as a fraction of its
      close, shifted one bar inside stops() (re-based on the fill). The ATR stop is tested on the
      bar's low against the fill price less 2.75 ATR, a close-based exit signal; it starts on the bar
      after the fill (the previous bar's level needs an open position). "Position held" follows the
      house target on bars.
    * strategy.entry reverses: REVERSAL INTENDED. The fixed quantity 2 is sizing. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header (the comment's 1 / 5-minute use is not the header's).

Admission criteria
    1 fits the interface: PASS, bar-close orders; rolling target fixed at entry (approximation stated); ATR exit on closes.
    2 generic: PASS, RSI extremes, EMA pullbacks and ATR exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity 2, commission and slippage stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_435147_momentum_pullback_ema5"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_inp": [2.75, 1.5],
    "look": [12, 24],
}
DEFAULT_PARAMS = {"rsi_len": 6, "atr_len": 10, "atr_inp": 2.75, "look": 12}


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


def _since(cond):
    out = np.full(len(cond), np.nan)
    last = -1
    for i in range(len(cond)):
        if cond[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna()).to_numpy()
    es, el = h.ewm(span=5, adjust=False).mean(), lo.ewm(span=5, adjust=False).mean()
    let = ((lo.shift(1) > el.shift(1)) & (lo <= el)).to_numpy()
    st_ = ((h.shift(1) < es.shift(1)) & (h >= es)).to_numpy()
    with np.errstate(invalid="ignore"):
        tl = (_since(r >= 90) < 6) & let
        ts = (_since(r <= 10) < 6) & st_
    k = int(p["look"])
    ph, pl = h.rolling(k).max().to_numpy(), lo.rolling(k).min().to_numpy()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() * float(p["atr_inp"])).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    tp = np.full(m, np.nan)
    pos, ei, t_, prev_stop = 0, -1, np.nan, np.nan
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if pos != 0 and i >= ei and not np.isnan(t_):            # the house target from the fill price
                if (pos == 1 and hv[i] >= ov[ei] * (1 + t_)) or (pos == -1 and lv[i] <= ov[ei] * (1 - t_)):
                    pos = 0
            stop = (ov[ei] - atr[i] if pos == 1 else ov[ei] + atr[i]) if pos != 0 and i >= ei else np.nan
            new = pos
            if pos == 1 and lv[i - 1] > prev_stop and lv[i] <= stop:
                new = 0
            if pos == -1 and hv[i - 1] < prev_stop and hv[i] >= stop:
                new = 0
            if tl[i] and pos != 1:
                new = 1
            if ts[i] and pos != -1:
                new = -1
            if new != pos:
                le[i], se[i] = new == 1, new == -1
                lx[i], sx[i] = pos == 1 and new == 0, pos == -1 and new == 0
                if new != 0:
                    ei = i + 1
                    f = (ph[i] - cv[i]) / cv[i] if new == 1 else (cv[i] - pl[i]) / cv[i]
                    t_ = f if f > 0 else np.nan
                    tp[i] = t_
            prev_stop = stop if new == pos else np.nan
            pos = new
    return le, lx, se, sx, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, _ = _run(bars_df, p)
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    *_, tp = _run(bars_df, p)
    return {"tp_stop": pd.Series(tp, index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {}
