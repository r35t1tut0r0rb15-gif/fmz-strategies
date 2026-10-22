"""Close crossings of the EMA 9 on the same bar as a MACD signal crossing, 2-day bars: both crossing up goes long with a stop at the 5-bar low, both down goes short with a stop at the 5-bar high; the 3.5 R target is taken from the price of the position held at the signal (none from flat); reversing.
Port of FMZ strategy #478727 "双重交叉趋势追踪策略指数均线与MACD协同交易系统-Dual-Crossover-Trend-Following-Strategy-EMA-and-MACD-Synergistic-Trading-System" (MACD + EMA9 3 h).

FMZ source id: 478727

Source
    https://www.fmz.com/strategy/478727 (PineScript v6, FMZ last modified 2025-01-17 16:06:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-197), EMA 9; MACD 12 / 26 / 9; stop at the 5-bar low / high; TP 3.5 R from strategy.position_avg_price; 200 % of equity
    crossover(close, ema9) and crossover(macd, signal) -> close Sell, entry Buy, exit(stop = lowest(low, 5), limit = avg + 3.5 (avg - stop));  mirror -> close Buy, entry Sell, exit(stop = highest(high, 5), limit = avg - 3.5 (stop - avg))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the signal bar's 5-bar low (high). The target uses strategy.position_avg_price, which
      on the signal bar is still the price of the position held then: na from flat (no target), and the
      replaced position's fill price on a reversal, as written (as #473147); a loop tracks those prices.
      The levels are sent as fractions of the new fill open (a level at or through it is marketable and
      closed one bar late). A repeat signal while held re-sends the exit from that position's own price,
      which is not followed (as #437800, mark trailing_stop_pending). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. The 200 %
      of equity size is sizing. 2-day bars are blocks of two broker days. FREQ = "2D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the replaced position's price as the target base, as written.
    2 generic: PASS, EMA and MACD joint crossings with a swing stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_478727_close_cross_ema9_macd_cross_swing5_stop_reversal"
FAMILY = "macd"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [5, 10],
    "risk_mult": [3.5, 2.0],
}
DEFAULT_PARAMS = {"lookback": 5, "risk_mult": 3.5, "ema_len": 9, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    lc = ((c > e) & (c.shift(1) <= e.shift(1)) & (macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    sc = ((c < e) & (c.shift(1) >= e.shift(1)) & (macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    k = int(p["lookback"])
    ll = lo.rolling(k).min().to_numpy(dtype=float)
    hh = h.rolling(k).max().to_numpy(dtype=float)
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    rm = float(p["risk_mult"])
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
            sl_n = ll[i]
            tp_n = avg + rm * (avg - sl_n)               # na from flat
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
        elif sc[i] and pos != -1:
            sl_n = hh[i]
            tp_n = avg - rm * (sl_n - avg)
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
