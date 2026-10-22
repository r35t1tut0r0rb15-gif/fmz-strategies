"""EMA 8 / 12 / 24 crossings of the EMA 72 confirmed by the CCI 20, daily bars, entries only from flat: all three crossing over the EMA 72 on one bar with the CCI over 150 and the close over the EMA 72 goes long with a 1.5 % target and 0.5 % stop; all three within the last 2 bars goes long with a 0.5 % / 0.2 % bracket; the mirrors go short.
Port of FMZ strategy #468325 "EMA与CCI多重交叉趋势追踪策略-Multi-EMA-and-CCI-Crossover-Trend-Following-Strategy" (EMA & CCI Strategy).

FMZ source id: 468325

Source
    https://www.fmz.com/strategy/468325 (PineScript v5, FMZ last modified 2024-09-26 15:43:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 156-313), EMA 8 / 12 / 24 / 72; CCI 20, levels +-150; brackets 1.5 % / 0.5 % (one-bar crosses) and 0.5 % / 0.2 % (within 2 bars) of the entry price; cross indices cleared while a trade is open
    crossover(ema8 / 12 / 24, ema72) -> remember the bar;  all three this bar and cci > 150 and close > ema72 and flat -> entry Long_one;  all three within 2 bars ... -> entry Long_time
    long from Long_one: exit(limit = entry x 1.015, stop = entry x 0.995), clear the up crosses;  from Long_time: exit(limit = entry x 1.005, stop = entry x 0.998), clear;  shorts mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * A bar meeting the one-bar test also meets the 2-bar test; both entries are sent but the default
      pyramiding of 1 lets only the first (Long_one) fill, so the trade's bracket is the one-bar kind
      when that test holds and the 2-bar kind otherwise. The bracket comes from the entry (fill) price:
      ported active from the fill bar (#440797) as fixed fractions of the fill, chosen by the signal
      bar's kind, and followed in the loop so the from-flat entries and the clearing of the cross
      indices while a trade is open line up. ta.cci uses the mean absolute deviation. Opposite entries
      cannot occur (entries only from flat). Stop module: portfolio_kwargs {} (driver D4). Stops on
      daily bars: mark coarse_bar_stop. The 100 % of equity size is not ported. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the entry-price brackets as fixed fractions.
    2 generic: PASS, clustered EMA crossings with CCI confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_468325_ema8_12_24_cross_ema72_cci150_two_bracket_kinds_from_flat"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "max_wait": [2, 4],
    "cci_level": [150, 100],
}
DEFAULT_PARAMS = {"max_wait": 2, "cci_level": 150, "cci_len": 20,
                  "tp_one": 0.015, "sl_one": 0.005, "tp_time": 0.005, "sl_time": 0.002}


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


def _cci(c, n):
    sma = c.rolling(n).mean()
    dev = c.rolling(n).apply(lambda a: np.abs(a - a.mean()).mean(), raw=True)
    return (c - sma) / (0.015 * dev)


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    e72 = c.ewm(span=72, adjust=False).mean()
    es = [c.ewm(span=n, adjust=False).mean() for n in (8, 12, 24)]
    xu = [((e > e72) & (e.shift(1) <= e72.shift(1))).to_numpy() for e in es]
    xd = [((e < e72) & (e.shift(1) >= e72.shift(1))).to_numpy() for e in es]
    cci = _cci(c, int(p["cci_len"])).to_numpy()
    above, below = (c > e72).to_numpy(), (c < e72).to_numpy()
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    lvl, w = float(p["cci_level"]), float(p["max_wait"])
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    kind = np.zeros(m)                           # 1: one-bar bracket, 2: within-time bracket
    up, dn = [np.nan] * 3, [np.nan] * 3
    pos, pend, k_n, sl, tp = 0, 0, 0, np.nan, np.nan
    for i in range(m):
        if pend != 0:
            pos, pend = pend, 0
            s_f = p["sl_one"] if k_n == 1 else p["sl_time"]
            t_f = p["tp_one"] if k_n == 1 else p["tp_time"]
            sl = ov[i] * (1 - pos * s_f)
            tp = ov[i] * (1 + pos * t_f)
        if pos == 1 and (lv[i] <= sl or hv[i] >= tp):
            pos = 0                              # the bracket fills inside this bar
        elif pos == -1 and (hv[i] >= sl or lv[i] <= tp):
            pos = 0
        for j in range(3):
            if xu[j][i]:
                up[j] = i
            if xd[j][i]:
                dn[j] = i
        one_l = all(u == i for u in up)
        time_l = all(not np.isnan(u) and i - u <= w for u in up)
        one_s = all(d == i for d in dn)
        time_s = all(not np.isnan(d) and i - d <= w for d in dn)
        with np.errstate(invalid="ignore"):
            c_up, c_dn = cci[i] > lvl, cci[i] < -lvl
        if pos == 0:
            if (one_l or time_l) and c_up and above[i]:
                le[i], pend, k_n = True, 1, (1 if one_l else 2)
                kind[i] = k_n
            elif (one_s or time_s) and c_dn and below[i]:
                se[i], pend, k_n = True, -1, (1 if one_s else 2)
                kind[i] = k_n
        elif pos == 1:
            up = [np.nan] * 3                    # cleared while a long is open
        else:
            dn = [np.nan] * 3
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(se, index=ix), pd.Series(kind, index=ix)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _run(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    k = _run(bars_df, p)[2].shift(1)             # the signal bar's bracket kind, read at the fill
    sl = pd.Series(np.where(k == 1, p["sl_one"], np.where(k == 2, p["sl_time"], np.nan)), index=k.index)
    tp = pd.Series(np.where(k == 1, p["tp_one"], np.where(k == 2, p["tp_time"], np.nan)), index=k.index)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
