"""PowerZones, broker days, from flat: a down candle followed by five up candles, then a close over that candle's open, goes long with a target 1.5 zone heights over the close and a stop one zone height under the zone low; the mirror goes short.
Port of FMZ strategy #488909 "PowerZone交易策略-PowerZone-Trading-Strategy" (PowerZone Trading Strategy).

FMZ source id: 488909

Source
    https://www.fmz.com/strategy/488909 (PineScript v6, FMZ last modified 2025-03-31 17:34:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 142-233), periods 5; threshold 0 %; wicks off; TP 1.5, SL 1.0 zone heights; 100 % of equity
    close[6] < open[6] and the 5 bars since all up -> zone high = open[6], low = low[6];  flat and close > zone high -> entry BullPZ + exit(limit = close + 1.5 h, stop = low - 1.0 h)
    close[6] > open[6] and the 5 bars since all down -> zone high = high[6], low = open[6];  flat and close < zone low -> entry BearPZ + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The zone test counts the five bars before the signal bar; the move threshold 0 % always passes once
      the closes exist. The bracket is set on the signal bar and sent as fractions of the fill open (a
      level at or through it is marketable and closed one bar late, as #458256). Entries need a flat
      position at the bar's close, so a loop follows the bracket on each bar's high / low (as #449508).
      Opposite entries cannot occur (entries only from flat). Stop module: portfolio_kwargs {} (driver D4).
      Stops on daily bars: mark coarse_bar_stop. MPL 2.0 source (the notice is kept: Mozilla Public License
      2.0, © tradingbauhaus). Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; zone bracket as fractions of the fill.
    2 generic: PASS, order-block (PowerZone) breakouts with a zone bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_488909_powerzone5_breakout_zone_bracket_flat"
FAMILY = "order_block"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "periods": [5, 3],
    "tp_factor": [1.5, 3.0],
}
DEFAULT_PARAMS = {"periods": 5, "tp_factor": 1.5, "sl_factor": 1.0, "threshold": 0.0}


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
    n = int(p["periods"])
    ob = n + 1
    co, oo, ho, lw = c.shift(ob), o.shift(ob), h.shift(ob), lo.shift(ob)
    move = ((co - c.shift(1)) / co).abs() * 100 >= float(p["threshold"])
    ups = sum((c.shift(k) > o.shift(k)).astype(int) for k in range(1, n + 1))
    dns = sum((c.shift(k) < o.shift(k)).astype(int) for k in range(1, n + 1))
    bull = (co < oo) & (ups == n) & move
    bear = (co > oo) & (dns == n) & move
    b_hi, b_lo = oo, lw
    s_hi, s_lo = ho, oo
    lc = (bull & (c > b_hi)).to_numpy()
    sc = (bear & (c < s_lo)).to_numpy()
    bh, bl, sh, sl_ = (x.to_numpy(dtype=float) for x in (b_hi, b_lo, s_hi, s_lo))
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    kt, ks = float(p["tp_factor"]), float(p["sl_factor"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, tp_sent, side = np.full(m, np.nan), np.full(m, np.nan), np.zeros(m)
    pos, pend, sl, tp, sl_n, tp_n = 0, 0, np.nan, np.nan, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend, sl, tp = pend, 0, sl_n, tp_n
            through = (sl >= ov[i] or tp <= ov[i]) if pos == 1 else (sl <= ov[i] or tp >= ov[i])
            if through:                          # a level through the fill: closed at the next open
                if pos == 1:
                    lx[i] = True
                else:
                    sx[i] = True
                pend = 2
        elif pend == 2:
            pos, pend = 0, 0
        if pos == 1 and pend == 0 and (lv[i] <= sl or hv[i] >= tp):
            pos = 0                              # the bracket fills inside this bar
        elif pos == -1 and pend == 0 and (hv[i] >= sl or lv[i] <= tp):
            pos = 0
        if pos != 0 or pend != 0:
            continue
        if lc[i]:
            zh = bh[i] - bl[i]
            sl_n, tp_n = bl[i] - zh * ks, cv[i] + zh * kt
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
        elif sc[i]:
            zh = sh[i] - sl_[i]
            sl_n, tp_n = sh[i] + zh * ks, cv[i] - zh * kt
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
