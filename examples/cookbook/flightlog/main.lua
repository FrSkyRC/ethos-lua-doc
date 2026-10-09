-- Flight log tool: a System menu tool with a settings form, file-based
-- settings, a confirmation dialog and proper cleanup on close.
-- https://frskyrc.github.io/ethos-lua-doc/cookbook/system-tool/

-- Use absolute paths for files touched from callbacks. Relative paths only
-- resolve against this script's folder while main.lua is loading; later
-- (e.g. in close()) they resolve against whichever script Ethos loaded last.
local BASE = "SCRIPTS:/flightlog/"
local SETTINGS = BASE .. "settings.lua"
local LOG_DIR = "LOGS:/flightlog"

local state   -- everything the open page owns; nil while closed

---------------------------------------------------------------- settings file
local function loadSettings()
  local chunk = loadfile(SETTINGS)
  local ok, t = pcall(chunk or function() return nil end)
  t = (ok and type(t) == "table") and t or {}
  t.pilot = t.pilot or ""
  t.units = t.units or 0
  t.keepDays = t.keepDays or 30
  return t
end

local function saveSettings(t)
  local f = io.open(SETTINGS, "w")
  if not f then return false end
  f:write(string.format("return { pilot = %q, units = %d, keepDays = %d }\n", t.pilot, t.units, t.keepDays))
  f:close()
  return true
end

---------------------------------------------------------------- actions
local function clearLogs()
  if os.stat(LOG_DIR) then os.rmtree(LOG_DIR) end
  -- os.mkdir is not recursive: LOGS: itself may not exist yet on a fresh radio
  if not os.stat("LOGS:") then os.mkdir("LOGS:") end
  os.mkdir(LOG_DIR)
end

local UNITS = { { "Metric", 0 }, { "Imperial", 1 } }   -- built once

---------------------------------------------------------------- page
local function build()
  form.clear()
  local s = state.settings

  local line = form.addLine("Pilot name")
  form.addTextField(line, nil, function() return s.pilot end,
    function(v) s.pilot = v; state.dirty = true end)

  line = form.addLine("Units")
  form.addChoiceField(line, nil, UNITS, function() return s.units end,
    function(v) s.units = v; state.dirty = true end)

  line = form.addLine("Keep logs for")
  local f = form.addNumberField(line, nil, 1, 365, function() return s.keepDays end,
    function(v) s.keepDays = v; state.dirty = true end)
  f:suffix(" days")

  line = form.addLine("Logs")
  form.addButton(line, nil, {
    text = "Delete all",
    press = function()
      form.openDialog({
        title = "Delete logs",
        message = "Delete every flight log?",
        buttons = {
          { label = "Delete", action = function() clearLogs(); return true end },
          { label = "Cancel", action = function() return true end },
        },
        options = TEXT_LEFT,
      })
    end,
  })
end

local function create()
  state = { settings = loadSettings(), dirty = false }
  build()
  return state
end

local function close()
  if state and state.dirty then saveSettings(state.settings) end  -- write once, on close
  state = nil                                                    -- release everything the page held
end

local function init()
  -- the icon is required: without it Ethos logs "registerSystemTool(): missing icon"
  system.registerSystemTool({ name = "Flight log", icon = lcd.loadMask("icon.png"), create = create, close = close })
end

return { init = init }
