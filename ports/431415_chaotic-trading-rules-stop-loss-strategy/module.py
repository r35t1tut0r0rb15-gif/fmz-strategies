"""RSI 14 exits from the extremes with a leverage "call" exit, broker days: the first RSI cross back above 30 after a short
signal goes long, the first cross back below 70 after a long signal goes short; a low 0.4 % under the long signal bar's
open (high 0.39 % over the short's) closes the position, the 200x liquidation level as written.
Port of FMZ strategy #431415 "Chaotic Trading Rules Stop Loss Strategy" (Adding some essential components to a prebuilt RSI strategy).

FMZ source id: 431415

Source
    https://www.fmz.com/strategy/431415 (PineScript v2, FMZ last modified 2023-11-07 16:44:31).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 212-298), RSI 14, 30 / 70, leverage 200, trailing / TP / SL 99999 (off)
    long = crossover(rsi, 30); long_signal = crossover(last_long, last_short) (the first long after a short) -> entry long
    long_call = signal open - (0.8 + 0.2 / 200) / 200 x signal open;  low <= long_call -> close long
    short_call = signal open + (0.78 + 0.2 / 200) / 200 x signal open;  high >= short_call -> close short
    ts / tp / sl = 99999 / 100 price units (the template's "off" values)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the trailing, take-profit and stop distances are 999.99 price units, the template's
      disabling default (they never fire on the quotes it was written for); a price-unit distance has
      no generic meaning: not ported. The leverage "call" exits are fractions of the signal bar's open
      and are ported, checked on the bar's low / high with strategy.close (next-open exits).
    * The closes act on the position held at the bar's start and do not undo a reversal on the same
      bar. strategy.entry reverses: REVERSAL INTENDED. The test window is always true. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: ADAPT, price-unit distances (the template's off values) not ported; leverage call as a fraction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the leverage input stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND431415 (2 members, best partner #440456, Jaccard 0.786); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431415_rsi_leverage_call"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "leverage": [200, 50],
    "length": [14, 7],
}
DEFAULT_PARAMS = {"length": 14, "over_sold": 30, "over_bought": 70, "leverage": 200}


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


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    r = _rsi(bars_df["close"], int(p["length"]))
    lg = ((r > p["over_sold"]) & (r.shift(1) <= p["over_sold"])).to_numpy()
    sh = ((r < p["over_bought"]) & (r.shift(1) >= p["over_bought"])).to_numpy()
    lev = float(p["leverage"])
    kl = (0.8 + 0.2 / lev) / lev
    ks = (0.78 + 0.2 / lev) / lev
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos, last_l, last_s, side = 0, 0.0, 0.0, 0
    open_l = open_s = 0.0
    for i in range(m):
        prev_side = side
        if lg[i]:
            last_l = i + 1.0
        if sh[i]:
            last_s = i + 1.0
        side = 1 if last_l > last_s else (-1 if last_s > last_l else side)
        l_sig = side == 1 and prev_side != 1 and lg[i]
        s_sig = side == -1 and prev_side != -1 and sh[i]
        if l_sig:
            open_l = o[i]
        if s_sig:
            open_s = o[i]
        start = pos
        if l_sig:
            pos = 1
        if s_sig:
            pos = -1
        if start == 1 and pos == 1 and lo[i] <= open_l * (1 - kl):
            pos = 0
        if start == -1 and pos == -1 and h[i] >= open_s * (1 + ks):
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
