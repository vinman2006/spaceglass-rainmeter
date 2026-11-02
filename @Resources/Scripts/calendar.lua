-- ============================================================================
-- SPACEGLASS — INTERACTIVE MONTHLY CALENDAR ENGINE (@Resources/Scripts/calendar.lua)
-- Implements exact Gregorian leap-year calendar math, Sunday/Monday week start,
-- previous/next month navigation, orange pill today highlight, colored Google
-- Calendar event dots, and click-a-date event inspection.
-- ============================================================================

local json_helper = nil
local displayedYear = 2026
local displayedMonth = 11
local selectedDay = nil
local selectedDateEvents = {}
local selectedDateUrl = nil
local monthEventsByDay = {} -- day_number -> { count = n, color = "166,108,219", events = {...} }
local isOfflineCached = false

-- Base grid geometry (7 cols x 6 rows) scaled dynamically via getScale()
local baseCols = { 33, 77, 121, 165, 209, 253, 297 }
local baseRows = { 68, 93, 118, 143, 168, 193 }

local function getScale()
    return tonumber(SKIN:GetVariable('Scale', '1.0')) or 1.0
end

local monthNames = {
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
}
local dowSunFirst = { "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat" }
local dowMonFirst = { "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" }

function IsLeapYear(year)
    return (year % 4 == 0 and year % 100 ~= 0) or (year % 400 == 0)
end

function GetDaysInMonth(year, month)
    local days = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 }
    if month == 2 and IsLeapYear(year) then
        return 29
    end
    return days[month] or 30
end

-- Sakamoto's algorithm: returns 0 = Sunday .. 6 = Saturday
function GetDayOfWeek(year, month, day)
    local t = { 0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4 }
    local y = year
    if month < 3 then
        y = y - 1
    end
    return (y + math.floor(y / 4) - math.floor(y / 100) + math.floor(y / 400) + t[month] + day) % 7
end

function Initialize()
    local scriptDir = SKIN:GetVariable('@') .. 'Scripts\\'
    local ok, mod = pcall(dofile, scriptDir .. 'json_helper.lua')
    if ok then json_helper = mod end

    local now = os.date("*t")
    displayedYear = now.year
    displayedMonth = now.month
    selectedDay = now.day

    RefreshBackendMonthUrl()
    RenderCalendarGrid()
end

function Update()
    return 1
end

function RefreshBackendMonthUrl()
    local baseUrl = SKIN:GetVariable('BackendBaseUrl', 'http://127.0.0.1:8765')
    local url = string.format("%s/api/calendar/month?year=%d&month=%d", baseUrl, displayedYear, displayedMonth)
    SKIN:Bang('!SetOption', 'MeasureMonthWebParser', 'URL', url)
    SKIN:Bang('!UpdateMeasure', 'MeasureMonthWebParser')
    SKIN:Bang('!CommandMeasure', 'MeasureMonthWebParser', 'Update')
end

function NavigateMonth(delta)
    displayedMonth = displayedMonth + tonumber(delta)
    if displayedMonth > 12 then
        displayedMonth = 1
        displayedYear = displayedYear + 1
    elseif displayedMonth < 1 then
        displayedMonth = 12
        displayedYear = displayedYear - 1
    end
    selectedDay = nil
    monthEventsByDay = {}
    RenderCalendarGrid()
    RefreshBackendMonthUrl()
end

function JumpToToday()
    local now = os.date("*t")
    displayedYear = now.year
    displayedMonth = now.month
    selectedDay = now.day
    monthEventsByDay = {}
    RenderCalendarGrid()
    RefreshBackendMonthUrl()
end

function ToggleWeekStart()
    local cur = tonumber(SKIN:GetVariable('WeekStartMonday', '0')) or 0
    local nextVal = (cur == 1) and '0' or '1'
    SKIN:Bang('!SetVariable', 'WeekStartMonday', nextVal)
    SKIN:Bang('!WriteKeyValue', 'Variables', 'WeekStartMonday', nextVal, '#@#Variables.inc')
    RenderCalendarGrid()
