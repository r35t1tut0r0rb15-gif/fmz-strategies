"""2/20 EMA side and Bull Power combination, broker days: the two-bar extreme on the far side of the EMA 14 against the previous close sets a long / short state; the 15-bar SMA of Gimelfarb's bull power above
-15 sets the other; agreeing long go long, agreeing short go short, otherwise close all; reversing.
Port of FMZ strategy #437031 "Quantitative Dual indicator Strategy" (Combo 2/20 EMA & Bull Power).

FMZ source id: 437031

Source
    https://www.fmz.com/strategy/437031 (PineScript v5, FMZ last modified 2023-12-29 16:29:21).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 119-170), EMA length 14, bull power sell level -15 (price units), reverse off, start 2005
    EMA20: nXS = (min(low, low[1]) > ema or max(high, high[1]) < ema) ? min(low, low[1]) : max(high, high[1]);  pos = -1 if nXS > close[1], 1 if nXS < close[1], else pos[1]
    BP: value = the candle-case range formula (non-negative);  pos = sma(value, 15) > -15 ? 1 : -1;  both 1 -> entry Long, both -1 -> entry Short, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bull-power value is always a non-negative range, so its average is above the -15 level (a
      price-unit level, left as written: the test cannot depend on it) from the 15th bar on, and the bull
      side is -1 only while the average is undefined: shorts can only come in the warm-up, as written
      (an intended version is owed). The start-time test (2005) is a backtest window: dropped. State 0
      closes. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, EMA side test; the bull-power level is a price unit that cannot bind.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND429466 (3 members, best partner #438067, Jaccard 0.714); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437031_ema_2_20_bull_power_combo"
FAMILY = "trend_confluence"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20],
    "bp_len": [15, 30],
}
DEFAULT_PARAMS = {"length": 14, "bp_len": 15, "sell_level": -15.0, "reverse": False}


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


def _bull_value(o, h, lo, c, c1):
    """The script's nested candle-case formula, bar by bar (na comparisons are false, as in Pine)."""
    if c < o:
        return max(h - c1, c - lo) if c1 < o else max(h - o, c - lo)
    if c > o:
        return h - lo if c1 > o else max(o - c1, h - lo)
    if h - c > c - lo:
        return max(h - c1, c - lo) if c1 < o else h - o
    if h - c < c - lo:
        return h - lo if c1 > o else max(o - c, h - lo)
    if c1 > o:
        return max(h - o, c - lo)
    return max(o - c, h - lo) if c1 < o else h - lo


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ema = c.ewm(span=int(p["length"]), adjust=False).mean()
    hh = np.maximum(h, h.shift(1))
    ll = np.minimum(lo, lo.shift(1))
    nxs = pd.Series(np.where((ll > ema) | (hh < ema), ll, hh), index=c.index).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    m = len(cv)
    val = np.array([_bull_value(ov[i], hv[i], lv[i], cv[i], cv[i - 1] if i else np.nan) for i in range(m)])
    v2 = pd.Series(val, index=c.index).rolling(int(p["bp_len"])).mean().to_numpy()
    lvl = float(p["sell_level"])
    sig = np.zeros(m)
    pe = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            c1 = cv[i - 1] if i else np.nan
            if nxs[i] > c1:
                pe = -1.0
            elif nxs[i] < c1:
                pe = 1.0
            pb = 1.0 if v2[i] > lvl else -1.0
            sig[i] = 1.0 if (pe == 1.0 and pb == 1.0) else (-1.0 if (pe == -1.0 and pb == -1.0) else 0.0)
    if p["reverse"]:
        sig = -sig
    ix = bars_df.index
    flat = pd.Series(sig == 0, index=ix)
    return pd.Series(sig == 1, index=ix), flat, pd.Series(sig == -1, index=ix), flat.copy()


def portfolio_kwargs(**params):
    return {}
