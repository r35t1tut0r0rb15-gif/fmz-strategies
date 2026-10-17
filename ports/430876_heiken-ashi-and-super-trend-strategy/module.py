"""SuperTrend (ATR 10 x 3) computed on Heikin Ashi candles, broker days: the trend turning up goes long, turning down goes
short; each position has a 1.1 % target measured from the close before the signal bar.
Port of FMZ strategy #430876 "Heiken Ashi and Super Trend Strategy" (Heiken Ashi & Super Trend_ARM).

FMZ source id: 430876

Source
    https://www.fmz.com/strategy/430876 (PineScript v5, FMZ last modified 2023-11-02 16:15:18).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 130-256), HA SuperTrend factor 3, ATR 10, TP 1.1 %
    supertrend on Heikin Ashi high / low / close (HA ATR = rma of the HA true range, SMA seed)
    long = change(direction) < 0 -> entry "L";  short = change(direction) > 0 -> entry "S"
    open_longCondition = close[1] on the long bar; exit("TP_L", profit = open_longCondition x 1.1 % / mintick) (mirror short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Heikin Ashi from the bars: haClose = ohlc4, haOpen = (haOpen[1] + haClose[1]) / 2 (first
      (open + close) / 2), haHigh / haLow the extremes with the body. The SuperTrend is the author's
      own x_supertrend on them, nz() of the first bands read as 0, as written.
    * The target is a price distance of close[1] x 1.1 % from the entry fill (profit in ticks): as a
      fraction of the fill, close two bars before the fill bar x 1.1 % / the fill bar's open (known at
      that open). No stop. The date window is dropped.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on 1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the target fixed at entry.
    2 generic: PASS, a Heikin Ashi SuperTrend and a percentage target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the commission stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG430876 (2 members, best partner #435475, Jaccard 0.948); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_430876_heikin_ashi_supertrend_tp"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "factor": [3.0, 2.0],
    "tp_pct": [1.1, 3.0],
}
DEFAULT_PARAMS = {"factor": 3.0, "atr_len": 10, "tp_pct": 1.1}


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
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    m = len(c)
    hc = (o + h + lo + c) / 4
    ho = np.empty(m)
    for i in range(m):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 else (ho[i - 1] + hc[i - 1]) / 2
    hh = np.maximum(h, np.maximum(ho, hc))
    hl = np.minimum(lo, np.minimum(ho, hc))
    n, f = int(p["atr_len"]), float(p["factor"])
    tr = np.empty(m)
    for i in range(m):
        tr[i] = hh[i] - hl[i] if i == 0 else max(hh[i] - hl[i], abs(hh[i] - hc[i - 1]), abs(hl[i] - hc[i - 1]))
    atr = np.full(m, np.nan)
    for i in range(n - 1, m):
        atr[i] = tr[i - n + 1:i + 1].mean() if np.isnan(atr[i - 1]) else (tr[i] + (n - 1) * atr[i - 1]) / n
    src = (hh + hl) / 2
    direction = np.zeros(m)
    lower_p = upper_p = st_p = np.nan
    for i in range(m):
        up, lw = src[i] + f * atr[i], src[i] - f * atr[i]
        pl = 0.0 if np.isnan(lower_p) else lower_p
        pu = 0.0 if np.isnan(upper_p) else upper_p
        hc1 = hc[i - 1] if i else np.nan
        lw = lw if (lw > pl or hc1 < pl) else pl
        up = up if (up < pu or hc1 > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif st_p == pu:
            d = -1 if hc[i] > up else 1
        else:
            d = 1 if hc[i] < lw else -1
        st = lw if d == -1 else up
        direction[i] = d
        lower_p, upper_p, st_p = lw, up, st
    ch = np.concatenate(([0.0], np.diff(direction)))
    return ch < 0, ch > 0


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lg, sh = _signals(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(lg, index=idx), false, pd.Series(sh, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lg, sh = _signals(bars_df, p)
    idx = bars_df.index
    sig = pd.Series(lg | sh, index=idx).shift(1, fill_value=False)
    dist = bars_df["close"].shift(2) * float(p["tp_pct"]) / 100
    return {"tp_stop": (dist / bars_df["open"]).where(sig)}


def portfolio_kwargs(**params):
    return {}
