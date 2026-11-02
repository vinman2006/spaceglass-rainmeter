; ============================================================================
; SPACEGLASS — CENTRAL USER VARIABLES (@Resources/Variables.inc)
; Your Universe. Your Schedule.
; ============================================================================
[Variables]
; --- Application Info ---
AppName=SpaceGlass
AppVersion=1.0.0
AppTagline=Your Universe. Your Schedule.

; --- Backend Connection ---
BackendHost=127.0.0.1
BackendPort=8765
BackendBaseUrl=http://127.0.0.1:8765

; --- Unified Geometry & Layout Tokens ---
CardWidth=330
CardRadius=18
RightMargin=24
TopMargin=20
WidgetGap=14

ClockHeight=105
CalendarHeight=224
EventsHeight=135
TasksHeight=135

; Backward compatibility alias
WidgetWidth=320

; --- Unified Color Tokens ---
BgGradTop=32,24,20,215
BgGradBottom=22,16,14,230
CardBorder=255,255,255,28
AccentOrange=240,123,26
AccentOrangeHex=F07B1A

; --- Calculated Coordinates ---
DefaultX=(#WORKAREAX# + #WORKAREAWIDTH# - #CardWidth# - #RightMargin#)
ClockY=(#WORKAREAY# + #TopMargin#)
CalendarY=(#WORKAREAY# + #TopMargin# + #ClockHeight# + #WidgetGap#)
EventsY=(#WORKAREAY# + #TopMargin# + #ClockHeight# + #WidgetGap# + #CalendarHeight# + #WidgetGap#)
TasksY=(#WORKAREAY# + #TopMargin# + #ClockHeight# + #WidgetGap# + #CalendarHeight# + #WidgetGap# + #EventsHeight# + #WidgetGap#)

; --- Clock & Weather Preferences ---
Use24Hour=1
TimeFormat=%H:%M
TimeFormat12=%I:%M %p
ShowAmPm=0
CityName=Nagpur
Latitude=21.1458
Longitude=79.0882
TemperatureUnit=C
WeatherEnabled=1
WeatherRefreshSeconds=900

; --- Calendar Preferences ---
WeekStartMonday=0
CalendarRefreshSeconds=900
SelectedCalendarId=primary
GoogleCalendarWebUrl=https://calendar.google.com/calendar/r
GoogleCalendarNewEventUrl=https://calendar.google.com/calendar/u/0/r/eventedit

; --- Events Preferences ---
MaxUpcomingEvents=4
EventsRefreshSeconds=900

; --- Tasks Preferences ---
SelectedTaskListId=@default
SelectedTaskListName=My Tasks
TasksRefreshSeconds=900
ShowCompletedTasks=1
CollapseCompletedTasks=0
GoogleTasksWebUrl=https://tasks.google.com/
