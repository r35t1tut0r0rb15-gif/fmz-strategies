"""EMA 21 / 55 crosses, broker days: every cross of the EMA 55 under the EMA 21 goes long and every cross above goes short
(reversing). An entry taken from flat with the EMAs 8 > 13 > 21 > 55 stacked (inverse for shorts) also gets a 150-tick
stop and a 1000-tick target, which become ATR multiples.
Port of FMZ strategy #433971 "Quadriple Exponential Moving Average Trading Strategy" (Quadriple EMA Strategy).

FMZ source id: 433971

Source
    https://www.fmz.com/strategy/433971 (PineScript v5, FMZ last modified 2023-12-01 18:29:07).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 131-155), EMA 8 / 13 / 21 / 55; stop 150 ticks, target 1000 ticks (only on the stacked entry from flat)
    crossunder(ema55, ema21) and flat and ema21 > ema55 and ema13 > ema21 and ema8 > ema13 -> entry long + exit(loss = 150, profit = 1000)
    crossover(ema55, ema21) and flat and the inverse stack -> entry short + its exit
    crossover(ema55, ema21) -> close long, entry short;  crossunder(ema55, ema21) -> close short, entry long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every cross reverses; the bracket is placed only by the stacked entry from flat, so a trade
      opened by a reversal has no bracket, as written: sl / tp are set only on those entry bars and
      are undefined (no stop) otherwise. simulate() tracks the bracket on the bars' highs and lows
      (from the bar after the fill) only to know when the source is flat again.
    * Criterion 2: 150 / 1000 ticks are 15 / 100 USD on the header's daily BTC_USDT (about 0.015 / 0.1
      ATR); they become sl_atr x Wilder ATR 14 of the signal bar and a target 1000 / 150 times that,
      as fractions of its close (shifted one bar, re-based on the fill).
    * REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; stops on daily bars: mark
      coarse_bar_stop. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick distances -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 10000 cash quantity and the tick bracket stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_433971_quad_ema_cross_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.015, 0.5],
    "slow": [55, 89],
}
DEFAULT_PARAMS = {"slow": 55, "sl_atr": 0.015, "tp_ratio": 6.666666666666667, "atr_len": 14}


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


def _signals(bars_df, p):
    o = bars_df["open"].to_numpy(dtype=float)
    h = bars_df["high"].to_numpy(dtype=float)
    lo = bars_df["low"].to_numpy(dtype=float)
    cs = bars_df["close"]
    c = cs.to_numpy(dtype=float)
    e8, e13, e21 = (cs.ewm(span=n, adjust=False).mean() for n in (8, 13, 21))
    e55 = cs.ewm(span=int(p["slow"]), adjust=False).mean()
    xu = ((e55 < e21) & (e55.shift(1) >= e21.shift(1))).to_numpy()     # crossunder(ema55, ema21)
    xo = ((e55 > e21) & (e55.shift(1) <= e21.shift(1))).to_numpy()     # crossover(ema55, ema21)
    stk_up = ((e21 > e55) & (e13 > e21) & (e8 > e13)).to_numpy()
    stk_dn = ((e21 < e55) & (e13 < e21) & (e8 < e13)).to_numpy()
    c1 = cs.shift(1)
    tr = pd.concat([bars_df["high"] - bars_df["low"], (bars_df["high"] - c1).abs(),
                    (bars_df["low"] - c1).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean().to_numpy()
    k, tpr = float(p["sl_atr"]), float(p["tp_ratio"])
    m = len(c)
    le, se = xu.copy(), xo.copy()
    fsl = np.full(m, np.nan)
    ftp = np.full(m, np.nan)
    pos, pending, fill, entry, sld, tpd = 0, 0, -1, np.nan, np.nan, np.nan
    bracket = False
    for i in range(m):
        if pending != 0:
            pos, entry, fill, pending = pending, o[i], i, 0
        if pos != 0 and bracket and i > fill:
            if pos == 1 and (lo[i] <= entry - sld or h[i] >= entry + tpd):
                pos = 0
            elif pos == -1 and (h[i] >= entry + sld or lo[i] <= entry - tpd):
                pos = 0
        flat = pos == 0
        if xu[i]:
            pending = 1
            bracket = bool(flat and stk_up[i])
        elif xo[i]:
            pending = -1
            bracket = bool(flat and stk_dn[i])
        if pending != 0 and bracket:
            sld, tpd = k * atr[i], k * tpr * atr[i]
            fsl[i], ftp[i] = sld / c[i], tpd / c[i]
    return le, se, fsl, ftp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _signals(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, fsl, ftp = _signals(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(fsl, index=ix).shift(1), "tp_stop": pd.Series(ftp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
