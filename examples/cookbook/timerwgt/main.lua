-- Timer widget: shows a model timer, colored while running, with
-- tap-to-reset (when stopped) and a long-press menu entry.
-- https://frskyrc.github.io/ethos-lua-doc/cookbook/timer-control/

local RUN_COLOR = lcd.RGB(40, 190, 80)

local function create()
  return { index = 0, timer = nil, text = "--:--", name = "", running = false, lastValue = nil }
end

local function attach(widget)
  widget.timer = model.getTimer(widget.index)   -- nil if the model has no such timer
  widget.name = widget.timer and widget.timer:name() or ("Timer " .. (widget.index + 1))
  widget.lastValue = nil
end

local function wakeup(widget)
  if not widget.timer then
    attach(widget)
    if not widget.timer then return end
  end
  local t = widget.timer
  local value, running = t:value(), t:running()
  if value ~= widget.lastValue or running ~= widget.running then  -- ticks once a second
    widget.lastValue, widget.running = value, running
    widget.text = t:stringValue()
    lcd.invalidate()
  end
end

local function paint(widget)
  local w, h = lcd.getWindowSize()
  local fg = lcd.themeColor(THEME_DEFAULT_COLOR)
  lcd.font(FONT_S)
  lcd.color(fg)
  lcd.drawText(4, 2, widget.name)
  lcd.font(h > 90 and FONT_XXL or FONT_XL)
  lcd.color(widget.running and RUN_COLOR or fg)
  lcd.drawText(w / 2, h / 2 - 8, widget.text, CENTERED)
end

local function resetTimer(widget)
  if widget.timer then widget.timer:reset(); widget.lastValue = nil end
end

local function event(widget, category, value, x, y)
  if category == EVT_TOUCH and value == TOUCH_END and widget.timer and not widget.running then
    resetTimer(widget)
    return true
  end
  return false
end

local function menu(widget)
  return { { "Reset timer", function() resetTimer(widget) end } }
end

local function configure(widget)
  local line = form.addLine("Timer")
  form.addNumberField(line, nil, 1, 3, function() return widget.index + 1 end,
    function(v) widget.index = v - 1; widget.timer = nil end)
end

local function read(widget) widget.index = storage.read("index") or 0 end
local function write(widget) storage.write("index", widget.index) end

local function init()
  system.registerWidget({ key = "timerwg", name = "Timer",
    create = create, wakeup = wakeup, paint = paint, event = event, menu = menu,
    configure = configure, read = read, write = write })
end

return { init = init }
