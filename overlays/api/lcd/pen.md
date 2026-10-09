```lua
lcd.pen(PEN_DOTTED)
lcd.drawLine(0, thresholdY, w, thresholdY)   -- dotted threshold line
lcd.pen(PEN_SOLID)                            -- back to solid for the rest
```
