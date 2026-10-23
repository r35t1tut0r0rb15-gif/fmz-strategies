"""4-hour bars: the close crossing over the session VWAP with a positive MACD histogram (12 / 26 / 9) and RSI 14 under 70 goes long, crossing under with a negative histogram and RSI over 30 goes short; each trade gets a 0.25 % stop and a 0.5 % target from the signal close; reversing.
Port of FMZ strategy #473146 "VWAP-MACD-RSI多因子量化交易策略-VWAP-MACD-RSI-Multi-Factor-Quantitative-Trading-Strategy" (pbs).

FMZ source id: 473146

Source
    https://www.fmz.com/strategy/473146 (PineScript v5, FMZ last modified 2024-11-27 16:11:00).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 118-168), session VWAP; MACD 12 / 26 / 9; RSI 14, 70 / 30; TP 0.5 %, SL 0.25 % from the signal close
    longCondition = crossover(close, vwap) and macdHistogram > 0 and rsi < 70 -> entry Long, exit("Take Profit/Stop Loss", "Long", limit = close x 1.005, stop = close x 0.9975)
    shortCondition = crossunder(close, vwap) and macdHistogram < 0 and rsi > 30 -> entry Short, exit(same id, "Short", limit = close x 0.995, stop = close x 1.0025)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.vwap(close) restarts each session: the house session is the broker day (17:00
      America/New_York), so the VWAP is the volume-weighted close of the day's 4-hour bars so far, each
      bar placed in the broker day of its start. The bracket is sent on signal bars only, as levels from
      that close: ported as fractions of the fill, exact (1e-6 floor). Both sides share one exit id, but
      the calls only happen on their own signal bars (which never coincide), so each trade keeps its own
      bracket until the opposite entry reverses it. 100 % of equity is sizing. REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 4-hour bars: coarse_bar_stop. FREQ = "4h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket at the signal close as fractions of the fill.
    2 generic: PASS, session-VWAP crossings with MACD and RSI filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session-VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone) for the VWAP reset; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_473146_session_vwap_cross_macd_rsi_tight_bracket_4h_reversal"
FAMILY = "vwap"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.005, 0.01],
    "sl": [0.0025, 0.005],
}
DEFAULT_PARAMS = {"tp": 0.005, "sl": 0.0025, "ob": 70.0, "os": 30.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    day = broker_day(bars_df.index)
    vw = (c * v).groupby(day).cumsum() / v.groupby(day).cumsum()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    r = _rsi(c, 14)
    buy = (c > vw) & (c.shift(1) <= vw.shift(1)) & (hist > 0) & (r < float(p["ob"]))
    sell = (c < vw) & (c.shift(1) >= vw.shift(1)) & (hist < 0) & (r > float(p["os"]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o
    sl, tp = float(p["sl"]), float(p["tp"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - k * (1 - sl))
            .mask(sf, k * (1 + sl) - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, k * (1 + tp) - 1)
            .mask(sf, 1 - k * (1 - tp)))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
