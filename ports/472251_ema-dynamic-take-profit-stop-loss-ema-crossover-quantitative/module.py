"""EMA 10 / 26 crossings one trade at a time, daily bars: the cross up goes long and the cross down short, each with a 30-pip target and 10-pip stop from the signal close; a close beyond either level ends the trade flag, and only then can a new signal trade; reversing.
Port of FMZ strategy #472251 "EMA双均线交叉动态止盈止损量化交易策略-Dynamic-Take-Profit-Stop-Loss-EMA-Crossover-Quantitative-Trading-Strategy" (30 Pips Target & 15 Pips Stop-Loss with One Signal at a Time).

FMZ source id: 472251

Source
    https://www.fmz.com/strategy/472251 (PineScript v5, FMZ last modified 2024-11-18 15:53:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-178), EMA 10 / 26; pip = mintick x 10; target 30, stop 10 pips (price units); inTrade flag cleared by close tests
    inTrade: close >= long target or <= long stop -> close Long, clear;  close <= short target or >= short stop -> close Short, clear
    not inTrade: crossover -> long levels, entry Long + exit(limit, stop), inTrade;  crossunder -> short levels, entry Short + exit, inTrade

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pips are mintick x 10 = 1.0 in price: 30 / 10 price units, ported as fractions of 42000 of the
      signal close (0.000714 / 0.000238), and the bracket as those fractions of the fill. The flag is
      cleared only by the close tests (also when the bracket already filled inside an earlier bar), so
      new signals wait for a close beyond a level, as written; the close tests are sent as bar-close
      exits. A same-side signal on the bar a trade closes would continue the trade with a new bracket,
      which is not followed (the trade simply ends there). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the pip bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with a pip bracket, one trade at a time.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_472251_ema10_26_cross_pip_bracket_one_trade_flag"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_frac": [0.000714, 0.02],
    "sl_frac": [0.000238, 0.01],
}
DEFAULT_PARAMS = {"tp_frac": 0.000714, "sl_frac": 0.000238}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a, b = c.ewm(span=10, adjust=False).mean(), c.ewm(span=26, adjust=False).mean()
    xo = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    xu = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    tp, sl = float(p["tp_frac"]), float(p["sl_frac"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    in_trade = False
    lt = ls = st = ss = np.nan
    for i in range(m):
        if in_trade:
            if cv[i] >= lt or cv[i] <= ls:
                in_trade, lx[i] = False, True
                lt = ls = np.nan
            if cv[i] <= st or cv[i] >= ss:
                in_trade, sx[i] = False, True
                st = ss = np.nan
        if not in_trade:
            if xo[i]:
                lt, ls = cv[i] * (1 + tp), cv[i] * (1 - sl)
                le[i], in_trade = True, True
            if xu[i]:
                st, ss = cv[i] * (1 - tp), cv[i] * (1 + sl)
                se[i], in_trade = True, True
    lx &= ~(le | se)                             # a new entry on the closing bar takes its place
    sx &= ~(le | se)
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_frac"]), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
