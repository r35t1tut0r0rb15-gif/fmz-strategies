"""Keltner channel re-entry, broker days: from flat, a close back inside the lower band after a close below it goes
long (mirror short); the stop is the outer (3x) band and the target the opposite band, both from the signal bar.
Port of FMZ strategy #429489 "Channel Reversion Trading Strategy Analysis" (Estrategia de Canales [JoseMetal]).

FMZ source id: 429489

Source
    https://www.fmz.com/strategy/429489 (PineScript v5, FMZ last modified 2023-10-17 15:48:36).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 204-323), Keltner 35 x 1.5 (true range), stop band 3x, target the opposite band; entry "close outside, then close inside"
    long = close[1] < kc_lower and close > kc_lower and flat -> entry long + exit(limit = kc_upper, stop = kc_lower_3x)
    short = close[1] > kc_upper and close < kc_upper and flat -> entry short + exit(limit = kc_lower, stop = kc_upper_3x)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.kc(close, 35, mult, true): EMA 35 of close +/- mult x EMA 35 of the true range. The indicator input
      defaults to Keltner; Bollinger and the other entry / stop / target types are input options.
    * The bracket is fixed at entry from the signal bar's levels (dynamic take-profit is off): sl / tp as
      fractions of the signal close, shifted one bar inside stops(), re-based on the fill.
    * Entries only from flat: "flat" follows the house bracket on bars. Opposite entries cannot occur.
      Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d). The start date is dropped.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, channel levels from the bars (true-range multiples).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 10 % of equity stored; the bracket quoted in original_sizing.txt.
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

NAME = "fmz_429489_keltner_reentry_bracket"
FAMILY = "bollinger_reversion"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "kc_mult": [1.5, 2.0],
    "kc_sl_mult": [3.0, 2.5],
}
DEFAULT_PARAMS = {"kc_length": 35, "kc_mult": 1.5, "kc_sl_mult": 3.0}


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


def _levels(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["kc_length"])
    mid = c.ewm(span=n, adjust=False).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    rng = tr.ewm(span=n, adjust=False).mean()
    up, dn = mid + p["kc_mult"] * rng, mid - p["kc_mult"] * rng
    up_sl, dn_sl = mid + p["kc_sl_mult"] * rng, mid - p["kc_sl_mult"] * rng
    long_c = (c.shift(1) < dn.shift(1)) & (c > dn)
    short_c = (c.shift(1) > up.shift(1)) & (c < up)
    sl = pd.Series(np.where(long_c, (c - dn_sl) / c, np.where(short_c, (up_sl - c) / c, np.nan)), index=c.index)
    tp = pd.Series(np.where(long_c, (up - c) / c, np.where(short_c, (c - dn) / c, np.nan)), index=c.index)
    return long_c, short_c, sl.where(sl > 0), tp.where(tp > 0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_c, short_c, sl, tp = _levels(bars_df, p)
    lc, sc, slv, tpv = long_c.to_numpy(), short_c.to_numpy(), sl.to_numpy(), tp.to_numpy()
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_)):
                pos = 0
        if pos == 0 and lc[i]:
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, slv[i], tpv[i]
        elif pos == 0 and sc[i]:
            se[i], pos, entry_i, s_, t_ = True, -1, i + 1, slv[i], tpv[i]
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _levels(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
