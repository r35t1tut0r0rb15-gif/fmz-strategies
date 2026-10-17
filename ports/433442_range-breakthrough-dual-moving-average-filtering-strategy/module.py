"""Range-filter direction flips confirmed by a MACD-slope burst, broker days: the first bar of an up phase of the range
filter (100, x3) goes long when the MACD 20 / 40 change times 150 exceeds the Bollinger 20 / 2 band width; the mirror
goes short.
Port of FMZ strategy #433442 "Range Breakthrough Dual Moving Average Filtering Strategy" (Range Filter Buy and Sell Strategies).

FMZ source id: 433442

Source
    https://www.fmz.com/strategy/433442 (PineScript v5, FMZ last modified 2023-11-27 17:03:08).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 207-336), range filter: sampling 100, multiplier 3; MACD 20 / 40, sensitivity 150; BB 20 / 2; percent TP / SL off
    smrng = ema(ema(|src - src[1]|, 100), 199) x 3;  filt = the range-filter ratchet;  upward / downward = counts of rising / falling filt
    longCond = src > filt and upward > 0;  CondIni flips;  longCondition = longCond and CondIni[1] == -1 (shortCondition mirrors)
    longCondition and t1 > e1 and t1 > 0 -> entry long (t1 = (macd - macd[1]) x 150, e1 = BB width);  short mirrors

Interpretation choices (Pine rules in SURVEY_README.md)
    * t1 and e1 are both price differences, so the comparison is scale-free. The percent take profit /
      stop loss is off by default; the dead-zone value is unused.
    * pyramiding 5 could stack a second long when a short phase passes without its MACD confirmation;
      stacking is sizing (SURVEY_README, as #426588), so the net position is ported: long until a
      confirmed short, and so on. strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a range filter and a slope / width ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 5 stacking stored in original_sizing.txt.
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

NAME = "fmz_433442_range_filter_macd_burst"
FAMILY = "range_filter_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "per": [100, 50],
    "sensitivity": [150, 75],
}
DEFAULT_PARAMS = {"per": 100, "mult": 3.0, "sensitivity": 150, "fast": 20, "slow": 40, "bb_len": 20, "bb_mult": 2.0}


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
    c = bars_df["close"]
    t = int(p["per"])
    avr = c.diff().abs().ewm(span=t, adjust=False).mean()
    rng = (avr.ewm(span=t * 2 - 1, adjust=False).mean() * float(p["mult"])).to_numpy()
    x = c.to_numpy(dtype=float)
    m = len(x)
    filt = np.full(m, np.nan)
    prev = 0.0
    for i in range(m):
        r = rng[i]
        if np.isnan(r) or np.isnan(x[i]):
            filt[i] = x[i]
        elif x[i] > prev:
            filt[i] = prev if x[i] - r < prev else x[i] - r
        else:
            filt[i] = prev if x[i] + r > prev else x[i] + r
        prev = 0.0 if np.isnan(filt[i]) else filt[i]
    upw = np.zeros(m)
    dnw = np.zeros(m)
    for i in range(1, m):
        if filt[i] > filt[i - 1]:
            upw[i], dnw[i] = upw[i - 1] + 1, 0
        elif filt[i] < filt[i - 1]:
            upw[i], dnw[i] = 0, dnw[i - 1] + 1
        else:
            upw[i], dnw[i] = upw[i - 1], dnw[i - 1]
    x1 = np.concatenate(([np.nan], x[:-1]))
    with np.errstate(invalid="ignore"):
        moved = (x > x1) | (x < x1)          # the source's two clauses exclude an unchanged close
        lc = (x > filt) & (upw > 0) & moved
        sc = (x < filt) & (dnw > 0) & moved

    def macd(s):
        return s.ewm(span=int(p["fast"]), adjust=False).mean() - s.ewm(span=int(p["slow"]), adjust=False).mean()

    t1 = ((macd(c) - macd(c.shift(1))) * float(p["sensitivity"])).to_numpy()
    e1 = (2 * float(p["bb_mult"]) * c.rolling(int(p["bb_len"])).std(ddof=0)).to_numpy()
    with np.errstate(invalid="ignore"):
        up_ok = (t1 > 0) & (t1 > e1)
        dn_ok = (-t1 > 0) & (-t1 > e1)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    cond = 0
    for i in range(m):
        prev_c = cond
        if lc[i]:
            cond = 1
        elif sc[i]:
            cond = -1
        le[i] = lc[i] and prev_c == -1 and up_ok[i]
        se[i] = sc[i] and prev_c == 1 and dn_ok[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
