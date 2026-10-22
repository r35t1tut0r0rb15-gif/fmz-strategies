"""Eight Ichimoku (9 / 26 / 52, displacement 26) bullish checks, broker days: all eight bullish goes long (closing a short), none bullish goes short (closing a long); reversing.
Port of FMZ strategy #490795 "Multi Signal Convergence Cloud Edge Breakout Strategy" (CloudEdge).

FMZ source id: 490795

Source
    https://www.fmz.com/strategy/490795 (PineScript v6, FMZ last modified 2025-04-16 15:24:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 189-283), Ichimoku 9 / 26 / 52 / 26; thresholds 8 / 0
    signals: close > close[26]; close > tenkan; tenkan > kijun; chikou / tenkan, chikou / kijun, tenkan / kijun, chikou / kumo edges, senkou A / B: barssince(cross up) < barssince(cross down)
    count >= 8 -> entry Long, close Short;  count <= 0 -> entry Short, close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The chikou span is close[26] and the kumo edges are the spans 26 bars back, as written. barssince of
      a crossing that never happened is na, and the comparison is then false. The conditions are states;
      each entry reverses the other (REVERSAL INTENDED). No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku consensus states.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
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

NAME = "fmz_490795_ichimoku_eight_check_consensus_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bullishThreshold": [8, 7],
    "bearishThreshold": [0, 1],
}
DEFAULT_PARAMS = {"bullishThreshold": 8, "bearishThreshold": 0, "tenkan": 9, "kijun": 26, "senkouB": 52,
                  "displacement": 26}


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


def _since(cond):
    """ta.barssince: bars since cond was last true (na before the first time)."""
    v = cond.to_numpy()
    out = np.full(len(v), np.nan)
    last = -1
    for i in range(len(v)):
        if v[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def mid(n):
        return (h.rolling(int(n)).max() + lo.rolling(int(n)).min()) / 2

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    def earlier_up(up, dn):
        su, sd = _since(up), _since(dn)
        with np.errstate(invalid="ignore"):
            return su < sd

    d = int(p["displacement"])
    tk, kj = mid(p["tenkan"]), mid(p["kijun"])
    sa, sb = (tk + kj) / 2, mid(p["senkouB"])
    ch = c.shift(d)
    ku = pd.concat([sa.shift(d), sb.shift(d)], axis=1).max(axis=1, skipna=False)
    kl = pd.concat([sa.shift(d), sb.shift(d)], axis=1).min(axis=1, skipna=False)
    sigs = [
        (c > c.shift(d)).to_numpy(),
        (c > tk).to_numpy(),
        (tk > kj).to_numpy(),
        earlier_up(xo(ch, tk), xo(tk, ch)),
        earlier_up(xo(ch, kj), xo(kj, ch)),
        earlier_up(xo(tk, kj), xo(kj, tk)),
        earlier_up(xo(ch, ku), xo(kl, ch)),
        earlier_up(xo(sa, sb), xo(sb, sa)),
    ]
    count = pd.Series(np.sum(np.vstack(sigs).astype(int), axis=0), index=c.index)
    le = count >= int(p["bullishThreshold"])
    se = (count <= int(p["bearishThreshold"])) & ~le
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
