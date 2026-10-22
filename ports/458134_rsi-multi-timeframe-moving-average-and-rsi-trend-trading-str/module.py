"""SMA 9 / 21 and RSI 14 agreement on the 1-hour series and the chart's own bars, bar size from the search: the short SMA over the long with the RSI under 70 on both goes long, the mirror with the RSI over 30 goes short, each with a 1.5 ATR stop and 3 ATR target; reversing.
Port of FMZ strategy #458134 "多周期确认的移动平均线与RSI趋势交易策略-Multi-Timeframe-Moving-Average-and-RSI-Trend-Trading-Strategy" (SOL Futures Trading with MTF Confirmation).

FMZ source id: 458134

Source
    https://www.fmz.com/strategy/458134 (PineScript v5, FMZ last modified 2024-07-30 10:59:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 164-240), SMA 9 / 21, RSI 14 on request.security("60") (no lookahead) and on the chart; ATR 14; stop 1.5 ATR, target 3 ATR from the signal close; qty = 1 % of 50000 / ATR
    1h: sma9 > sma21 and rsi < 70, chart: the same -> entry Long + exit(stop = close - 1.5 atr, limit = close + 3 atr)
    1h: sma9 < sma21 and rsi > 30, chart: the same -> entry Short + exit(stop = close + 1.5 atr, limit = close - 3 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending" (rule 1);
      precompute builds the bars with the house bar_sizes.build_bars with the driver's bar_size. The
      version-5 request.security("60") without lookahead is read as the last 1-hour bar completed by the
      chart bar's close (#440503; on a chart bar of an hour or more it is the bar's last hour, #436765),
      built in precompute from the minutes. The entry tests are states, so the signal and its exit are
      re-sent on every bar while they hold: the opening levels are kept, as ATR multiples of the signal
      bar shifted into the fill (as #434428, mark trailing_stop_pending). The ATR position size is not
      ported (sizing is the optimisation layer's). REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4).

Admission criteria
    1 fits the interface: PASS, bar-close orders; 1-hour values from completed hours; ATR bracket at entry.
    2 generic: PASS, SMA and RSI agreement on two timeframes with an ATR bracket.
    3 crypto-exchange-only: no (no exchange header (SOL named in the title only)).
    4 signals only: ATR-risk position size stored, not ported.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_458134_sma9_21_rsi_1h_and_chart_agreement_atr_bracket_reversal"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # no backtest header: the driver supplies bar_size
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_len": [9, 5],
    "long_len": [21, 50],
    "sl_atr": [1.5, 3.0],
}
DEFAULT_PARAMS = {"short_len": 9, "long_len": 21, "sl_atr": 1.5, "tp_atr": 3.0, "rsi_len": 14, "atr_len": 14}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    p = {**DEFAULT_PARAMS, **params}
    bars = bar_sizes.build_bars(raw_1m_df, params["bar_size"])
    raw = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    hc = raw["close"].resample("1h", label="left", closed="left").last().dropna()
    h_s = hc.rolling(int(p["short_len"])).mean().to_numpy()
    h_l = hc.rolling(int(p["long_len"])).mean().to_numpy()
    h_r = _rsi(hc, int(p["rsi_len"])).to_numpy()
    mins = raw.index.to_numpy().astype("datetime64[ns]")
    opens = bars.index.to_numpy().astype("datetime64[ns]")
    which = np.searchsorted(opens, mins, side="right") - 1
    last_min = pd.Series(mins).groupby(which).max()
    chart_end = np.full(len(opens), np.datetime64("NaT"), dtype="datetime64[ns]")
    ok = last_min.index.to_numpy() >= 0
    chart_end[last_min.index.to_numpy()[ok]] = last_min.to_numpy()[ok] + np.timedelta64(1, "m")
    hour_end = hc.index.to_numpy().astype("datetime64[ns]") + np.timedelta64(1, "h")
    k = np.searchsorted(hour_end, chart_end, side="right") - 1   # last hour completed by the chart close
    k = np.where(np.isnat(chart_end), -1, k)
    out = bars.copy()
    for name, v in (("h_short", h_s), ("h_long", h_l), ("h_rsi", h_r)):
        out[name] = np.where(k >= 0, v[np.clip(k, 0, None)], np.nan)
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s, l = c.rolling(int(p["short_len"])).mean(), c.rolling(int(p["long_len"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    hs, hl, hr = bars_df["h_short"], bars_df["h_long"], bars_df["h_rsi"]
    le = (hs > hl) & (hr < 70) & (s > l) & (r < 70)
    se = (hs < hl) & (hr > 30) & (s < l) & (r > 30)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": (float(p["sl_atr"]) * a).shift(1), "tp_stop": (float(p["tp_atr"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}
