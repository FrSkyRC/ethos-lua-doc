-- Low value alert: a background task that calls out a source when it drops
-- below a threshold, with repeat interval and hysteresis.
-- https://frskyrc.github.io/ethos-lua-doc/cookbook/alert-task/

-- task state is file-level: a task has one instance per model
local cfg = { source = nil, threshold = 105, interval = 15 }  -- threshold in tenths (10.5)
local HYSTERESIS = 2         -- tenths above the threshold before re-arming
local CHECK_EVERY = 0.25     -- seconds; 4 Hz is plenty for an alert

local nextCheck, nextCall, armed = 0, 0, true

local function wakeup()
  local now = os.clock()
  if now < nextCheck then return end          -- cheap early exit on most ticks
  nextCheck = now + CHECK_EVERY

  local src = cfg.source
  local v = src and src:value()
  if not v then return end

  local tenths = v * 10
  if tenths < cfg.threshold then
    if armed or now >= nextCall then
      system.playNumber(v, src:unit(), src:decimals())
      system.playHaptic(300)
      armed = false
      nextCall = now + cfg.interval
    end
  elseif tenths > cfg.threshold + HYSTERESIS then
    armed = true                               -- clearly recovered: next drop alerts immediately
  end
end

local function configure()
  local line = form.addLine("Source")
  form.addSourceField(line, nil, function() return cfg.source end, function(v) cfg.source = v end)

  line = form.addLine("Alert below")
  local f = form.addNumberField(line, nil, 0, 10000, function() return cfg.threshold end,
    function(v) cfg.threshold = v end)
  f:decimals(1)

  line = form.addLine("Repeat every")
  f = form.addNumberField(line, nil, 5, 120, function() return cfg.interval end,
    function(v) cfg.interval = v end)
  f:suffix("s")
end

local function read()
  cfg.source = storage.read("source")
  cfg.threshold = storage.read("threshold") or cfg.threshold
  cfg.interval = storage.read("interval") or cfg.interval
end

local function write()
  storage.write("source", cfg.source)
  storage.write("threshold", cfg.threshold)
  storage.write("interval", cfg.interval)
end

local function init()
  system.registerTask({ key = "lowalrt", name = "Low value alert",
    wakeup = wakeup, configure = configure, read = read, write = write })
end

return { init = init }
