"""One-bar "RSI" swings, daily bars, short only: the one-bar RSI is 100 on a close at or over the previous close and 0 under it, so the first up bar sells short and the first down bar covers; a short opened right after a down bar also gets a stop at the signal close.
Port of FMZ strategy #471694 "多周期RSI动量与三重EMA趋势跟踪复合策略-Multi-Period-RSI-Momentum-and-Triple-EMA-Trend-Following-Composite-Strategy" (Combined RSI Primed and 3 EMA Strategy).

FMZ source id: 471694

Source
    https://www.fmz.com/strategy/471694 (PineScript v5, FMZ last modified 2024-11-12 15:07:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-169), RSI of a single bar's change (100 if not down, else 0); levels 94 / 50 / 4; EMA 21 / 50 / 200; break-even stop at the close on an RSI cross over 50; the long branch never fires
    rsi > 94 and not inPositionShort -> entry Sell, flag;  rsi < 4 and flag -> close Sell, clear;  crossover(rsi, 50) and flag -> exit(Sell, stop = close)
    long branch: lastBearishClose set on the EMA-200 cross-down bar, tested on that same bar (close > itself never), then reset to na

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source's rsi() works on one bar only, so it is 100 or 0 and the levels 94 / 4 mean "up or flat
      bar" / "down bar". The long side can never trigger (its level is set and reset on the same bar,
      and close > close is false), as written. The break-even stop is set only when the bar that enters
      also crosses the RSI over 50 (a down bar before it): it is that bar's close, sent as a fraction of
      the fill open (a level at or under the fill open is marketable and closed one bar late). The flag
      is cleared only by the down-bar close, so after a stop-out the next entry waits for a down bar
      and then an up bar, as written. Short only. Stop module: portfolio_kwargs {} (driver D4). Stops on
      daily bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the break-even level as a fraction of the fill.
    2 generic: PASS, one-bar swing shorts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only: Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_471694_one_bar_rsi_up_bar_short_down_bar_cover"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {}
DEFAULT_PARAMS = {}


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


def _parts(bars_df):
    c = bars_df["close"]
    ch = c.diff()
    rsi = pd.Series(np.where(ch.isna(), np.nan, np.where(ch < 0, 0.0, 100.0)), index=c.index)
    up = (rsi > 94).to_numpy()
    dn = (rsi < 4).to_numpy()
    xo = ((rsi > 50) & (rsi.shift(1) <= 50)).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lvl = np.full(m, np.nan)
    flag = False
    for i in range(m):
        if up[i] and not flag:
            se[i], flag = True, True
            if xo[i]:
                lvl[i] = cv[i]                   # break-even stop at the signal close
        if dn[i] and flag:
            sx[i], flag = True, False
    ix = bars_df.index
    return pd.Series(se, index=ix), pd.Series(sx, index=ix), pd.Series(lvl, index=ix)


def simulate(bars_df, **params):
    se, sx, lvl = _parts(bars_df)
    o = bars_df["open"]
    sx = sx | (lvl.shift(1) <= o)                # stop at or under the fill open: closed at the next open
    false = pd.Series(False, index=bars_df.index)
    return false, false.copy(), se, sx


def stops(bars_df, **params):
    _, _, lvl = _parts(bars_df)
    f = lvl.shift(1) / bars_df["open"] - 1                    # the signal bar's level, read at the fill
    return {"sl_stop": f.where(f > 0)}


def portfolio_kwargs(**params):
    return {}
