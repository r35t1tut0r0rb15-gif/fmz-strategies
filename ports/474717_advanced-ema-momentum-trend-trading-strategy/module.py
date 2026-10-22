"""Momentum crossings with the EMA 200 trend, 2-day bars, entries only from flat: the 10-bar momentum crossing over +5 with the close over the EMA 200 buys, crossing under -5 with the close under it sells, each with a 1 % stop and 2 % target from the signal close.
Port of FMZ strategy #474717 "Advanced EMA Momentum Trend Trading Strategy" ([Mustang Algo] Mom Strategy).

FMZ source id: 474717

Source
    https://www.fmz.com/strategy/474717 (PineScript v6, FMZ last modified 2024-12-11 17:50:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-269), momentum length 10, filters +5 / -5 (price units); EMA 200 on; time filter off; stop 1 %, TP ratio 2; 2 trades a day
    crossover(close - close[10], 5) and close > ema200 and flat -> entry Long, exit(stop = close - 1 %, limit = close + 2 %);  crossunder(close - close[10], -5) and close < ema200 and flat -> entry Short, exit(stop = close + 1 %, limit = close - 2 %)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The +5 / -5 momentum filters are price amounts, ported as fractions of 42000 of the close
      (0.000119). The momentum timeframe "" is the chart. The daily trade count resets whenever the day
      of week changes, which on 2-day bars is every bar, so the limit feeds nothing; the time filter is
      off. Entries only from flat: a loop follows each trade's bracket on the bar's high / low so the
      flat gate lines up (as 449508); the levels are sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late). The two crossings cannot hold on one bar.
      Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). Stops on 2-day bars:
      mark coarse_bar_stop. The fixed contract size is not ported. FREQ = "2D" from the backtest header
      (blocks of 2 broker days, as #429148).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, momentum threshold crossings with an EMA filter and a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: fixed contract size stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (time filter off).
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_474717_momentum10_cross_ema200_pct_bracket_from_flat"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "len": [10, 20],
    "stop_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"len": 10, "stop_pct": 1.0, "tp_ratio": 2.0, "mom_frac": 0.000119, "ema_len": 200, "days": 2}


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
    mom = (c - c.shift(int(p["len"]))) / c        # momentum against a threshold in fractions of the close
    th = float(p["mom_frac"])
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    lc = ((mom > th) & (mom.shift(1) <= th) & (c > e)).to_numpy()
    sc = ((mom < -th) & (mom.shift(1) >= -th) & (c < e)).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    slf = float(p["stop_pct"]) / 100
    tpf = slf * float(p["tp_ratio"])
    m = len(ov)
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
                pend, sl, tp = 2, np.nan, np.nan
        elif pend == 2:
            pos, pend, sl, tp = 0, 0, np.nan, np.nan
        if pos == 1 and (lv[i] <= sl or hv[i] >= tp):
            pos, sl, tp = 0, np.nan, np.nan      # the bracket fills inside this bar
        elif pos == -1 and (hv[i] >= sl or lv[i] <= tp):
            pos, sl, tp = 0, np.nan, np.nan
        if pend != 0 or pos != 0:
            continue
        if lc[i]:
            sl_n, tp_n = cv[i] * (1 - slf), cv[i] * (1 + tpf)
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
        elif sc[i]:
            sl_n, tp_n = cv[i] * (1 + slf), cv[i] * (1 - tpf)
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
