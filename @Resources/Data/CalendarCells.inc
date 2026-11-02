; ============================================================================
; SPACEGLASS — 42 CALENDAR GRID CELLS & EVENT DOTS (@Resources/Data/CalendarCells.inc)
; Included by Calendar/Calendar.ini and dynamically updated by calendar.lua
; ============================================================================

[MeterCell1]
Meter=String
X=35
Y=65
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=700
StringAlign=Center
AntiAlias=1
Text="1"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(1)"]

[MeterDot1]
Meter=Shape
Shape=Ellipse 35,81,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell2]
Meter=String
X=76
Y=65
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="2"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(2)"]

[MeterDot2]
Meter=Shape
Shape=Ellipse 76,81,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell3]
Meter=String
X=117
Y=65
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="3"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(3)"]

[MeterDot3]
Meter=Shape
Shape=Ellipse 117,81,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell4]
Meter=String
X=158
Y=65
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="4"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(4)"]

[MeterDot4]
Meter=Shape
Shape=Ellipse 158,81,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell5]
Meter=String
X=199
Y=65
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="5"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(5)"]

[MeterDot5]
Meter=Shape
Shape=Ellipse 199,81,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell6]
Meter=String
X=240
Y=65
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="6"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(6)"]

[MeterDot6]
Meter=Shape
Shape=Ellipse 240,81,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell7]
Meter=String
X=281
Y=65
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="7"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(7)"]

[MeterDot7]
Meter=Shape
Shape=Ellipse 281,81,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell8]
Meter=String
X=35
Y=88
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="8"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(8)"]

[MeterDot8]
Meter=Shape
Shape=Ellipse 35,104,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell9]
Meter=String
X=76
Y=88
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="9"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(9)"]

[MeterDot9]
Meter=Shape
Shape=Ellipse 76,104,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell10]
Meter=String
X=117
Y=88
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="10"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(10)"]

[MeterDot10]
Meter=Shape
Shape=Ellipse 117,104,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell11]
Meter=String
X=158
Y=88
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="11"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(11)"]

[MeterDot11]
Meter=Shape
Shape=Ellipse 158,104,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell12]
Meter=String
X=199
Y=88
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="12"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(12)"]

[MeterDot12]
Meter=Shape
Shape=Ellipse 199,104,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell13]
Meter=String
X=240
Y=88
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="13"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(13)"]

[MeterDot13]
Meter=Shape
Shape=Ellipse 240,104,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell14]
Meter=String
X=281
Y=88
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="14"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(14)"]

[MeterDot14]
Meter=Shape
Shape=Ellipse 281,104,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell15]
Meter=String
X=35
Y=111
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="15"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(15)"]

[MeterDot15]
Meter=Shape
Shape=Ellipse 35,127,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell16]
Meter=String
X=76
Y=111
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="16"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(16)"]

[MeterDot16]
Meter=Shape
Shape=Ellipse 76,127,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell17]
Meter=String
X=117
Y=111
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="17"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(17)"]

[MeterDot17]
Meter=Shape
Shape=Ellipse 117,127,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=0
DynamicVariables=1

[MeterCell18]
Meter=String
X=158
Y=111
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="18"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(18)"]

[MeterDot18]
Meter=Shape
Shape=Ellipse 158,127,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell19]
Meter=String
X=199
Y=111
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="19"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(19)"]

[MeterDot19]
Meter=Shape
Shape=Ellipse 199,127,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell20]
Meter=String
X=240
Y=111
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="20"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(20)"]

[MeterDot20]
Meter=Shape
Shape=Ellipse 240,127,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell21]
Meter=String
X=281
Y=111
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="21"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(21)"]

[MeterDot21]
Meter=Shape
Shape=Ellipse 281,127,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell22]
Meter=String
X=35
Y=134
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="22"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(22)"]

[MeterDot22]
Meter=Shape
Shape=Ellipse 35,150,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell23]
Meter=String
X=76
Y=134
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="23"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(23)"]

[MeterDot23]
Meter=Shape
Shape=Ellipse 76,150,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell24]
Meter=String
X=117
Y=134
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="24"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(24)"]

[MeterDot24]
Meter=Shape
Shape=Ellipse 117,150,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=0
DynamicVariables=1

[MeterCell25]
Meter=String
X=158
Y=134
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="25"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(25)"]

[MeterDot25]
Meter=Shape
Shape=Ellipse 158,150,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell26]
Meter=String
X=199
Y=134
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="26"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(26)"]

[MeterDot26]
Meter=Shape
Shape=Ellipse 199,150,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell27]
Meter=String
X=240
Y=134
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="27"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(27)"]

[MeterDot27]
Meter=Shape
Shape=Ellipse 240,150,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell28]
Meter=String
X=281
Y=134
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="28"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(28)"]

[MeterDot28]
Meter=Shape
Shape=Ellipse 281,150,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell29]
Meter=String
X=35
Y=157
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="29"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(29)"]

[MeterDot29]
Meter=Shape
Shape=Ellipse 35,173,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell30]
Meter=String
X=76
Y=157
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text="30"
Hidden=0
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(30)"]

[MeterDot30]
Meter=Shape
Shape=Ellipse 76,173,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell31]
Meter=String
X=117
Y=157
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text=""
Hidden=1
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(31)"]

[MeterDot31]
Meter=Shape
Shape=Ellipse 117,173,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell32]
Meter=String
X=158
Y=157
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text=""
Hidden=1
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(32)"]

[MeterDot32]
Meter=Shape
Shape=Ellipse 158,173,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell33]
Meter=String
X=199
Y=157
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text=""
Hidden=1
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(33)"]

[MeterDot33]
Meter=Shape
Shape=Ellipse 199,173,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell34]
Meter=String
X=240
Y=157
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text=""
Hidden=1
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(34)"]

[MeterDot34]
Meter=Shape
Shape=Ellipse 240,173,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell35]
Meter=String
X=281
Y=157
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text=""
Hidden=1
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(35)"]

[MeterDot35]
Meter=Shape
Shape=Ellipse 281,173,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell36]
Meter=String
X=35
Y=178
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text=""
Hidden=1
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(36)"]

[MeterDot36]
Meter=Shape
Shape=Ellipse 35,194,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell37]
Meter=String
X=76
Y=178
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text=""
Hidden=1
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(37)"]

[MeterDot37]
Meter=Shape
Shape=Ellipse 76,194,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell38]
Meter=String
X=117
Y=178
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text=""
Hidden=1
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(38)"]

[MeterDot38]
Meter=Shape
Shape=Ellipse 117,194,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell39]
Meter=String
X=158
Y=178
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text=""
Hidden=1
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(39)"]

[MeterDot39]
Meter=Shape
Shape=Ellipse 158,194,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell40]
Meter=String
X=199
Y=178
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text=""
Hidden=1
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(40)"]

[MeterDot40]
Meter=Shape
Shape=Ellipse 199,194,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell41]
Meter=String
X=240
Y=178
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text=""
Hidden=1
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(41)"]

[MeterDot41]
Meter=Shape
Shape=Ellipse 240,194,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1

[MeterCell42]
Meter=String
X=281
Y=178
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
Text=""
Hidden=1
DynamicVariables=1
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(42)"]

[MeterDot42]
Meter=Shape
Shape=Ellipse 281,194,2.2,2.2 | Fill Color #CosmicViolet#,255 | StrokeWidth 0
Hidden=1
DynamicVariables=1
