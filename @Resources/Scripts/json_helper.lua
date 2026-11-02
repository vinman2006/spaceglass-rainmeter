-- ============================================================================
-- SPACEGLASS — PURE LUA 5.1 JSON DECODER & URL HELPER (@Resources/Scripts/json_helper.lua)
-- Lightweight, dependency-free JSON parser for Rainmeter Lua 5.1 environment.
-- ============================================================================

local json = {}

local function skip_whitespace(str, idx)
    local _, next_idx = string.find(str, "^[ \t\r\n]*", idx)
    return (next_idx or idx - 1) + 1
end

local parse_value

local function parse_string(str, idx)
    idx = idx + 1 -- skip opening quote
    local res = {}
    local len = string.len(str)
    while idx <= len do
        local c = string.sub(str, idx, idx)
        if c == '"' then
            return table.concat(res), idx + 1
        elseif c == '\\' then
            idx = idx + 1
            local esc = string.sub(str, idx, idx)
            if esc == '"' or esc == '\\' or esc == '/' then
                table.insert(res, esc)
            elseif esc == 'b' then table.insert(res, '\b')
            elseif esc == 'f' then table.insert(res, '\f')
            elseif esc == 'n' then table.insert(res, '\n')
            elseif esc == 'r' then table.insert(res, '\r')
            elseif esc == 't' then table.insert(res, '\t')
            elseif esc == 'u' then
                local hex = string.sub(str, idx + 1, idx + 4)
                local code = tonumber(hex, 16) or 63
                if code < 128 then
                    table.insert(res, string.char(code))
                elseif code < 2048 then
                    table.insert(res, string.char(192 + math.floor(code / 64), 128 + (code % 64)))
                else
                    table.insert(res, string.char(
                        224 + math.floor(code / 4096),
                        128 + (math.floor(code / 64) % 64),
                        128 + (code % 64)
                    ))
                end
                idx = idx + 4
            end
            idx = idx + 1
        else
            table.insert(res, c)
            idx = idx + 1
        end
    end
    return table.concat(res), idx
end

local function parse_number(str, idx)
    local s, e = string.find(str, "^-?%d+%.?%d*[eE]?[+-]?%d*", idx)
    if s then
        local num_str = string.sub(str, s, e)
        return tonumber(num_str), e + 1
    end
    return nil, idx + 1
end

local function parse_array(str, idx)
    idx = skip_whitespace(str, idx + 1)
    local arr = {}
    if string.sub(str, idx, idx) == ']' then
        return arr, idx + 1
    end
    local i = 1
    while idx <= string.len(str) do
        local val
        val, idx = parse_value(str, idx)
        arr[i] = val
        i = i + 1
        idx = skip_whitespace(str, idx)
        local c = string.sub(str, idx, idx)
        if c == ']' then
            return arr, idx + 1
        elseif c == ',' then
            idx = skip_whitespace(str, idx + 1)
        else
            break
        end
    end
    return arr, idx
end

local function parse_object(str, idx)
    idx = skip_whitespace(str, idx + 1)
    local obj = {}
    if string.sub(str, idx, idx) == '}' then
        return obj, idx + 1
    end
    while idx <= string.len(str) do
        idx = skip_whitespace(str, idx)
        if string.sub(str, idx, idx) ~= '"' then break end
        local key
        key, idx = parse_string(str, idx)
        idx = skip_whitespace(str, idx)
        if string.sub(str, idx, idx) == ':' then
            idx = skip_whitespace(str, idx + 1)
        end
        local val
        val, idx = parse_value(str, idx)
        if key ~= nil then
            obj[key] = val
        end
        idx = skip_whitespace(str, idx)
        local c = string.sub(str, idx, idx)
        if c == '}' then
            return obj, idx + 1
        elseif c == ',' then
            idx = skip_whitespace(str, idx + 1)
        else
            break
        end
    end
    return obj, idx
end

parse_value = function(str, idx)
    idx = skip_whitespace(str, idx)
    local c = string.sub(str, idx, idx)
    if c == '"' then
        return parse_string(str, idx)
    elseif c == '{' then
        return parse_object(str, idx)
    elseif c == '[' then
        return parse_array(str, idx)
    elseif c == 't' and string.sub(str, idx, idx + 3) == 'true' then
        return true, idx + 4
    elseif c == 'f' and string.sub(str, idx, idx + 4) == 'false' then
        return false, idx + 5
    elseif c == 'n' and string.sub(str, idx, idx + 3) == 'null' then
        return nil, idx + 4
    else
        return parse_number(str, idx)
    end
end

function json.decode(str)
    if type(str) ~= "string" or str == "" then
        return nil
    end
    local ok, res = pcall(function()
        local val, _ = parse_value(str, 1)
        return val
    end)
    if ok then return res end
    return nil
end

function json.url_encode(str)
    if not str then return "" end
    str = string.gsub(str, "\n", "\r\n")
    str = string.gsub(str, "([^%w %-%_%.%~])", function(c)
        return string.format("%%%02X", string.byte(c))
    end)
    str = string.gsub(str, " ", "+")
    return str
end

return json
