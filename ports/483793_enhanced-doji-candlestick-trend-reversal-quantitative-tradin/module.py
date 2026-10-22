"""Doji candles (body at most 30 % of the range) with a bullish or bearish confirming candle on the bar or the bar before, 2-day bars: a doji with a bullish confirmation goes long, with a bearish one goes short, each with a 5-tick stop (read as a fraction) and a 2R target from the signal close; a doji while in a trade closes it.
Port of FMZ strategy #483793 "Enhanced Doji Candlestick Trend Reversal Quantitative Trading Strategy" (Enhanced Doji Candle Strategy).

FMZ source id: 483793

Source
    https://www.fmz.com/strategy/483793 (PineScript v5, FMZ last modified 2025-02-27 16:33:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 177-229), doji threshold 0.3; stop 5 pips (ticks); RR 2; SMA 20 (plot only); 10 % of equity
    doji and (bullConfirm or bullConfirm[1]) -> entry Buy + exit(stop = close - 5 ticks, limit = close + 10 ticks);  doji and (bearConfirm or bearConfirm[1]) -> entry Sell + mirror
    doji -> close Buy, close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The doji close calls act on the trade held at the bar's close: a long held on a doji bar is closed
      (its repeated Buy entry adds nothing) unless a Sell is called on the same bar, which reverses it;
      likewise for shorts. Followed in a loop with the bracket checked on each bar's high / low (as
      449508). The SMA trend lines feed nothing.
    * Criterion 2: 5 ticks on the header's ETH_USDT (tick 0.01, about 3000 USDT) is read as 1.667e-05 of
      the price (as #458242 at the header's prices); the levels are fixed at the signal close and sent as
      fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than
      1 hour: mark coarse_bar_stop. The 10 % of equity size is sizing. Bars are blocks of two broker days
      (17:00 America/New_York) counted from 1970-01-01, stamped with their first minute. FREQ = "2D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; tick bracket as fractions of the fill.
    2 generic: ADAPT, 5-tick stop read as a fraction at ETH 3000.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_483793_doji_confirm_tick_stop_2r_doji_close_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_frac": [1.667e-05, 0.005],
    "risk_reward": [2.0, 3.0],
}
DEFAULT_PARAMS = {"stop_frac": 1.667e-05, "risk_reward": 2.0, "doji_threshold": 0.3, "days": 2}


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


def _plan(bars_df, p):
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    doji = ((c - o).abs() <= (h - lo) * float(p["doji_threshold"])).to_numpy()
    bc = (c > o) & (lo >= o * 0.99)
    sc = (c < o) & (h <= o * 1.01)
    bull = (bc | bc.shift(1, fill_value=False)).to_numpy()
    bear = (sc | sc.shift(1, fill_value=False)).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    a = float(p["stop_frac"])
    b = a * float(p["risk_reward"])
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    sl_lv, tp_lv = np.full(m, np.nan), np.full(m, np.nan)
    pos, pend, out_pend = 0, 0, False
    sl = tp = np.nan
    for i in range(m):
        if out_pend:
            pos, out_pend = 0, False
        if pend != 0:
            pos, pend = pend, 0
            sl, tp = sl_lv[i - 1], tp_lv[i - 1]
            if (pos > 0 and (sl >= ov[i] or tp <= ov[i])) or (pos < 0 and (sl <= ov[i] or tp >= ov[i])):
                if pos > 0:
                    lx[i] = True
                else:
                    sx[i] = True
                out_pend = True               # marketable at the fill: closed one bar late
        if pos != 0 and not out_pend:
            if (pos > 0 and (lv[i] <= sl or hv[i] >= tp)) or (pos < 0 and (hv[i] >= sl or lv[i] <= tp)):
                pos = 0                       # the bracket closes it inside the bar
        if not doji[i] or out_pend:
            continue
        go_l = bull[i] and pos <= 0
        go_s = bear[i] and pos >= 0
        if go_s:
            se[i], pend = True, -1
            sl_lv[i], tp_lv[i] = cv[i] * (1 + a), cv[i] * (1 - b)
        elif go_l:
            le[i], pend = True, 1
            sl_lv[i], tp_lv[i] = cv[i] * (1 - a), cv[i] * (1 + b)
        if pos > 0 and not go_s:
            lx[i], out_pend = True, True
        if pos < 0 and not go_l:
            sx[i], out_pend = True, True
    idx = c.index
    S = lambda arr: pd.Series(arr, index=idx)  # noqa: E731
    return S(le), S(lx), S(se), S(sx), S(sl_lv), S(tp_lv)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, _, _ = _plan(bars_df, p)
    return le, lx & ~le & ~se, se, sx & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, se, _, sl_lv, tp_lv = _plan(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - sl_lv.shift(1) / o, tp_lv.shift(1) / o - 1
    s_sl, s_tp = sl_lv.shift(1) / o - 1, 1 - tp_lv.shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
