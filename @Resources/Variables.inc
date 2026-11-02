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

; --- Screen & Positioning Defaults ---
; Right-aligned floating stack: 24px from right edge, 20px from top edge
WidgetWidth=320
RightMargin=24
TopMargin=20
WidgetGap=14

; Calculated X coordinate for right-aligned widgets on primary or target monitor
DefaultX=(#WORKAREAX# + #WORKAREAWIDTH# - #WidgetWidth# - #RightMargin#)
ClockY=(#WORKAREAY# + #TopMargin#)
CalendarY=(#WORKAREAY# + #TopMargin# + 110 + #WidgetGap#)
EventsY=(#WORKAREAY# + #TopMargin# + 110 + #WidgetGap# + 220 + #WidgetGap#)
TasksY=(#WORKAREAY# + #TopMargin# + 110 + #WidgetGap# + 220 + #WidgetGap# + 160 + #WidgetGap#)

; --- Clock & Weather Preferences ---
; Use24Hour: 1 = 24-hour (19:30), 0 = 12-hour (07:30 PM)
Use24Hour=1
TimeFormat=%H:%M
TimeFormat12=%I:%M
ShowAmPm=0
CityName=Nagpur
Latitude=21.1458
Longitude=79.0882
TemperatureUnit=C
WeatherEnabled=1
WeatherRefreshSeconds=900

; --- Calendar Preferences ---
; WeekStartMonday: 0 = Sunday-first (matches reference screenshot), 1 = Monday-first
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
