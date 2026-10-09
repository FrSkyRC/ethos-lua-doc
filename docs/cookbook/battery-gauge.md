# Battery gauge widget

A percentage bar computed from pack voltage and cell count, using a LiPo discharge curve, with green, amber and red thresholds.

## What it demonstrates

- **Lookup tables at file level.** The voltage→percent curve and colors are built once.
- **Linear interpolation** between curve points.
- **Integer-percent change detection.** The bar only redraws when the rounded percentage changes.
- **Theme-aware frame and text** through `lcd.themeColor(THEME_DEFAULT_COLOR)`.

## The script

```lua title="scripts/battgauge/main.lua" linenums="1"
--8<-- "examples/cookbook/battgauge/main.lua"
```

!!! note "Resting voltage"
    The curve is for a pack at rest. Under load the voltage sags and the gauge reads low. For flight use, prefer a consumption-based estimate (mAh used vs pack capacity) if you have a current sensor, or smooth the voltage over a few seconds.

## Try it without a flight battery

Choose **System value → Main voltage** (the radio's own battery) as the source and set **Cells** to 2. In the X20S simulator this reads 7.5 V, 25 %.

## API used

[`lcd.drawFilledRectangle`](../api/lcd/drawFilledRectangle.md) · [`lcd.drawRectangle`](../api/lcd/drawRectangle.md) · [`lcd.RGB`](../api/lcd/RGB.md) · [`lcd.GREY`](../api/lcd/GREY.md) · [`lcd.invalidate`](../api/lcd/invalidate.md) · [`form.addSourceField`](../api/form/addSourceField.md)
