"""MACD 13 / 21 with an SMA 8 signal line, daily bars: the signal line crossing over the MACD above the SMA 50 goes long (and again on the next bar), with a 1 % stop and 2 % target from the fill; crossing under it below the SMA 50 goes short, and the short's levels sit on the wrong side of the market, so each short closes at the open after its first bar; reversing.
Port of FMZ strategy #451413 "趋势跟踪与动量交易相结合的双重MACD优化策略-Dual-MACD-Optimization-Strategy-Combining-Trend-Following-and-Momentum-Trading" (Improved MACD_VXI Strategy).

FMZ source id: 451413

Source
    https://www.fmz.com/strategy/451413 (PineScript v5, FMZ last modified 2024-05-14 17:35:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-154), MACD EMA 13 / 21, signal SMA 8; SMA 50 trend; stop avg x 0.99, limit avg x 1.02 for both ids
    crossover(signal, macd) and close > sma50 -> entry Buy;  crossunder(signal, macd) and close < sma50 -> entry Sell
    the same conditions one bar back -> entry Buy / entry Sell again
    exit(Buy, stop = avg x 0.99, limit = avg x 1.02);  exit(Sell, stop = avg x 0.99, limit = avg x 1.02)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent every bar from the average (fill) price, na while flat: ported active from
      the fill bar (#440797) as fixed fractions 0.01 / 0.02 of the fill. The short exit reuses the
      long's levels: a buy stop under and a buy limit over the price, both on the wrong side, so the
      short closes at the first open after its fill bar (as #439872, #442657: the port closes it on
      that bar's signal). The repeat of the previous bar's signal is a second entry on the same id:
      ignored while that side is held, a new entry after a long's stop or target on its fill bar.
      When a bar carries both a new signal and the previous bar's opposite one, the later call wins
      (as #437773). strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). Stops on 1-day bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; long bracket fixed from the fill; the short's wrong-side levels read as a close.
    2 generic: PASS, MACD signal crossings with an SMA trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_451413_macd_signal_cross_sma50_long_bracket_short_one_bar"
FAMILY = "macd"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [13, 12],
    "slow": [21, 26],
    "sma_len": [50, 100],
}
DEFAULT_PARAMS = {"fast": 13, "slow": 21, "signal_len": 8, "sma_len": 50,
                  "sl_pct": 0.01, "tp_pct": 0.02}


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
    c = bars_df["close"]
    macd = (c.ewm(span=int(p["fast"]), adjust=False).mean()
            - c.ewm(span=int(p["slow"]), adjust=False).mean())
    sig = macd.rolling(int(p["signal_len"])).mean()
    sma = c.rolling(int(p["sma_len"])).mean()
    buy = (sig > macd) & (sig.shift(1) <= macd.shift(1)) & (c > sma)
    sell = (sig < macd) & (sig.shift(1) >= macd.shift(1)) & (c < sma)
    calls = [buy.to_numpy(), sell.to_numpy(),
             buy.shift(1, fill_value=False).to_numpy(), sell.shift(1, fill_value=False).to_numpy()]
    sides = [1, -1, 1, -1]
    sl, tp = float(p["sl_pct"]), float(p["tp_pct"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se, sx = (np.zeros(m, dtype=bool) for _ in range(3))
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i and (lv[i] <= ov[entry_i] * (1 - sl) or hv[i] >= ov[entry_i] * (1 + tp)):
            pos = 0
        if i + 1 >= m:
            continue
        want = 0
        for arr, d in zip(calls, sides):
            if arr[i]:
                want = d                     # the later call wins a tie
        if want == 1 and pos != 1:
            le[i], pos, entry_i = True, 1, i + 1
        elif want == -1 and pos != -1:
            se[i], pos, entry_i = True, -1, i + 1
        elif pos == -1 and i == entry_i:
            sx[i], pos = True, 0          # the wrong-side short levels fill at the next open
    return le, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, sx = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, _ = _run(bars_df, p)
    ix = bars_df.index
    on = pd.Series(le, index=ix)
    return {"sl_stop": pd.Series(float(p["sl_pct"]), index=ix).where(on).shift(1),
            "tp_stop": pd.Series(float(p["tp_pct"]), index=ix).where(on).shift(1)}


def portfolio_kwargs(**params):
    return {}
