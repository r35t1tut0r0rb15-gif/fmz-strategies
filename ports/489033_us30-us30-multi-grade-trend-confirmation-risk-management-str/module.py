"""Hourly bars: the EMA 20 crossing over the SMA 20 above the EMA 200 with RSI 9 over 50 goes long when the bar's body is above its 20-bar average on rising volume; the mirror goes short when that holds or RSI 9 is under 45 (the A-grade test's precedence); each trade gets a 0.5 % target and 0.3 % stop from the signal close; reversing.
Port of FMZ strategy #489033 "US30多级趋势确认与风险管理策略-US30-Multi-Grade-Trend-Confirmation-Risk-Management-Strategy" (US30 Multi-Grade Trend Confirmation Risk Management Strategy).

FMZ source id: 489033

Source
    https://www.fmz.com/strategy/489033 (PineScript v5, FMZ last modified 2025-04-01 13:41:30).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 283-371), RSI 9; SMA / EMA 20; EMA 200; body vs its SMA 20 (x 1 / x 2); volume > volume[1]; grades A, B on, C off; TP 0.5 %, SL 0.3 %; 10 % of equity
    gradeA = candleVeryLarge and volumeRising and rsi > 55 or rsi < 45;  gradeB = candleLarge and volumeRising;  gradeC = candleLarge (off)
    longBase = close > ema200 and crossover(ema, sma) and rsi > 50 and close > ema and close > sma -> entry "Long " + grade, exit("TP/SL", limit = close x 1.005, stop = close x 0.997)
    shortBase mirrored -> entry "Short " + grade, exit("TP/SL", limit = close x 0.995, stop = close x 1.003)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "a and b and c or d" is "(a and b and c) or d" in Pine, so grade A also holds whenever RSI 9 is
      under 45: never on a long base (RSI over 50), so a long needs grade B (a large body on rising
      volume, which grade A's very large body implies); a short takes grade B or RSI under 45, as
      written (weird case). The bracket is sent on signal bars from that close: ported as fractions of the
      fill, exact (1e-6 floor); repeats while in the trade (a new entry id the engine ignores) re-send
      it (not followed: trailing_stop_pending). Both sides share the exit id "TP/SL", but their signal
      bars never coincide. The loop follows the bracket on the bars only to know when the trade is flat.
      The title names US30 on 1-minute bars; the header is BTC_USDT 1h. REVERSAL INTENDED. 10 % of
      equity is sizing. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket at the signal close as fractions of the fill.
    2 generic: PASS, EMA / SMA crossings in the EMA 200 trend graded by body size and volume.
    3 crypto-exchange-only: no (exchange pair in the header only (US30 named in the title)).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against the previous bar's (volume > volume[1]); exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489033_ema_sma_cross_graded_body_volume_pct_bracket_1h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [0.5, 1.0],
    "sl_pct": [0.3, 0.6],
}
DEFAULT_PARAMS = {"tp_pct": 0.5, "sl_pct": 0.3}


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


def _run(bars_df, p):
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    r = _rsi(c, 9)
    sma, ema, e200 = c.rolling(20).mean(), c.ewm(span=20, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    vr = v > v.shift(1)
    body = (c - o).abs()
    avg = body.rolling(20).mean()
    grade_a = ((body > avg * 2) & vr & (r > 55)) | (r < 45)
    grade_b = (body > avg) & vr
    ok = grade_a | grade_b
    up_x = (ema > sma) & (ema.shift(1) <= sma.shift(1))
    dn_x = (ema < sma) & (ema.shift(1) >= sma.shift(1))
    buy = ((c > e200) & up_x & (r > 50) & (c > ema) & (c > sma) & ok).to_numpy()
    sell = ((c < e200) & dn_x & (r < 50) & (c < ema) & (c < sma) & ok).to_numpy()
    cn, hn, ln = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    tp, sl = float(p["tp_pct"]) / 100, float(p["sl_pct"]) / 100
    m = len(cn)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, st, tg = 0, np.nan, np.nan
    for i in range(m):
        if pos == 1 and (ln[i] <= st or hn[i] >= tg):
            pos = 0                         # the bracket closed the trade (the engine does it at the level)
        elif pos == -1 and (hn[i] >= st or ln[i] <= tg):
            pos = 0
        if buy[i] and pos != 1 and i + 1 < m:
            le[i], pos, st, tg = True, 1, cn[i] * (1 - sl), cn[i] * (1 + tp)
        elif sell[i] and pos != -1 and i + 1 < m:
            se[i], pos, st, tg = True, -1, cn[i] * (1 + sl), cn[i] * (1 - tp)
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    tp, sl = float(p["tp_pct"]) / 100, float(p["sl_pct"]) / 100
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c * (1 - sl)).shift(1) / o)
            .mask(sf, (c * (1 + sl)).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (c * (1 + tp)).shift(1) / o - 1)
            .mask(sf, 1 - (c * (1 - tp)).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