end

function SelectDay(cellIndex)
    local cellMeter = SKIN:GetMeter('MeterCell' .. tostring(cellIndex))
    if not cellMeter then return end
    local dayNum = tonumber(cellMeter:GetOption('Text'))
    if not dayNum then return end

    selectedDay = dayNum
    RenderCalendarGrid()
end

function OpenSelectedDateInBrowser()
    if selectedDateUrl and selectedDateUrl ~= "" then
        SKIN:Bang('"' .. selectedDateUrl .. '"')
        return
    end
    if selectedDay then
        local url = string.format("https://calendar.google.com/calendar/r/day/%d/%d/%d", displayedYear, displayedMonth, selectedDay)
        SKIN:Bang('"' .. url .. '"')
    else
        local webUrl = SKIN:GetVariable('GoogleCalendarWebUrl', 'https://calendar.google.com/calendar/r')
        SKIN:Bang('"' .. webUrl .. '"')
    end
end

function OnMonthDataReceived()
    local measure = SKIN:GetMeasure('MeasureMonthWebParser')
    if not measure then return end
    local raw = measure:GetStringValue()
    if not raw or raw == "" then return end

    monthEventsByDay = {}
    isOfflineCached = false

    if json_helper then
        local payload = json_helper.decode(raw)
        if payload then
            isOfflineCached = (payload.source == "cache")
            if type(payload.days) == "table" then
                for dayKey, dayInfo in pairs(payload.days) do
                    local dNum = tonumber(dayKey)
                    if dNum and type(dayInfo) == "table" then
                        monthEventsByDay[dNum] = {
                            count = tonumber(dayInfo.count) or 1,
                            color = dayInfo.color_rgb or "166,108,219",
                            events = dayInfo.events or {}
                        }
                    end
                end
            end
        end
    end
    RenderCalendarGrid()
end

function OnBackendOffline()
    isOfflineCached = true
    RenderCalendarGrid()
end

