```lua
-- draw a striped fill that must not spill past the filled width
lcd.setClipping(barX, barY, fillW, barH)
lcd.drawBitmap(barX, barY, STRIPES)
lcd.setClipping()                          -- reset
-- or: lcd.setClipping(0, 0, lcd.getWindowSize())
```
