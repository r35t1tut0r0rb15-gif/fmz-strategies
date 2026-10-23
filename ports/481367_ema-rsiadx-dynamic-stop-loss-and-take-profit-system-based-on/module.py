"""3-hour bars: the EMA 9 crossing over the EMA 21 with RSI 14 over 50, volume over its 20-bar average and ADX 14 over 25 goes long; an EMA crossing under, an RSI under 50, or low volume with ADX over 25 goes short; a 3 % stop and 5 % target from position_avg_price are armed only when a signal arrives while a trade is open, followed in the signals; reversing.
Port of FMZ strategy #481367 "基于EMA交叉结合RSIADX和成交量确认的动态止盈止损系统-Dynamic-Stop-Loss-and-Take-Profit-System-Based-on-EMA-Crossover-with-RSI-ADX-and-Volume-Confirmation" (Estrategia Avancada - EMA, RSI, ADX e Volume).

FMZ source id: 481367

Source
    https://www.fmz.com/strategy/481367 (PineScript v5, FMZ last modified 2025-02-10 15:10:20).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 110-159), EMA 9 / 21; RSI 14; DMI 14 / 14, ADX > 25; volume SMA 20; SL 3 %, TP 5 % of position_avg_price
    buy_signal = crossover(ema9, ema21) and rsi > 50 and volume > volume_ma and adx > 25 -> close Venda, entry Compra, exit("TakeProfit", "Compra", limit = avg x 1.05, stop = avg x 0.97)
    sell_signal = crossunder(ema9, ema21) or rsi < 50 or (volume < volume_ma and adx > 25) -> close Compra, entry Venda, exit("TakeProfit", "Venda", limit = avg x 0.95, stop = avg x 1.03)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "and" binds before "or", so the sell signal is true on any bar with RSI under 50 (or a crossing
      under, or low volume in a strong trend): the strategy is short most of the time (weird case). The
      bracket takes position_avg_price at the signal bar: na when the signal opens a trade from flat (no
      exit exists), the old trade's fill on a reversal bar, the trade's own fill on a repeated signal
      while it is open. The house engine cannot arm a bracket from those prices, so the signals follow
      it: a bar whose low / high reaches an armed level closes the trade at the next open (mark
      trailing_stop_pending). A buy and a sell never meet on one bar. REVERSAL INTENDED. No sizing code.
      FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; position-price bracket followed in the signals.
    2 generic: PASS, EMA crossings with RSI / volume / ADX filters, loose short state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 20 on both sides; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_481367_ema9_21_rsi_adx_volume_loose_short_avg_bracket_3h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sl": [0.03, 0.02],
    "tp": [0.05, 0.08],
}
DEFAULT_PARAMS = {"sl": 0.03, "tp": 0.05, "adx_min": 25.0}


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


def _fixnan(x):
    """Pine fixnan: a NaN takes the last non-NaN value (Pine's own indicator semantics)."""
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _dmi(h, lo, c, n, sm):
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trur = _rma(tr, n)
    plus, minus = _fixnan(100 * _rma(pdm, n) / trur), _fixnan(100 * _rma(mdm, n) / trur)
    tot = plus + minus
    adx = 100 * _rma((plus - minus).abs() / tot.where(tot != 0, 1.0), sm)
    return plus, minus, adx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    f, s = c.ewm(span=9, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    r = _rsi(c, 14)
    _, _, adx = _dmi(h, lo, c, 14, 14)
    vma = v.rolling(20).mean()
    strong = adx > float(p["adx_min"])
    buy = ((f > s) & (f.shift(1) <= s.shift(1)) & (r > 50) & (v > vma) & strong).to_numpy()
    sell = (((f < s) & (f.shift(1) >= s.shift(1))) | (r < 50) | ((v < vma) & strong)).to_numpy()
    on, hn, ln = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sl, tp = float(p["sl"]), float(p["tp"])
    m = len(on)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    vpos, pine, fp, pend, armed = 0, 0, np.nan, False, None
    for i in range(m):
        held = pine
        if pend:
            fp, pend = on[i], False
        if held != 0 and armed is not None:
            st, lm = armed
            if (held == 1 and (ln[i] <= st or hn[i] >= lm)) or (held == -1 and (hn[i] >= st or ln[i] <= lm)):
                held, armed, fp = 0, None, np.nan
        new, sent = held, None
        if buy[i]:
            new = 1
            sent = (fp * (1 - sl), fp * (1 + tp)) if held != 0 else None
        if sell[i]:
            new = -1
            sent = (fp * (1 + sl), fp * (1 - tp)) if held != 0 else None
        if new != held:
            armed, pend = sent, new != 0
        elif sent is not None:
            armed = sent
        pine = new
        if new != vpos and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif vpos == 1:
                lx[i] = True
            else:
                sx[i] = True
            vpos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
