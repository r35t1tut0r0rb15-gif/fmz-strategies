"""123 reversal and rescaled-RSI histogram combination, broker days: the 123 reversal state (two closes against a stochastic 14 test) and the (RSI 13 - 50) x 1.5 state (above -10 long, else short) agreeing long go
long, agreeing short go short, disagreeing close all; reversing.
Port of FMZ strategy #437673 "双重反转RSI历史警报策略Dual-Reversion-RSI-HistoAlert-Strategy" (Combo Backtest 123 Reversal & RSI HistoAlert).

FMZ source id: 437673

Source
    https://www.fmz.com/strategy/437673 (PineScript v4, FMZ last modified 2024-01-04 17:17:24).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 191-232), 123: length 14, K smoothing 1, D 3, level 50; RSI 13, levels -10 / 10, modifier 1.5; reverse off
    RSI_Hist: RSIMain = (rsi(close, 13) - 50) x 1.5;  pos = 1 if RSIMain > -10, -1 if RSIMain < 10, else pos[1]  (overlapping levels, as #437029)
    Reversal123 as in the combo family;  agree -> entry, else close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The RSI levels overlap as written (above -10 long, at or under -10 short). The 123 test is read as
      written. The state is a level, so the entry is sent on every bar of the state; state 0 closes.
      REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close patterns, stochastic and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_437673_reversal123_rsi_histo_combo"
FAMILY = "reversal_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 9],
    "rsi_period": [13, 21],
}
DEFAULT_PARAMS = {"length": 14, "rsi_period": 13, "k_smoothing": 1, "d_length": 3, "level": 50.0,
                  "buy_level": -10.0, "sell_level": 10.0, "modify": 1.5, "reverse": False}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
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
    main = ((_rsi(c, int(p["rsi_period"])) - 50) * float(p["modify"])).to_numpy()
    b, s = float(p["buy_level"]), float(p["sell_level"])
    m = len(c)
    sig = np.zeros(m)
    p123 = pr = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if up_[i]:
                p123 = 1.0
            elif dn_[i]:
                p123 = -1.0
            if main[i] > b:
                pr = 1.0
            elif main[i] < s:
                pr = -1.0
            sig[i] = 1.0 if (p123 == 1.0 and pr == 1.0) else (-1.0 if (p123 == -1.0 and pr == -1.0) else 0.0)
    if p["reverse"]:
        sig = -sig
    ix = bars_df.index
    flat = pd.Series(sig == 0, index=ix)
    return pd.Series(sig == 1, index=ix), flat, pd.Series(sig == -1, index=ix), flat.copy()


def portfolio_kwargs(**params):
    return {}
