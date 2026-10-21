"""Rescaled RSI histogram state, broker days: (RSI 13 - 50) x 1.5 above -10 is long, otherwise (at or under -10, which is under +10) short; an optional switch trades the reverse; entries are sent on every bar
of the state, reversing.
Port of FMZ strategy #437029 "RSI指标改进交易策略RSI-Indicator-Improvement-Trading-Strategy" (RSI HistoAlert Strategy).

FMZ source id: 437029

Source
    https://www.fmz.com/strategy/437029 (PineScript v2, FMZ last modified 2023-12-29 16:23:48).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 177-196), RSI 13, buy level -10, sell level 10, modifier 1.5, reverse off
    RSIMain = (rsi(close, 13) - 50) x 1.5;  pos = 1 if RSIMain > -10, -1 if RSIMain < 10, else pos[1];  possig = -pos when reverse;  entry Long / Short on possig

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two tests overlap as written: any value above -10 is long, the rest (at or under -10) short; the
      hold branch can only act while the RSI is undefined. The state is a level, so the entry is sent on
      every bar of the state; a same-side entry while in the position is ignored (pyramiding 0). REVERSAL
      INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels.
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

NAME = "fmz_437029_rsi_histo_level_state"
FAMILY = "rsi_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [13, 21],
    "buy_level": [-10.0, 0.0],
}
DEFAULT_PARAMS = {"period": 13, "buy_level": -10.0, "sell_level": 10.0, "modify": 1.5, "reverse": False}


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
    main = ((_rsi(bars_df["close"], int(p["period"])) - 50) * float(p["modify"])).to_numpy()
    b, s = float(p["buy_level"]), float(p["sell_level"])
    m = len(main)
    pos = np.zeros(m)
    prev = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if main[i] > b:
                prev = 1.0
            elif main[i] < s:
                prev = -1.0
            pos[i] = prev
    sig = -pos if p["reverse"] else pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(sig == 1, index=ix), false, pd.Series(sig == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
