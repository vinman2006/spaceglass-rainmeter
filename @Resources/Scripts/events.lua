-- ============================================================================
-- SPACEGLASS — UPCOMING EVENTS LUA CONTROLLER (@Resources/Scripts/events.lua)
-- Parses upcoming events from GET /api/calendar/events, updates color bars,
-- manages status badge and interactive connect button for unlinked states.
-- ============================================================================

local json_helper = nil
local currentEvents = {}
local slotY = { 50, 90, 130 }
local defaultColors = { "166,108,219", "88,166,255", "255,122,24" }

function Initialize()
    local scriptDir = SKIN:GetVariable('@') .. 'Scripts\\'
    local ok, mod = pcall(dofile, scriptDir .. 'json_helper.lua')
    if ok then json_helper = mod end
end

function Update()
    return 1
end

function HideAllEventSlots()
    for i = 1, 3 do
        SKIN:Bang('!SetOption', 'MeterEventBar' .. i, 'Hidden', '1')
        SKIN:Bang('!SetOption', 'MeterEventTitle' .. i, 'Hidden', '1')
        SKIN:Bang('!SetOption', 'MeterEventSub' .. i, 'Hidden', '1')
    end
end

function SetEmptyState(message, showConnectBtn)
    HideAllEventSlots()
    SKIN:Bang('!SetOption', 'MeterEmptyState', 'Text', message)
    SKIN:Bang('!SetOption', 'MeterEmptyState', 'Hidden', '0')
    local btnHidden = showConnectBtn and '0' or '1'
    SKIN:Bang('!SetOption', 'MeterConnectBtnBg', 'Hidden', btnHidden)
    SKIN:Bang('!SetOption', 'MeterConnectBtnText', 'Hidden', btnHidden)
    SKIN:Bang('!UpdateMeter', '*')
    SKIN:Bang('!Redraw')
end

function OnEventsReceived()
    local measure = SKIN:GetMeasure('MeasureEventsWebParser')
    if not measure then return end
    local raw = measure:GetStringValue()
    if not raw or raw == "" then
        SetEmptyState("Backend unavailable. Retrying...", false)
        return
    end

    if not json_helper then return end
    local payload = json_helper.decode(raw)
    if not payload then
        SetEmptyState("Unable to parse calendar response.", false)
        return
    end

    if payload.authenticated == false then
        SKIN:Bang('!SetOption', 'MeterSyncBadge', 'Text', 'Not linked')
        SKIN:Bang('!SetOption', 'MeterSyncBadgeBg', 'Hidden', '0')
        SetEmptyState("Connect Google Account in Settings to view events.", true)
        return
    else
        local badge = (payload.source == "cache") and "Cached" or ""
        SKIN:Bang('!SetOption', 'MeterSyncBadge', 'Text', badge)
        SKIN:Bang('!SetOption', 'MeterSyncBadgeBg', 'Hidden', (badge == "") and "1" or "0")
        SKIN:Bang('!SetOption', 'MeterConnectBtnBg', 'Hidden', '1')
        SKIN:Bang('!SetOption', 'MeterConnectBtnText', 'Hidden', '1')
    end

    local items = payload.events or {}
    currentEvents = items

    if #items == 0 then
        SetEmptyState("No upcoming events. Enjoy your free time!", false)
        return
    end

    SKIN:Bang('!SetOption', 'MeterEmptyState', 'Hidden', '1')
    SKIN:Bang('!SetOption', 'MeterConnectBtnBg', 'Hidden', '1')
    SKIN:Bang('!SetOption', 'MeterConnectBtnText', 'Hidden', '1')
    HideAllEventSlots()

    local count = math.min(#items, 2)
    for i = 1, count do
        local ev = items[i]
        local barColor = ev.color_rgb or defaultColors[i] or "166,108,219"
        local yBar = slotY[i]
        SKIN:Bang('!SetOption', 'MeterEventBar' .. i, 'Shape',
            string.format("Rectangle 22,%d,4,30,2 | Fill Color %s,255 | StrokeWidth 0", yBar, barColor))
        SKIN:Bang('!SetOption', 'MeterEventBar' .. i, 'Hidden', '0')

        SKIN:Bang('!SetOption', 'MeterEventTitle' .. i, 'Text', ev.title or "(No title)")
        SKIN:Bang('!SetOption', 'MeterEventTitle' .. i, 'Hidden', '0')

        SKIN:Bang('!SetOption', 'MeterEventSub' .. i, 'Text', ev.display_time or "")
        SKIN:Bang('!SetOption', 'MeterEventSub' .. i, 'Hidden', '0')
    end

    SKIN:Bang('!UpdateMeter', '*')
    SKIN:Bang('!Redraw')
end

function OnEventsError()
    SKIN:Bang('!SetOption', 'MeterSyncBadge', 'Text', 'Offline')
    SKIN:Bang('!SetOption', 'MeterSyncBadgeBg', 'Hidden', '0')
    if #currentEvents == 0 then
        SetEmptyState("SpaceGlass backend is offline.", false)
    end
end

function OpenEvent(slotIndex)
    local idx = tonumber(slotIndex)
    local ev = currentEvents[idx]
    if ev and ev.html_link and ev.html_link ~= "" then
        SKIN:Bang('"' .. ev.html_link .. '"')
    else
        local fallbackUrl = SKIN:GetVariable('GoogleCalendarWebUrl', 'https://calendar.google.com/calendar/r')
        SKIN:Bang('"' .. fallbackUrl .. '"')
    end
end
