"""Closes back through the SMA 20 of highs / lows with a significant slope, daily bars: a close over a rising SMA of highs after a close under it goes long, the mirror under a falling SMA of lows goes short; reversing. Each trade's stop is 1 % beyond its signal close and its target 5 % from strategy.position_avg_price on the signal bar (na from flat, the replaced position's price on a reversal), as written.
Port of FMZ strategy #473321 "Dynamic Dual SMA Trend Following Strategy with Smart Risk Management" (SMA Buy/Sell Strategy with Significant Slope).

FMZ source id: 473321

Source
    https://www.fmz.com/strategy/473321 (PineScript v5, FMZ last modified 2024-11-29 11:06:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-140), SMA 20 of high / low; slope over 5 bars > 0.05 %; target 5 % of avg, stop 1 % of close, sent on signal bars
    buy = close > smaH and low < smaH and close[1] < smaH and smaH rising significantly;  long and sell -> close Buy;  short and buy -> close Sell;  buy -> entry Buy, exit(limit = avg x 1.05, stop = close x 0.99);  sell -> entry Sell, exit(limit = avg x 0.95, stop = close x 1.01)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on the signal bar only: the stop from that bar's close, the target from
      strategy.position_avg_price, which is na from flat (no target) and the replaced position's fill
      price on a reversal, as written (as #468309, #473147). The loop tracks those fill prices and the
      bracket inside each bar; the levels are sent as fractions of the new fill open (a level at or
      through it is marketable and closed one bar late). A repeat signal inside a trade re-sends the
      bracket from its own close: the opening levels are kept (as #434428, mark trailing_stop_pending).
      The closes on opposite signals repeat the reversals. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the replaced position's price as the target base, as written.
    2 generic: PASS, SMA-of-extremes re-crossings with a slope filter and a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_473321_sma20_high_low_slope_recross_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sma_period": [20, 50],
    "tp_pct": [0.05, 0.10],
    "sl_pct": [0.01, 0.02],
}
DEFAULT_PARAMS = {"sma_period": 20, "tp_pct": 0.05, "sl_pct": 0.01, "slope_pct": 0.05}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["sma_period"])
    sh, sl_ = h.rolling(n).mean(), lo.rolling(n).mean()
    th = float(p["slope_pct"]) / 100

    def sig(s):
        return (s - s.shift(5)).abs() / s.shift(5) > th

    buy = (c > sh) & (lo < sh) & (c.shift(1) < sh) & (sh > sh.shift(1)) & sig(sh)
    sell = (c < sl_) & (h > sl_) & (c.shift(1) > sl_) & (sl_ < sl_.shift(1)) & sig(sl_)
    lc, sc = buy.to_numpy(), sell.to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    slp, tpp = float(p["sl_pct"]), float(p["tp_pct"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, tp_sent, side = np.full(m, np.nan), np.full(m, np.nan), np.zeros(m)
    pos, pend, avg, sl, tp, sl_n, tp_n = 0, 0, np.nan, np.nan, np.nan, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend, avg, sl, tp = pend, 0, ov[i], sl_n, tp_n
            through = (sl >= ov[i] or tp <= ov[i]) if pos == 1 else (sl <= ov[i] or tp >= ov[i])
            if through:                          # a level through the fill: closed at the next open
                if pos == 1:
                    lx[i] = True
                else:
                    sx[i] = True
                pend, sl, tp = 2, np.nan, np.nan
        elif pend == 2:
            pos, pend, avg, sl, tp = 0, 0, np.nan, np.nan, np.nan
        if pos == 1 and (lv[i] <= sl or hv[i] >= tp):
            pos, avg, sl, tp = 0, np.nan, np.nan, np.nan     # the bracket fills inside this bar
        elif pos == -1 and (hv[i] >= sl or lv[i] <= tp):
            pos, avg, sl, tp = 0, np.nan, np.nan, np.nan
        if pend == 2:
            continue
        if lc[i] and pos != 1:
            sl_n, tp_n = cv[i] * (1 - slp), avg * (1 + tpp)  # target na from flat
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
        elif sc[i] and pos != -1:
            sl_n, tp_n = cv[i] * (1 + slp), avg * (1 - tpp)
            se[i], pend, sl_sent[i], tp_sent[i], side[i] = True, -1, sl_n, tp_n, -1
    ix = bars_df.index
    return [pd.Series(x, index=ix) for x in (le, lx, se, sx, sl_sent, tp_sent, side)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return tuple(_run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_l, tp_l, sd = _run(bars_df, p)[4:]
    o = bars_df["open"]
    sl_l, tp_l, sd = sl_l.shift(1), tp_l.shift(1), sd.shift(1)    # the signal bar's levels, read at the fill
    sl_f = (1 - sl_l / o).where(sd > 0, sl_l / o - 1)
    tp_f = (tp_l / o - 1).where(sd > 0, 1 - tp_l / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
