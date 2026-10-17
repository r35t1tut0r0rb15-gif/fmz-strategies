"""HPotter N bars up, broker days, long only: after 4 consecutive bars closing at or above their open (counted on the
previous bars), go long and keep the long while the script's reference price (the last such bar's close) stands; the
reference is cleared when a bar's low reaches 10 price units under it or its high 20 above it (re-expressed as ATR
multiples), which closes the long.
Port of FMZ strategy #434674 "N Consecutive Higher Closes Breakout Strategy" (N Bars Up).

FMZ source id: 434674

Source
    https://www.fmz.com/strategy/434674 (PineScript v4, FMZ last modified 2023-12-08 10:50:54).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 154-172), n 4; take profit 20 / stop loss 10 price units ("pip" inputs)
    nCounter = close[1] >= open[1] ? nCounter[1] + 1 : 0;  C1 = nCounter >= 4;  posprice = C1 ? close : posprice[1];  pos = posprice > 0
    pos 0 -> close_all;  pos 1 -> entry long;  then posprice := 0 if low <= posprice - 10 or high >= posprice + 20

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are the script's own bookkeeping tested on bar closes (the bar's low / high against
      the reference), so they are close-based exit signals (no broker stop): the long is held while
      the reference stands, as written.
    * Criterion 2: 10 / 20 price units on daily BTC are about 0.0125 / 0.025 x the daily Wilder ATR
      14 in 2023; the port uses sl_atr and 2 x sl_atr of the ATR at the bar that sets the
      reference. Long only. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the script's levels as exit signals.
    2 generic: ADAPT, price-unit distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND434674 (2 members, best partner #436599, Jaccard 0.660); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434674_n_bars_up_long"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n_len": [4, 3],
    "sl_atr": [0.0125, 1.0],
}
DEFAULT_PARAMS = {"n_len": 4, "sl_atr": 0.0125, "tp_mult": 2.0, "atr_len": 14}


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
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean().to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    n, ks, kt = int(p["n_len"]), float(p["sl_atr"]), float(p["sl_atr"]) * float(p["tp_mult"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    cnt, pp, ds, dt = 0, 0.0, np.nan, np.nan
    for i in range(m):
        if i > 0:
            cnt = cnt + 1 if cv[i - 1] >= ov[i - 1] else 0
        if cnt >= n:
            pp, ds, dt = cv[i], ks * atr[i], kt * atr[i]
        tgt[i] = 1 if pp > 0 else 0
        if pp > 0 and lv[i] <= pp - ds:
            pp = 0.0
        if pp > 0 and hv[i] >= pp + dt:
            pp = 0.0
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix), \
        false, false.copy()


def portfolio_kwargs(**params):
    return {}
