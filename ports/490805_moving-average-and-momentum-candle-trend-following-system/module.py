"""Momentum candles (a body larger than the previous one) on the side of the SMA 200, broker days, from flat: a bullish one above goes long, a bearish one below goes short, each with a 50-pip stop and 100-pip target from the signal close (read as 2.5 % / 5 %).
Port of FMZ strategy #490805 "Moving Average and Momentum Candle Trend Following System" (MA200 + Momentum Candle Strategy (No Duplicate Entry)).

FMZ source id: 490805

Source
    https://www.fmz.com/strategy/490805 (PineScript v5, FMZ last modified 2025-04-16 16:01:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 172-219), SMA 200; SL 50 pips, TP 100 pips (pip = mintick x 10); 10 % of equity
    close > open and body > body[1] and close > sma200 and no open trade -> entry Buy + exit(stop = close - 50 pips, limit = close + 100 pips);  mirror -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pip distances (mintick x 10) are read as percents at the header coin's price (TRX about 0.2 with
      tick 0.00001: 50 pips = 0.005 = 2.5 %, 100 pips = 5 %; C2 ADAPT, as #458242). The bracket is set on the
      signal bar and sent as fractions of the fill open (a level at or through it is marketable and closed
      one bar late, as #458256). Entries need no open trade at the bar's close, so a loop follows the
      bracket on each bar's high / low (as #449508). Opposite entries cannot occur (entries only from flat).
      Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; pip bracket as fractions of the fill.
    2 generic: ADAPT, pip distances read as percents at the header price.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_490805_momentum_candle_sma200_side_pip_bracket_flat"
FAMILY = "candlestick_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [2.5, 5.0],
    "maLength": [200, 100],
}
DEFAULT_PARAMS = {"sl_pct": 2.5, "maLength": 200}


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
    ma = c.rolling(int(p["maLength"])).mean()
    body = (c - o).abs()
    big = body > body.shift(1)
    lc = ((c > o) & big & (c > ma)).to_numpy()
    sc = ((c < o) & big & (c < ma)).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    q = float(p["sl_pct"]) / 100
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
            sl_n, tp_n = cv[i] * (1 - q), cv[i] * (1 + 2 * q)
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
        elif sc[i]:
            sl_n, tp_n = cv[i] * (1 + q), cv[i] * (1 - 2 * q)
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
