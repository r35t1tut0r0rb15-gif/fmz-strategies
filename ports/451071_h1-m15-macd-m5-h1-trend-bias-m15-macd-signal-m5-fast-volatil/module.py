"""MACD (12, 26, 9) of the day's last 15-minute close, daily bars: long while the MACD is above its signal, short while below; longs carry a 1.5 % target and a 0.5 % stop from the fill, while the short's
bracket reuses the long's levels on the wrong side, so each short closes at the next open after its fill and re-enters; reversing.
Port of FMZ strategy #451071 "H1趋势偏差M15-MACD信号M5快速波动率缺口策略-H1-Trend-Bias-M15-MACD-Signal-M5-Fast-Volatility-Gap-Strategy" (H1 Bias + M15 MSS + M5 FVG).

FMZ source id: 451071

Source
    https://www.fmz.com/strategy/451071 (PineScript v5, FMZ last modified 2024-05-11 17:21:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-145), MACD 12 / 26 / 9 on the 15-minute close; H1 SMA 50 (plot only); ATR filter > 0.001; TP 15 % / SL 5 % divided by leverage 10; 10 % of equity
    macd > signal and atr > 0.001 -> entry Long;  macd < signal and atr > 0.001 -> entry Short;  closes on the opposite state
    exit(Long, limit = avg x 1.015, stop = avg x 0.995);  exit(Short, same levels)  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 15-minute request on a daily chart returns the day's last 15-minute close (as #436765),
      which is the daily close, so the MACD runs on daily closes; the ATR test is always true on BTC.
      The long bracket comes from the average price (na while flat): tp_stop 0.015, sl_stop 0.005 of
      the fill (as #440797). For a short the same levels are a buy limit above and a buy stop under the
      price, on the wrong side, so the short closes at the first open after its fill bar and the level
      signal re-enters on the next bar, as written (as #439872). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Daily stop module: mark coarse_bar_stop. The 10 % of equity
      size is sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the 15-minute value ends with the daily bar; the long bracket from the fill; the short's wrong-side levels read as a close.
    2 generic: PASS, MACD state with a percent bracket on longs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 10 % of equity size and leverage-scaled percents stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_451071_daily_macd_state_long_bracket_short_churn_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.015, 0.03],
    "sl": [0.005, 0.01],
}
DEFAULT_PARAMS = {"tp": 0.015, "sl": 0.005}


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
    m15 = df["close"].resample("15min", label="left", closed="left").last().dropna()
    bars["c15"] = m15.groupby(broker_day(m15.index)).last()          # the day's last 15-minute close
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _run(bars_df):
    c15 = bars_df["c15"]
    macd = c15.ewm(span=12, adjust=False).mean() - c15.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    lc = (macd > sig).to_numpy()
    sc = (macd < sig).to_numpy()
    m = len(lc)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    short_held = False
    for i in range(m):
        if short_held:
            sx[i], short_held = True, False          # wrong-side levels: out at the next open
        elif sc[i]:
            se[i], short_held = True, True           # filled at the next open
    return lc, se, sx


def simulate(bars_df, **params):
    lc, se, sx = _run(bars_df)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(lc, index=ix), false, pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lc, _, _ = _run(bars_df)
    ix = bars_df.index
    on = pd.Series(lc, index=ix)
    return {"sl_stop": pd.Series(float(p["sl"]), index=ix).where(on).shift(1),
            "tp_stop": pd.Series(float(p["tp"]), index=ix).where(on).shift(1)}


def portfolio_kwargs(**params):
    return {}
