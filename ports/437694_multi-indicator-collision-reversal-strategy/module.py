"""123 reversal and "N bars up" combination, broker days: the 123 reversal state (two closes against a stochastic 14 test) long together with the N-bars-up state (on since the first run of four up candles)
goes long; anything else closes (the second state is never short, so neither is the strategy); long only as written.
Port of FMZ strategy #437694 "Multi indicator Collision Reversal Strategy" (Combo Backtest 123 Reversal & N Bars Up).

FMZ source id: 437694

Source
    https://www.fmz.com/strategy/437694 (PineScript v4, FMZ last modified 2024-01-04 18:02:12).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 198-239), 123: length 14, K smoothing 1, D 3, level 50; N bars up 4; reverse off
    NBU: nCounter counts up candles of the previous bar (close[1] >= open[1]), reset by a down candle;  posprice := C1 ? close : posprice[1];  pos = posprice > 0 ? 1 : 0
    pos = 1 if both are 1, -1 if both are -1, else 0;  entry Long / Short, close_all on 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * posprice is never reset, so after the first run of four up candles the N-bars-up state stays 1 for
      good, and it is never -1: the combination is long or flat, never short, as written (an intended
      version is owed). The 123 test is read as written. State 0 closes. Long only. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and candle counts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430768 (2 members, best partner #430768, Jaccard 0.768); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437694_reversal123_n_bars_up_combo"
FAMILY = "reversal_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "n_length": [4, 3],
}
DEFAULT_PARAMS = {"length": 14, "n_length": 4, "k_smoothing": 1, "d_length": 3, "level": 50.0}


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
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    vfast = st.rolling(int(p["k_smoothing"])).mean()
    vslow = vfast.rolling(int(p["d_length"])).mean()
    lvl = float(p["level"])
    c1, c2 = c.shift(1), c.shift(2)
    up_ = ((c2 < c1) & (c > c1) & (vfast < vslow) & (vfast > lvl)).to_numpy()
    dn_ = ((c2 > c1) & (c < c1) & (vfast > vslow) & (vfast < lvl)).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    k = int(p["n_length"])
    m = len(cv)
    sig = np.zeros(m)
    p123 = 0.0
    cnt = 0
    pp = 0.0
    for i in range(m):
        if up_[i]:
            p123 = 1.0
        elif dn_[i]:
            p123 = -1.0
        if i >= 1:
            if cv[i - 1] >= ov[i - 1]:
                cnt += 1
            elif cv[i - 1] < ov[i - 1]:
                cnt = 0
        if cnt >= k:
            pp = cv[i]
        nbu = 1.0 if pp > 0 else 0.0
        sig[i] = 1.0 if (p123 == 1.0 and nbu == 1.0) else 0.0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(sig == 1, index=ix), pd.Series(sig == 0, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
