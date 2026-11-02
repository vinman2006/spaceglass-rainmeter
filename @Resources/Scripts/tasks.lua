-- ============================================================================
-- SPACEGLASS — GOOGLE TASKS LUA CONTROLLER (@Resources/Scripts/tasks.lua)
-- Manages two-way Google Tasks synchronization via the local Python backend:
--   - Renders active (overdue/today/upcoming) and completed tasks
--   - Strikethrough + orange checkmark circle (#FF7A18) for completed tasks
--   - Click checkbox to complete or reopen a task in Google Tasks
--   - Delete task with confirmation dialog
--   - Switch between Google Task lists
--   - Collapsible completed tasks section
-- ============================================================================

local json_helper = nil
local displayedTasks = {}
local availableLists = {}
local currentListId = "@default"
local collapseCompleted = false
local rowY = { 52, 84, 116, 148 }

function Initialize()
    local scriptDir = SKIN:GetVariable('@') .. 'Scripts\\'
    local ok, mod = pcall(dofile, scriptDir .. 'json_helper.lua')
    if ok then json_helper = mod end
    currentListId = SKIN:GetVariable('SelectedTaskListId', '@default')
    collapseCompleted = (tonumber(SKIN:GetVariable('CollapseCompletedTasks', '0')) or 0) == 1
end

function Update()
    return 1
end

function HideAllTaskRows()
    for i = 1, 4 do
        SKIN:Bang('!SetOption', 'MeterTaskCheck' .. i, 'Hidden', '1')
        SKIN:Bang('!SetOption', 'MeterTaskText' .. i, 'Hidden', '1')
        SKIN:Bang('!SetOption', 'MeterTaskStrike' .. i, 'Hidden', '1')
        SKIN:Bang('!SetOption', 'MeterTaskDue' .. i, 'Hidden', '1')
        SKIN:Bang('!SetOption', 'MeterTaskDel' .. i, 'Hidden', '1')
    end
end

function ShowEmptyMessage(msg, showConnectBtn)
    HideAllTaskRows()
    SKIN:Bang('!SetOption', 'MeterTasksEmpty', 'Text', msg)
    SKIN:Bang('!SetOption', 'MeterTasksEmpty', 'Hidden', '0')
    local btnHidden = showConnectBtn and '0' or '1'
    SKIN:Bang('!SetOption', 'MeterTasksConnectBtnBg', 'Hidden', btnHidden)
    SKIN:Bang('!SetOption', 'MeterTasksConnectBtnText', 'Hidden', btnHidden)
    SKIN:Bang('!UpdateMeter', '*')
    SKIN:Bang('!Redraw')
end

function OnTasksReceived()
    local measure = SKIN:GetMeasure('MeasureTasksWebParser')
    if not measure then return end
    local raw = measure:GetStringValue()
    if not raw or raw == "" then
        ShowEmptyMessage("Backend unavailable. Retrying...", false)
        return
    end

    if not json_helper then return end
    local payload = json_helper.decode(raw)
    if not payload then
        ShowEmptyMessage("Unable to parse tasks response.", false)
        return
    end

    if payload.authenticated == false then
        SKIN:Bang('!SetOption', 'MeterTasksStatusBadge', 'Text', 'Not linked')
        SKIN:Bang('!SetOption', 'MeterTasksStatusBadgeBg', 'Hidden', '0')
        ShowEmptyMessage("Connect Google Account in Settings to sync Tasks.", true)
        return
    else
        local badge = (payload.source == "cache") and "Cached" or ""
        SKIN:Bang('!SetOption', 'MeterTasksStatusBadge', 'Text', badge)
        SKIN:Bang('!SetOption', 'MeterTasksStatusBadgeBg', 'Hidden', (badge == "") and "1" or "0")
        SKIN:Bang('!SetOption', 'MeterTasksConnectBtnBg', 'Hidden', '1')
        SKIN:Bang('!SetOption', 'MeterTasksConnectBtnText', 'Hidden', '1')
    end

    if payload.list_title and payload.list_title ~= "" then
        SKIN:Bang('!SetOption', 'MeterListTitle', 'Text', payload.list_title)
    end
    if type(payload.available_lists) == "table" then
        availableLists = payload.available_lists
    end

    local activeTasks = payload.active_tasks or {}
    local completedTasks = payload.completed_tasks or {}

    displayedTasks = {}
    for _, t in ipairs(activeTasks) do
        table.insert(displayedTasks, t)
    end
    if not collapseCompleted then
        for _, t in ipairs(completedTasks) do
            table.insert(displayedTasks, t)
        end
    end

    if #completedTasks > 0 then
        local toggleLabel = collapseCompleted
            and string.format("▸ Show completed (%d)", #completedTasks)
            or string.format("▾ Completed (%d)", #completedTasks)
        SKIN:Bang('!SetOption', 'MeterCompletedToggle', 'Text', toggleLabel)
    else
        SKIN:Bang('!SetOption', 'MeterCompletedToggle', 'Text', '')
    end

    if #displayedTasks == 0 then
        ShowEmptyMessage("No pending tasks. Click + to add one!")
        return
    end

    SKIN:Bang('!SetOption', 'MeterTasksEmpty', 'Hidden', '1')
    HideAllTaskRows()

    local count = math.min(#displayedTasks, 4)
    for i = 1, count do
        local task = displayedTasks[i]
        local isCompleted = (task.status == "completed")
        local iconFile = isCompleted and "checkbox_checked_orange.png" or "checkbox_unchecked.png"
        local textColor = isCompleted and "#TextMuted#" or "#TextPrimary#"
        local titleStr = task.title or "(Untitled task)"

        SKIN:Bang('!SetOption', 'MeterTaskCheck' .. i, 'ImageName', '#@#Icons\\' .. iconFile)
        SKIN:Bang('!SetOption', 'MeterTaskCheck' .. i, 'Hidden', '0')

        SKIN:Bang('!SetOption', 'MeterTaskText' .. i, 'Text', titleStr)
        SKIN:Bang('!SetOption', 'MeterTaskText' .. i, 'FontColor', textColor)
        SKIN:Bang('!SetOption', 'MeterTaskText' .. i, 'Hidden', '0')

        if isCompleted then
            local approxWidth = math.min(200, math.max(40, string.len(titleStr) * 6.8))
            local lineY = rowY[i] + 9
            SKIN:Bang('!SetOption', 'MeterTaskStrike' .. i, 'Shape',
                string.format("Line 50,%d,%d,%d | StrokeWidth 1.2 | Stroke Color #TextMuted#", lineY, 50 + approxWidth, lineY))
            SKIN:Bang('!SetOption', 'MeterTaskStrike' .. i, 'Hidden', '0')
        else
            SKIN:Bang('!SetOption', 'MeterTaskStrike' .. i, 'Hidden', '1')
        end

        if task.is_overdue and not isCompleted then
            SKIN:Bang('!SetOption', 'MeterTaskDue' .. i, 'Text', task.due_label or "Overdue")
            SKIN:Bang('!SetOption', 'MeterTaskDue' .. i, 'FontColor', '#DangerColor#')
            SKIN:Bang('!SetOption', 'MeterTaskDue' .. i, 'Hidden', '0')
        elseif task.due_label and task.due_label ~= "" and not isCompleted then
            SKIN:Bang('!SetOption', 'MeterTaskDue' .. i, 'Text', task.due_label)
            SKIN:Bang('!SetOption', 'MeterTaskDue' .. i, 'FontColor', '#TextMuted#')
            SKIN:Bang('!SetOption', 'MeterTaskDue' .. i, 'Hidden', '0')
        else
            SKIN:Bang('!SetOption', 'MeterTaskDue' .. i, 'Hidden', '1')
        end

        SKIN:Bang('!SetOption', 'MeterTaskDel' .. i, 'Hidden', '0')
    end

    SKIN:Bang('!UpdateMeter', '*')
    SKIN:Bang('!Redraw')
end

function OnTasksError()
    SKIN:Bang('!SetOption', 'MeterTasksStatusBadge', 'Text', 'Offline')
    SKIN:Bang('!SetOption', 'MeterTasksStatusBadgeBg', 'Hidden', '0')
    if #displayedTasks == 0 then
        ShowEmptyMessage("SpaceGlass backend is offline.", false)
    end
end

function ToggleTask(slotIndex)
    local idx = tonumber(slotIndex)
    local task = displayedTasks[idx]
    if not task or not task.id then return end

    local nextStatus = (task.status == "completed") and "needsAction" or "completed"
    local scriptPath = SKIN:GetVariable('@') .. '..\\Backend\\companion_ui.py'
    local param = string.format('"%s" --action toggle-task --list-id "%s" --task-id "%s" --status "%s"',
        scriptPath, currentListId, task.id, nextStatus)

    SKIN:Bang('!SetOption', 'MeasureTaskMutationRunner', 'Parameter', param)
    SKIN:Bang('!UpdateMeasure', 'MeasureTaskMutationRunner')
    SKIN:Bang('!CommandMeasure', 'MeasureTaskMutationRunner', 'Run')
end

function DeleteTask(slotIndex)
    local idx = tonumber(slotIndex)
    local task = displayedTasks[idx]
    if not task or not task.id then return end

    local scriptPath = SKIN:GetVariable('@') .. '..\\Backend\\companion_ui.py'
    local safeTitle = string.gsub(task.title or "Task", '"', "'")
    local param = string.format('"%s" --action delete-task --list-id "%s" --task-id "%s" --title "%s"',
        scriptPath, currentListId, task.id, safeTitle)

    SKIN:Bang('!SetOption', 'MeasureTaskMutationRunner', 'Parameter', param)
    SKIN:Bang('!UpdateMeasure', 'MeasureTaskMutationRunner')
    SKIN:Bang('!CommandMeasure', 'MeasureTaskMutationRunner', 'Run')
end

function ToggleCompletedSection()
    collapseCompleted = not collapseCompleted
    local val = collapseCompleted and '1' or '0'
    SKIN:Bang('!SetVariable', 'CollapseCompletedTasks', val)
    SKIN:Bang('!WriteKeyValue', 'Variables', 'CollapseCompletedTasks', val, '#@#Variables.inc')
    OnTasksReceived()
end

function CycleTaskList()
    if #availableLists <= 1 then
        local scriptPath = SKIN:GetVariable('@') .. '..\\Backend\\companion_ui.py'
        SKIN:Bang('!Execute', {'"pythonw.exe" "' .. scriptPath .. '" --tab google'})
        return
    end
    local nextIndex = 1
    for i, lst in ipairs(availableLists) do
        if lst.id == currentListId then
            nextIndex = (i % #availableLists) + 1
            break
        end
    end
    local chosen = availableLists[nextIndex]
    if chosen and chosen.id then
        currentListId = chosen.id
        SKIN:Bang('!SetVariable', 'SelectedTaskListId', chosen.id)
        SKIN:Bang('!SetVariable', 'SelectedTaskListName', chosen.title or "My Tasks")
        SKIN:Bang('!WriteKeyValue', 'Variables', 'SelectedTaskListId', chosen.id, '#@#Variables.inc')
        SKIN:Bang('!WriteKeyValue', 'Variables', 'SelectedTaskListName', chosen.title or "My Tasks", '#@#Variables.inc')
        local baseUrl = SKIN:GetVariable('BackendBaseUrl', 'http://127.0.0.1:8765')
        local url = string.format("%s/api/tasks?list_id=%s&include_completed=1", baseUrl, json_helper.url_encode(chosen.id))
        SKIN:Bang('!SetOption', 'MeasureTasksWebParser', 'URL', url)
        SKIN:Bang('!UpdateMeasure', 'MeasureTasksWebParser')
        SKIN:Bang('!CommandMeasure', 'MeasureTasksWebParser', 'Update')
    end
end
