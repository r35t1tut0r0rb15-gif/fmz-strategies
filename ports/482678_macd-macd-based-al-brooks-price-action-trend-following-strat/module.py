"""The close above the SMA 52 with MACD above zero and its signal goes long (mirrored short), with a 1 % stop and a
2 R target, closed on any bar where neither side holds, daily bars.
Port of FMZ strategy #482678 "MACD结合阿尔布鲁克斯价格行为的趋势跟踪策略-MACD-Based-Al-Brooks-Price-Action-Trend-Following-Strategy" (Al Brooks Price Action with MACD Signals).

FMZ source id: 482678

Source
    https://www.fmz.com/strategy/482678 (PineScript v6, FMZ last modified 2025-02-19 17:36:15).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 111-149), SMA 52, MACD 12 / 26 / 9, buffer 0.01, RR 2, price = close
    buy = close > sma and macd > 0 and macd > signal -> entry long with exit(stop = close x 0.99,
    limit = close + 2 (close - stop)); sell mirrored -> entry short
    neither buy nor sell -> close both

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "in %" buffer 0.01 is used as a fraction: a 1 % stop and a 2 % target.
    * buy / sell are states, so every bar in them re-issues the exit from the current close (a moving level): fixed
      at the entry from the signal close (re-based on the fill); mark trailing_stop_pending.
    * The closes run on bars where neither state holds, so they never meet an entry. simulate() mirrors the house
      bracket from the fill (as #430254) so a close after a stop exit is not emitted, and re-enters on the next bar
      in the state after a stop (as Pine would). candleType "Open" is a GRID variant.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-issued bracket fixed at entry (marked).
    2 generic: PASS, an SMA, MACD and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482678_sma52_macd_state_pct_bracket"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "candle": ["close", "open"],
    "sl_buffer": [0.01, 0.02],
}
DEFAULT_PARAMS = {"length": 52, "rr": 2.0, "sl_buffer": 0.01, "candle": "close"}


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


def _run(bars_df, p):
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    c = bars_df["close"]
    sma = c.rolling(int(p["length"])).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    price = bars_df[p["candle"]]
    buy = ((price > sma) & (macd > 0) & (macd > sig)).to_numpy()
    sell = ((price < sma) & (macd < 0) & (macd < sig)).to_numpy()
    sl, tp = p["sl_buffer"], p["sl_buffer"] * p["rr"]
    m = len(o)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:                 # house bracket from the fill price
            e = o[entry_i]
            if pos == 1 and (lo[i] <= e * (1 - sl) or h[i] >= e * (1 + tp)):
                pos = 0
            elif pos == -1 and (h[i] >= e * (1 + sl) or lo[i] <= e * (1 - tp)):
                pos = 0
        if buy[i] and pos != 1 and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
        elif sell[i] and pos != -1 and i + 1 < m:
            se[i], pos, entry_i = True, -1, i + 1
        elif not buy[i] and not sell[i] and pos != 0:
            (lx if pos == 1 else sx)[i] = True
            pos = 0
    return le, lx, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    return tuple(pd.Series(a, index=idx) for a in _run(bars_df, p))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_buffer"], "tp_stop": p["sl_buffer"] * p["rr"]}


def portfolio_kwargs(**params):
    return {}
