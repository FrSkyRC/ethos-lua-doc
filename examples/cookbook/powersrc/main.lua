-- Power source: a Lua source computing watts from a voltage and a current
-- sensor. It shows up in every source picker (mixes, logic switches, widgets).
-- https://frskyrc.github.io/ethos-lua-doc/cookbook/lua-source/

local cfg = { volts = nil, amps = nil }

local function sourceInit(source)
  source:unit(UNIT_WATT)
  source:decimals(0)
  source:value(0)
end

local function sourceWakeup(source)
  local v = cfg.volts and cfg.volts:value()
  local a = cfg.amps and cfg.amps:value()
  if v and a then
    local w = math.floor(v * a + 0.5)
    if w ~= source:value() then source:value(w) end   -- write only on change
  end
end

local function sourceConfigure(source)
  local line = form.addLine("Voltage")
  form.addSourceField(line, nil, function() return cfg.volts end, function(s) cfg.volts = s end)
  line = form.addLine("Current")
  form.addSourceField(line, nil, function() return cfg.amps end, function(s) cfg.amps = s end)
end

local function sourceRead(source)
  cfg.volts = storage.read("volts")
  cfg.amps = storage.read("amps")
end

local function sourceWrite(source)
  storage.write("volts", cfg.volts)
  storage.write("amps", cfg.amps)
end

local function init()
  system.registerSource({ key = "power", name = "Power (W)",
    init = sourceInit, wakeup = sourceWakeup,
    configure = sourceConfigure, read = sourceRead, write = sourceWrite })
end

return { init = init }
