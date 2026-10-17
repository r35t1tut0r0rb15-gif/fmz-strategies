"""HPotter combo, broker days: the 2/20 EMA state (the two-bar extreme beyond the EMA 14 against the previous close) and the
accelerator oscillator's WMA 15 zero cross (two bars back) must agree; both long holds a long, both short holds a short,
any disagreement closes everything.
Port of FMZ strategy #430896 "Dual Signal Trend Tracking Strategy" (Combo 2/20 EMA & Bill Awesome Oscillator (AC)).

FMZ source id: 430896

Source
    https://www.fmz.com/strategy/430896 (PineScript v5, FMZ last modified 2023-11-02 17:02:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 180-260), EMA 14; AC 5 / 34 with a WMA 15 signal
    EMA20: nXS = (min(low, low[1]) > ema or max(high, high[1]) < ema) ? min(low, low[1]) : max(high, high[1])
           pos = nXS > close[1] ? -1 : nXS < close[1] ? 1 : pos[1]
    AC: nRes = (sma(hl2, 5) - sma(hl2, 34)) - sma(that, 5); x = wma(nRes, 15)
        pos = x[2] < 0 and x[1] > 0 ? 1 : x[2] > 0 and x[1] < 0 ? -1 : pos[1]
    both 1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The WMA signal is the default (trading WMA on); the MA / EMA choices are off. "Trade reverse"
      defaults to false and the 2005 start is dropped.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA and oscillator states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430896 (2 members, best partner #438775, Jaccard 0.668); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430896_combo_2_20_ema_ac"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20],
    "wma_len": [15, 5],
}
DEFAULT_PARAMS = {"length": 14, "slow": 34, "fast": 5, "wma_len": 15}


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


def _hold(cond_up, cond_dn):
    m = len(cond_up)
    out = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if cond_up[i]:
            q = 1
        elif cond_dn[i]:
            q = -1
        out[i] = q
    return out


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: (a * w).sum() / w.sum(), raw=True)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ema = c.ewm(span=int(p["length"]), adjust=False).mean()
    hh = np.maximum(h, h.shift(1))
    ll = np.minimum(lo, lo.shift(1))
    nxs = ll.where((ll > ema) | (hh < ema), hh)
    c1 = c.shift(1)
    pos1 = _hold((nxs < c1).to_numpy() & ~(nxs > c1).to_numpy(), (nxs > c1).to_numpy())
    hl2 = (h + lo) / 2
    f = int(p["fast"])
    ao = hl2.rolling(f).mean() - hl2.rolling(int(p["slow"])).mean()
    x = _wma(ao - ao.rolling(f).mean(), int(p["wma_len"]))
    x1, x2 = x.shift(1), x.shift(2)
    pos2 = _hold(((x2 < 0) & (x1 > 0)).to_numpy(), ((x2 > 0) & (x1 < 0)).to_numpy())
    tgt = np.where((pos1 == 1) & (pos2 == 1), 1, np.where((pos1 == -1) & (pos2 == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
