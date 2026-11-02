-- ============================================================================
-- SPACEGLASS — CLOCK & WEATHER LUA CONTROLLER (@Resources/Scripts/clock_weather.lua)
-- Handles 12/24-hour clock format switching, weather JSON parsing, and
-- graceful hiding if weather is disabled or unavailable.
-- ============================================================================

local json_helper = nil

function Initialize()
    local scriptDir = SKIN:GetVariable('@') .. 'Scripts\\'
    local ok, mod = pcall(dofile, scriptDir .. 'json_helper.lua')
    if ok then
        json_helper = mod
    end
    ApplyClockFormat()
    ApplyWeatherVisibility()
end

function Update()
    ApplyClockFormat()
    return 1
end

function ApplyClockFormat()
    local use24 = tonumber(SKIN:GetVariable('Use24Hour', '1')) or 1
    local timeStr = ''
    if use24 == 1 then
        local m24 = SKIN:GetMeasure('MeasureTime24')
        if m24 then timeStr = m24:GetStringValue() end
    else
        local m12 = SKIN:GetMeasure('MeasureTime12')
        if m12 then timeStr = m12:GetStringValue() end
    end
    if timeStr ~= '' then
        SKIN:Bang('!SetOption', 'MeterTime', 'Text', timeStr)
    end
end

function ToggleClockFormat()
    local use24 = tonumber(SKIN:GetVariable('Use24Hour', '1')) or 1
    local nextVal = (use24 == 1) and '0' or '1'
    SKIN:Bang('!SetVariable', 'Use24Hour', nextVal)
    SKIN:Bang('!WriteKeyValue', 'Variables', 'Use24Hour', nextVal, '#@#Variables.inc')
    ApplyClockFormat()
    SKIN:Bang('!UpdateMeter', 'MeterTime')
    SKIN:Bang('!Redraw')
end

function ApplyWeatherVisibility()
    local enabled = tonumber(SKIN:GetVariable('WeatherEnabled', '1')) or 1
    if enabled == 0 then
        HideWeatherMeters(true)
    end
end

function HideWeatherMeters(hidden)
    local hVal = hidden and '1' or '0'
    SKIN:Bang('!SetOption', 'MeterWeatherIcon', 'Hidden', hVal)
    SKIN:Bang('!SetOption', 'MeterWeatherTemp', 'Hidden', hVal)
    SKIN:Bang('!SetOption', 'MeterWeatherCity', 'Hidden', hVal)
    SKIN:Bang('!UpdateMeterGroup', 'Weather')
    SKIN:Bang('!Redraw')
end

function OnWeatherResponse()
    local enabled = tonumber(SKIN:GetVariable('WeatherEnabled', '1')) or 1
    if enabled == 0 then
        HideWeatherMeters(true)
        return
    end

    local measure = SKIN:GetMeasure('MeasureWeatherWebParser')
    if not measure then
        HideWeatherMeters(true)
        return
    end

    local raw = measure:GetStringValue()
    if not raw or raw == '' then
        HideWeatherMeters(true)
        return
    end

    if json_helper then
        local data = json_helper.decode(raw)
        if data and data.available == true and data.temperature ~= nil then
            local tempText = tostring(math.floor(tonumber(data.temperature) + 0.5)) .. '°'
            local cityText = data.city or SKIN:GetVariable('CityName', 'Nagpur')
            local iconName = data.icon or 'weather_partly_cloudy.png'
            SKIN:Bang('!SetOption', 'MeterWeatherTemp', 'Text', tempText)
            SKIN:Bang('!SetOption', 'MeterWeatherCity', 'Text', cityText)
            SKIN:Bang('!SetOption', 'MeterWeatherIcon', 'ImageName', '#@#Icons\\' .. iconName)
            HideWeatherMeters(false)
            return
        end
    end

    -- Fallback regex extraction if JSON helper wasn't loaded or available is false
    local avail = string.match(raw, '"available"%s*:%s*(true)')
    local temp = string.match(raw, '"temperature"%s*:%s*([%-]?%d+%.?%d*)')
    local city = string.match(raw, '"city"%s*:%s*"([^"]+)"')
    local icon = string.match(raw, '"icon"%s*:%s*"([^"]+)"')
    if avail and temp then
        local tempRounded = tostring(math.floor(tonumber(temp) + 0.5)) .. '°'
        SKIN:Bang('!SetOption', 'MeterWeatherTemp', 'Text', tempRounded)
        if city then
            SKIN:Bang('!SetOption', 'MeterWeatherCity', 'Text', city)
        end
        if icon then
            SKIN:Bang('!SetOption', 'MeterWeatherIcon', 'ImageName', '#@#Icons\\' .. icon)
        end
        HideWeatherMeters(false)
    else
        HideWeatherMeters(true)
    end
end

function OnWeatherError()
    -- Never fabricate weather information; hide gracefully if unconfigured or unreachable
    HideWeatherMeters(true)
end
