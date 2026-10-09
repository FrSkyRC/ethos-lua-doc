# Drawing on screen

All drawing happens inside a `paint` callback (widgets, system tools, dialogs). Coordinates are in pixels relative to the window you're drawing in, with `0, 0` at the top-left.

## The paint / invalidate model

Ethos doesn't redraw your window every frame. It calls `paint` when:

- you call [`lcd.invalidate()`](../api/lcd/invalidate.md) (whole window) or `lcd.invalidate(x, y, w, h)` (a region), or
- Ethos needs a redraw itself (screen shown, resized, overlay closed).

So the pattern is: **detect change in `wakeup`, invalidate, draw in `paint`.**

```lua
local function wakeup(widget)
  local v = widget.source:value()
  if v ~= widget.value then
    widget.value = v
    lcd.invalidate()          -- schedule a paint
  end
end

local function paint(widget)
  -- draw everything from widget state; no expensive lookups here
end
```

Calling `lcd.invalidate()` unconditionally in `wakeup` works, but it repaints at full rate forever and wastes CPU on every visible screen. See [Saving CPU](../best-practice/cpu.md).

## Window size

```lua
local w, h = lcd.getWindowSize()
```

Always lay out relative to the window. The same widget may be placed in a full-screen slot on an X20 (800×480) and a small slot on an X18 (480×320). Read the size in `paint` (it's cheap), and cache derived layout only if computing it is expensive.

## Colors

```lua
lcd.color(lcd.RGB(255, 128, 0))          -- orange
lcd.color(lcd.RGB(255, 0, 0, 0.5))      -- 50 % transparent red
lcd.color(lcd.GREY(64))                  -- dark grey
lcd.color(lcd.themeColor(THEME_DEFAULT_COLOR))  -- follow the user's theme
```

| Call | Use |
| --- | --- |
| [`lcd.RGB(r, g, b [, alpha])`](../api/lcd/RGB.md) | Make a color value. Compute once and keep it, don't rebuild in every paint |
| [`lcd.GREY(value [, alpha])`](../api/lcd/GREY.md) | Shades of grey |
| [`lcd.color(c)`](../api/lcd/color.md) | Set the current drawing color |
| [`lcd.themeColor(THEME_*)`](../api/lcd/themeColor.md) | Read a color from the active theme. Text and backgrounds then work in light **and** dark themes |
| [`lcd.getContrastingColor(bg)`](../api/lcd/getContrastingColor.md) | Black or white, whichever reads better on `bg` |

!!! tip "Prefer theme colors for text and frames"
    Hard-coded `WHITE` text disappears on a light theme. `lcd.themeColor(THEME_DEFAULT_COLOR)` for text and `THEME_DEFAULT_BGCOLOR` for fills keep your widget readable whatever theme the pilot uses. The full list is under [Theme colors](../api/constants.md#theme-colors).

## Text

```lua
lcd.font(FONT_L)
local tw, th = lcd.getTextSize("12.6V")      -- measure with the current font
lcd.drawText(w - 4, 0, "12.6V", RIGHT)        -- right-aligned at x = w - 4
lcd.drawText(w / 2, h / 2 - th / 2, "Hi", CENTERED)
lcd.drawNumber(10, 10, 12.63, UNIT_VOLT, 1)   -- "12.6V", unit and decimals handled for you
```

Fonts from small to large: `FONT_XXS`, `FONT_XS`, `FONT_S`, `FONT_M`, `FONT_L`, `FONT_XL`, `FONT_XXL`, plus bold/italic variants. See [Fonts](../api/constants.md#fonts).

**Fitting text** to a box: try fonts from large to small and use the first that fits.

```lua
local FONTS = { FONT_XXL, FONT_XL, FONT_L, FONT_M, FONT_S }  -- built once, at file level

local function fitFont(text, maxW, maxH)
  for i = 1, #FONTS do
    lcd.font(FONTS[i])
    local tw, th = lcd.getTextSize(text)
    if tw <= maxW and th <= maxH then return tw, th end
  end
  return lcd.getTextSize(text)  -- smallest font, may overflow
end
```

Measuring text costs time. If the text only changes occasionally, measure once when it changes and keep the result.

## Shapes

```lua
lcd.drawLine(x1, y1, x2, y2)
lcd.drawRectangle(x, y, w, h [, thickness])
lcd.drawFilledRectangle(x, y, w, h)
lcd.drawCircle(cx, cy, r)
lcd.drawFilledCircle(cx, cy, r)
lcd.drawTriangle(x1, y1, x2, y2, x3, y3)
lcd.drawFilledTriangle(x1, y1, x2, y2, x3, y3)
lcd.drawAnnulusSector(cx, cy, innerR, outerR, startAngle, endAngle)  -- arcs and dial gauges
lcd.pen(PEN_DOTTED)  -- line style for subsequent lines
```

A dial gauge from annulus sectors. Angles are in degrees, 0–360, with 0 at the top running clockwise, so a classic 270° gauge starts at 225 (bottom-left). Open-source dashboards split any arc wider than 180° into two calls, and so does this helper:

```lua
local function drawArc(cx, cy, inner, outer, startAngle, endAngle)
  local sweep = endAngle - startAngle
  if sweep < 0 then sweep = sweep + 360 end
  if sweep <= 180 then
    lcd.drawAnnulusSector(cx, cy, inner, outer, startAngle, endAngle)
  else                                   -- split wide arcs in two
    local mid = (startAngle + sweep / 2) % 360
    lcd.drawAnnulusSector(cx, cy, inner, outer, startAngle, mid)
    lcd.drawAnnulusSector(cx, cy, inner, outer, mid, endAngle)
  end
end

local START = 225  -- bottom-left; 270° of travel ends bottom-right (135)

local function drawDial(cx, cy, r, percent, color)
  lcd.color(lcd.GREY(60))
  drawArc(cx, cy, r * 0.75, r, START, (START + 270) % 360)                  -- track
  if percent > 0 then
    lcd.color(color)
    drawArc(cx, cy, r * 0.75, r, START, (START + 270 * percent / 100) % 360) -- value
  end
end
```

## Bitmaps and masks

| | Bitmap | Mask |
| --- | --- | --- |
| Load | [`lcd.loadBitmap(path)`](../api/lcd/loadBitmap.md) | [`lcd.loadMask(path)`](../api/lcd/loadMask.md) |
| Draw | [`lcd.drawBitmap(x, y, bmp [, w, h])`](../api/lcd/drawBitmap.md) | [`lcd.drawMask(x, y, mask)`](../api/lcd/drawMask.md) |
| Colors | Full color image (PNG/JPG/BMP) | Single-channel: drawn in the **current `lcd.color()`** |
| Source image | Any | **Dark pixels are drawn, white is transparent.** Draw icons black on white |
| Best for | Photos, logos, panels | Icons that should follow the theme color |

!!! tip "Mask polarity, verified in the simulator"
    A white-on-black icon loaded with `lcd.loadMask` shows up as a solid block with holes. Make mask images **black shapes on a white background**; the black parts get painted in the current color. The same applies to a system tool's `icon`.

The simulator console logs each image as it is decoded, e.g. `Bitmap SCRIPTS:/mytool/icon.png loaded, RAM used: 4096 bytes`. That's the quickest way to see what each asset costs.

```lua
-- load ONCE (file level or create), never inside paint
local icon = lcd.loadMask("gfx/battery.png")

local function paint(widget)
  lcd.color(widget.alarm and lcd.RGB(220, 40, 40) or lcd.themeColor(THEME_DEFAULT_COLOR))
  lcd.drawMask(4, 4, icon)
end
```

!!! warning "Bitmaps are the fastest way to run out of memory"
    Decoded images live in the Lua bitmap memory, which shares one region with the Lua heap. Load each image once, reuse the handle, prefer masks for icons, size images to how they're displayed, and set handles to `nil` when a tool closes. See [Saving RAM](../best-practice/memory.md#bitmaps).

## Clipping

[`lcd.setClipping(x, y, w, h)`](../api/lcd/setClipping.md) restricts drawing to a rectangle. Use it for scrolling lists, bar fills and graphs that must not spill over. Reset it when you're done, either with `lcd.setClipping()` or by setting the whole window again:

```lua
lcd.setClipping(barX, barY, fillW, barH)   -- only the filled part of the bar
lcd.drawMask(barX, barY, stripes)          -- pattern is cut to the fill width
lcd.setClipping(0, 0, lcd.getWindowSize()) -- back to the whole window
```
