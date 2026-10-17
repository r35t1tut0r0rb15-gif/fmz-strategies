"""SMA 5 / 21 crosses with a percentage bracket, long only, three-day bars: SMA 5 crossing above SMA 21 goes long,
crossing below closes it; a 1 % stop and a 2 % target (re-placed every bar in the source, fixed at entry here).
Port of FMZ strategy #489158 "高级双均线策略交叉交易系统-Advanced-Dual-Moving-Average-Crossover-Trading-System" (Intraday MA Crossover Strategy).

FMZ source id: 489158

Source
    https://www.fmz.com/strategy/489158 (PineScript v5, FMZ last modified 2025-04-02 11:35:32).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 211-252), SMA 5 / 21, SL 1 %, TP 2 %
    crossover(sma5, sma21) -> entry long;  crossunder -> close long
    every bar: exit(stop = close x 0.99, limit = close x 1.02)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket follows every bar's close (a moving level): mark trailing_stop_pending; fixed at 1 % / 2 % of the
      fill here (scalars). The counter / price variables only feed labels.
    * Long only. Stop module: portfolio_kwargs {} (D4). The title's "Intraday" is a label; FREQ = "3D" from the
      backtest header: three-day bars from broker days in fixed blocks counted from 1970-01-01 (block phase: decision
      owed), as #426509: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (mark).
    2 generic: PASS, SMAs and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489158_sma_5_21_cross_bracket_long_3d"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3D"  # backtest header period: 3d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [1.0, 3.0],
    "tp_pct": [2.0, 6.0],
}
DEFAULT_PARAMS = {"short_len": 5, "long_len": 21, "sl_pct": 1.0, "tp_pct": 2.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=3):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=3)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s, l_ = c.rolling(int(p["short_len"])).mean(), c.rolling(int(p["long_len"])).mean()
    up = ((s > l_) & (s.shift(1) <= l_.shift(1))).astype(bool)
    dn = ((s < l_) & (s.shift(1) >= l_.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, dn, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
