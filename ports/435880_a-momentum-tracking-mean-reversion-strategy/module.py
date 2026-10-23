"""Hourly bars, long only, through the script's own trade-state machine: an RSI 2 under 12 together with a raw stochastic 12 under 10 opens a long (not on the bar after a close); a 1 % rise of the highest high since the signal over the signal close, a low 2 % under the signal close, or the first EMA 10 / 20 cross down closes it at the next open.
Port of FMZ strategy #435880 "A Momentum Tracking Mean Reversion Strategy" (APEX - Tester - Buy/Sell Strategies - Basic - BACKTESTER).

FMZ source id: 435880

Source
    https://www.fmz.com/strategy/435880 (PineScript v3, FMZ last modified 2023-12-19 14:42:26).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 299-1347), buy: RSI 2 < 12 (on), STOCH fast K 12 < 10 (slow K / D 1, on), BB T3 10 x 2.1 "cross below" (on, but gated by the STOCHRSI switch); sell: EMA 10 crosses under EMA 20 (on); TP 1 %, trailing profit 0, SL 2 %, trailing stop off; LongsOnly; start 2018-09-20
    allBuy = rsiBuy and bbBuy and stochBuy and (the switched-off sets = true);  sell = sell_ma_use ? crossunder(ema(close, 10), ema(close, 20)) : false
    tradeState: INACTIVE -> ACTIVELONG when buy and not longClose[1];  longCondition = change(tradeState) and ACTIVELONG -> entry Long
    long_tp = last_high >= open_close x 1.01 (ttp 0);  long_sl = low <= open_close x 0.98;  long_sos = first sell bar;  longClose = (tp or sl or sos) and not longCondition -> close Long, tradeState := INACTIVE

Interpretation choices (Pine rules in SURVEY_README.md)
    * bbBuy is gated by "stochrsi_use" instead of "bb_use" (a copy slip), so with STOCHRSI off the BB
      test is always true (weird case); the buy is the RSI 2 and stochastic 12 test alone. The stochastic
      slow K / D are EMAs of length 1, i.e. the raw stochastic. The target and stop are the script's
      bar-close tests on its own anchor (the signal bar's close and the highest high since the signal bar,
      that bar included), so they exit at the next bar's open, not at the levels: ported in the signals.
      "Trailing profit" 0 makes the target test true as soon as the high has reached +1 %. A new trade
      cannot start on the bar after a close (longClose[1]). The S/R fractal lines (with volume) only feed
      plots and alerts: volume is not used. orderType is LongsOnly. The 2018-09-20 start is dropped. No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based target and stop in the signals.
    2 generic: PASS, short-RSI and stochastic oversold entries with an EMA-cross exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the author's 2018-09-20 start dropped).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435880_apex_rsi2_stoch12_oversold_ema_cross_exit_long"
FAMILY = "oscillator_agreement"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_oversold": [12.0, 20.0],
    "stoch_oversold": [10.0, 20.0],
}
DEFAULT_PARAMS = {"rsi_len": 2, "rsi_oversold": 12.0, "stoch_len": 12, "stoch_oversold": 10.0,
                  "sell_short": 10, "sell_long": 20, "tp": 0.01, "sl": 0.02}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    n = int(p["stoch_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    stoch = 100 * (c - ll) / (hh - ll).where(hh != ll)
    buy = ((rsi < float(p["rsi_oversold"])) & (stoch < float(p["stoch_oversold"]))).to_numpy()
    es = c.ewm(span=int(p["sell_short"]), adjust=False).mean()
    el = c.ewm(span=int(p["sell_long"]), adjust=False).mean()
    sell = ((es < el) & (es.shift(1) >= el.shift(1))).to_numpy()
    sell_prev = np.concatenate(([False], sell[:-1]))
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tp, sl = float(p["tp"]), float(p["sl"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    state, close_prev, entry_c, last_high = 0, False, np.nan, np.nan
    for i in range(m):
        long_cond = False
        if state == 0 and buy[i] and not close_prev:
            state, long_cond, entry_c = 1, True, cv[i]
            le[i] = i + 1 < m
        lclose = False
        if state == 1:
            last_high = hv[i] if np.isnan(last_high) or hv[i] > last_high else last_high
            l_tp = last_high >= entry_c * (1 + tp)
            l_sl = lv[i] <= entry_c * (1 - sl)
            l_sos = sell[i] and not sell_prev[i]
            lclose = (l_tp or l_sl or l_sos) and not long_cond
        if lclose:
            lx[i] = True
            state, last_high = 0, np.nan
        close_prev = lclose
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
