"""Broker days: the Choppiness Index 14 crossing under 61.8 while a Renko-style direction (ATR 14 boxes of the close) is up and the close is above its EMA 8 goes long; the mirror (direction down, close under the EMA 8) goes short; reversing.
Port of FMZ strategy #437652 "基于ATR和波动性指数的趋势跟踪策略ATR-and-Volatility-Index-Based-Trend-Tracking-Strategy" (Weis Chop Strategy (sharatgbhat)).

FMZ source id: 437652

Source
    https://www.fmz.com/strategy/437652 (PineScript v4, FMZ last modified 2024-01-04 15:31:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 144-202), Renko method ATR 14, price source Close; CHOP 14 at 61.8; EMA 8; Weis wave volume (plot only)
    currclose := close > prevclose + atr(14) or close < prevclose - atr(14) ? close : prevclose;  direction = currclose > prev ? 1 : < ? -1 : direction[1]
    close > ema(8) and direction up and crossunder(chop, 61.8) -> entry Buy;  mirror -> entry Sell, exit("exit", "Buy", when = directionIsDown, profit 20, loss 10 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the Close source the Renko "high" and "low" are both the close; the box size is ATR 14; the
      brick level starts from 0 (nz) on the first bar. The Weis wave volume only feeds a plot: volume is
      not used (weird case: held for volume). The two strategy.exit calls sit inside the short block: the
      "Buy" one (20 / 10 ticks, about 2 / 1 USD on BTC) is sent on the bar whose short entry reverses that
      long anyway, and the "Sell" one needs directionIsUp, false on that bar; they are not ported, so a
      position ends at the opposite entry. The max intraday loss line is commented out. REVERSAL INTENDED.
      10 % of equity is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Renko direction with a choppiness breakdown and EMA momentum.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 10 % of equity, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437652_renko_atr_direction_chop_cross_ema8_reversal"
FAMILY = "choppiness"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "chop_len": [14, 21],
    "box_atr": [14, 28],
}
DEFAULT_PARAMS = {"chop_len": 14, "box_atr": 14, "chop_level": 61.8, "ema_len": 8}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    box = _rma(tr, int(p["box_atr"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    direc = np.zeros(m)
    cur_p, d_p = np.nan, 0.0
    for i in range(m):
        prev = 0.0 if np.isnan(cur_p) else cur_p
        if cv[i] > prev + box[i]:
            cur = cv[i]
        elif cv[i] < prev - box[i]:
            cur = cv[i]
        else:
            cur = prev
        d = 1.0 if cur > prev else (-1.0 if cur < prev else d_p)
        direc[i] = d
        cur_p, d_p = cur, d
    n = int(p["chop_len"])
    tr1 = tr.fillna(h - lo)
    rng = h.rolling(n).max() - lo.rolling(n).min()
    ci = 100 * np.log10(tr1.rolling(n).sum() / rng.where(rng != 0)) / np.log10(n)
    lvl = float(p["chop_level"])
    trade = ((ci < lvl) & (ci.shift(1) >= lvl)).to_numpy()
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    buy = (c > e).to_numpy() & (direc > 0) & trade
    sell = (c < e).to_numpy() & (direc < 0) & trade
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(buy, index=ix), false, pd.Series(sell, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