function RenderCalendarGrid()
    local weekStartMonday = (tonumber(SKIN:GetVariable('WeekStartMonday', '0')) or 0) == 1
    local headers = weekStartMonday and dowMonFirst or dowSunFirst
    for i = 1, 7 do
        SKIN:Bang('!SetOption', 'MeterDOW' .. i, 'Text', headers[i])
    end

    local titleStr = string.format("%s %d", monthNames[displayedMonth] or "Month", displayedYear)
    SKIN:Bang('!SetOption', 'MeterMonthTitle', 'Text', titleStr)

    local firstDow = GetDayOfWeek(displayedYear, displayedMonth, 1) -- 0=Sun..6=Sat
    local offset = firstDow
    if weekStartMonday then
        offset = (firstDow + 6) % 7
    end

    local totalDays = GetDaysInMonth(displayedYear, displayedMonth)
    local now = os.date("*t")
    local isCurrentMonth = (now.year == displayedYear and now.month == displayedMonth)

    local todayPillHidden = "1"
    local selectedRingHidden = "1"
    local scale = getScale()

    for cell = 1, 42 do
        local dayNum = cell - offset
        local col = ((cell - 1) % 7) + 1
        local row = math.floor((cell - 1) / 7) + 1
        local cx = math.floor(baseCols[col] * scale + 0.5)
        local cy = math.floor(baseRows[row] * scale + 0.5)

        local cellName = 'MeterCell' .. cell
        local dotName  = 'MeterDot' .. cell

        if dayNum >= 1 and dayNum <= totalDays then
            SKIN:Bang('!SetOption', cellName, 'Text', tostring(dayNum))
            SKIN:Bang('!SetOption', cellName, 'X', tostring(cx))
            SKIN:Bang('!SetOption', cellName, 'Y', tostring(cy))
            SKIN:Bang('!SetOption', cellName, 'Hidden', '0')

            local isToday = isCurrentMonth and (dayNum == now.day)
            if isToday then
                SKIN:Bang('!SetOption', cellName, 'FontWeight', '700')
                SKIN:Bang('!SetOption', cellName, 'FontColor', '#TextPrimary#')
                local pillW = math.floor(32 * scale + 0.5)
                local pillH = math.floor(24 * scale + 0.5)
                local pillR = math.floor(12 * scale + 0.5)
                local pillX = math.floor(cx - (16 * scale) + 0.5)
                local pillY = math.floor(cy - (5 * scale) + 0.5)
                SKIN:Bang('!SetOption', 'MeterTodayPill', 'Shape',
                    string.format("Rectangle %d,%d,%d,%d,%d | Fill Color #AccentOrange#,255 | StrokeWidth 0", pillX, pillY, pillW, pillH, pillR))
                todayPillHidden = "0"
            else
                SKIN:Bang('!SetOption', cellName, 'FontWeight', '400')
                SKIN:Bang('!SetOption', cellName, 'FontColor', '#TextPrimary#')
            end

            if selectedDay == dayNum and not isToday then
                local ringW = math.floor(32 * scale + 0.5)
                local ringH = math.floor(24 * scale + 0.5)
                local ringR = math.floor(12 * scale + 0.5)
                local ringX = math.floor(cx - (16 * scale) + 0.5)
                local ringY = math.floor(cy - (5 * scale) + 0.5)
                local strokeW = math.max(1, math.floor(1 * scale + 0.5))
                SKIN:Bang('!SetOption', 'MeterSelectedDateRing', 'Shape',
                    string.format("Rectangle %d,%d,%d,%d,%d | Fill Color 255,255,255,22 | StrokeWidth %d | Stroke Color #CosmicBlue#,220", ringX, ringY, ringW, ringH, ringR, strokeW))
                selectedRingHidden = "0"
            end

            local evInfo = monthEventsByDay[dayNum]
            if evInfo and evInfo.count and evInfo.count > 0 then
                local dotColor = evInfo.color or "166,108,219"
                local dotR = math.max(2, math.floor(2 * scale + 0.5))
                local dotY = math.floor(cy + (15 * scale) + 0.5)
                SKIN:Bang('!SetOption', dotName, 'Shape',
                    string.format("Ellipse %d,%d,%d,%d | Fill Color %s,255 | StrokeWidth 0", cx, dotY, dotR, dotR, dotColor))
                SKIN:Bang('!SetOption', dotName, 'Hidden', '0')
            else
                SKIN:Bang('!SetOption', dotName, 'Hidden', '1')
            end
        else
            SKIN:Bang('!SetOption', cellName, 'Text', '')
            SKIN:Bang('!SetOption', cellName, 'Hidden', '1')
            SKIN:Bang('!SetOption', dotName, 'Hidden', '1')
        end
    end

    SKIN:Bang('!SetOption', 'MeterTodayPill', 'Hidden', todayPillHidden)
    SKIN:Bang('!SetOption', 'MeterSelectedDateRing', 'Hidden', selectedRingHidden)

    -- Update bottom selected-date summary line
    selectedDateUrl = nil
    if selectedDay and monthEventsByDay[selectedDay] and monthEventsByDay[selectedDay].events then
        local evs = monthEventsByDay[selectedDay].events
        if #evs > 0 then
            local firstEv = evs[1]
            selectedDateUrl = firstEv.html_link
            local prefix = isOfflineCached and "[Cached] " or ""
            local extra = (#evs > 1) and string.format(" (+%d more)", #evs - 1) or ""
            local summary = string.format("%s%s %d: %s (%s)%s",
                prefix, string.sub(monthNames[displayedMonth], 1, 3), selectedDay,
                firstEv.title or "Event", firstEv.time_label or "All day", extra)
            SKIN:Bang('!SetOption', 'MeterSelectedDateInfo', 'Text', summary)
        else
            SKIN:Bang('!SetOption', 'MeterSelectedDateInfo', 'Text', '')
        end
    else
        SKIN:Bang('!SetOption', 'MeterSelectedDateInfo', 'Text', '')
    end

    SKIN:Bang('!UpdateMeter', '*')
    SKIN:Bang('!Redraw')
end
