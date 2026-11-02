; ============================================================================

; SPACEGLASS — CENTRAL USER VARIABLES (@Resources/Variables.inc)

; Your Universe. Your Schedule.

; ============================================================================

[Variables]

; --- Application Info ---

AppName=SpaceGlass

AppVersion=1.0.0

AppTagline=Your Universe. Your Schedule.



; --- High-DPI & 4K Display Scaling Factor ---

; Standard 1080p: 1.0 | 1440p / 125% DPI: 1.25 | 150% DPI: 1.5 | 4K / 200% DPI: 2.0

Scale=1.25



; --- Backend Connection ---

BackendHost=127.0.0.1

BackendPort=8765

BackendBaseUrl=http://127.0.0.1:8765



; --- Unified Geometry & Layout Tokens (Scalable) ---

CardWidth=(330 * #Scale#)

CardRadius=(18 * #Scale#)

RightMargin=24

TopMargin=20

WidgetGap=14



ClockHeight=(105 * #Scale#)

CalendarHeight=(224 * #Scale#)

EventsHeight=(135 * #Scale#)

TasksHeight=(135 * #Scale#)



; Backward compatibility alias

WidgetWidth=320



; --- Unified Color Tokens ---

BgGradTop=14,16,24,130

BgGradBottom=10,12,18,150

CardBorder=255,255,255,38

AccentOrange=56,139,253

AccentOrangeHex=388BFD



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

