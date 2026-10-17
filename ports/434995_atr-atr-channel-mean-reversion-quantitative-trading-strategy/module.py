"""ATR stretch mean reversion, broker days, long only from flat: a bar whose low reaches more than one ATR 10 under its own
open goes long; the long is closed when a high passes the open plus one ATR, when a high above the EMA 10 comes with a close
under the previous low, or when a low falls 1.5 ATR under the fill price (all tested on bar closes).
Port of FMZ strategy #434995 "基于ATR通道均线反转的量化交易策略ATR-Channel-Mean-Reversion-Quantitative-Trading-Strategy" (ATR Mean Reversion).

FMZ source id: 434995

Source
    https://www.fmz.com/strategy/434995 (PineScript v5, FMZ last modified 2023-12-11 15:38:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 155-189), ATR & EMA 10; SL 1.5 ATR from the fill (buyPrice = the next bar's open); dates 1995-2099
    low < open - atr(10) and flat -> entry long;  buyPrice = open of the bar after the signal
    (high > ema(10) and long and close < low[1]) or high > open + atr(10) -> close long;  long and low < buyPrice - 1.5 atr -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * All three exits are tested on the bar's close (strategy.close at the next open): close-based
      exit signals, not broker stops (no mark). The stop test on the fill bar still uses the old
      buyPrice (0, or na after an exit), so it starts on the bar after the fill, as written.
    * Long only; entries only from flat. The date filter is always true. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exits on closes.
    2 generic: PASS, ATR stretches from the open and an average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity, capital and commission stored.
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

NAME = "fmz_434995_atr_open_stretch_long"
FAMILY = "mean_reversion_band"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [10, 20],
    "sl_mult": [1.5, 3.0],
}
DEFAULT_PARAMS = {"period": 10, "sl_mult": 1.5}


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
    n = int(p["period"])
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    ema = c.ewm(span=n, adjust=False).mean().to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    l1 = np.concatenate(([np.nan], lv[:-1]))
    k = float(p["sl_mult"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, bp, sig_prev = 0, 0.0, False
    with np.errstate(invalid="ignore"):
        for i in range(m):
            buy = (lv[i] < ov[i] - atr[i]) and pos == 0
            sell = (hv[i] > ema[i] and pos > 0 and cv[i] < l1[i]) or hv[i] > ov[i] + atr[i]
            stop = pos > 0 and lv[i] < bp - k * atr[i]       # bp before this bar's update
            nxt = pos
            if buy:
                le[i], nxt = True, 1
            if sig_prev:
                bp = ov[i]
            if (sell or stop) and pos > 0:
                lx[i], nxt = True, 0
            if sell or stop:
                bp = np.nan
            sig_prev = buy
            pos = nxt
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
