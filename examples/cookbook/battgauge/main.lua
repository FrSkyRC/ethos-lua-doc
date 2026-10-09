-- Battery gauge: percentage bar from pack voltage and cell count.
-- https://frskyrc.github.io/ethos-lua-doc/cookbook/battery-gauge/

-- LiPo resting voltage per cell -> percent (built once, at file level)
local CURVE = {
  { 3.30, 0 }, { 3.60, 5 }, { 3.70, 15 }, { 3.75, 25 }, { 3.79, 35 },
  { 3.83, 45 }, { 3.87, 55 }, { 3.92, 65 }, { 3.97, 75 }, { 4.05, 85 },
  { 4.12, 95 }, { 4.20, 100 },
}

local GREEN, AMBER, RED = lcd.RGB(40, 190, 80), lcd.RGB(240, 170, 0), lcd.RGB(225, 50, 50)
local TRACK = lcd.GREY(70)

local function percentFromCell(v)
  if v <= CURVE[1][1] then return 0 end
  for i = 2, #CURVE do
    local hi = CURVE[i]
    if v <= hi[1] then
      local lo = CURVE[i - 1]
      return lo[2] + (v - lo[1]) * (hi[2] - lo[2]) / (hi[1] - lo[1])
    end
  end
  return 100
end

local function create()
  return { source = nil, cells = 0, percent = nil, volts = nil, label = "--" }
end

local function wakeup(widget)
  local src = widget.source
  local v = src and src:value()
  if not v or widget.cells < 1 then
    if widget.percent then widget.percent, widget.label = nil, "--"; lcd.invalidate() end
    return
  end
  local pct = math.floor(percentFromCell(v / widget.cells) + 0.5)
  if pct ~= widget.percent then
    widget.percent = pct
    widget.label = pct .. "%  " .. string.format("%.1fV", v)
    lcd.invalidate()
  end
end

local function paint(widget)
  local w, h = lcd.getWindowSize()
  local pad = 6
  local barH = math.max(12, math.floor(h * 0.45))
  local barY = h - barH - pad

  -- track and fill
  lcd.color(TRACK)
  lcd.drawFilledRectangle(pad, barY, w - pad * 2, barH)
  local pct = widget.percent
  if pct then
    lcd.color(pct > 30 and GREEN or pct > 15 and AMBER or RED)
    lcd.drawFilledRectangle(pad, barY, math.floor((w - pad * 2) * pct / 100), barH)
  end

  -- frame and label, in theme colors so it works on light and dark themes
  lcd.color(lcd.themeColor(THEME_DEFAULT_COLOR))
  lcd.drawRectangle(pad, barY, w - pad * 2, barH)
  lcd.font(h > 90 and FONT_L or FONT_S)
  lcd.drawText(pad, pad, widget.cells > 0 and widget.label or "Set cells in config")
end

local function configure(widget)
  local line = form.addLine("Voltage source")
  form.addSourceField(line, nil, function() return widget.source end,
    function(v) widget.source = v; widget.percent = nil end)
  line = form.addLine("Cells")
  form.addNumberField(line, nil, 0, 14, function() return widget.cells end,
    function(v) widget.cells = v; widget.percent = nil end)
end

local function read(widget)
  widget.source = storage.read("source")
  widget.cells = storage.read("cells") or 0
end

local function write(widget)
  storage.write("source", widget.source)
  storage.write("cells", widget.cells)
end

local function init()
  system.registerWidget({ key = "battgg", name = "Battery gauge",
    create = create, wakeup = wakeup, paint = paint,
    configure = configure, read = read, write = write })
end

return { init = init }
