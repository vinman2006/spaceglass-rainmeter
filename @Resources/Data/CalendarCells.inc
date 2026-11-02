; ============================================================================
; SPACEGLASS — 42 CALENDAR GRID CELLS & EVENT DOTS (@Resources/Data/CalendarCells.inc)
; High-DPI Scalable Architecture
; ============================================================================

[MeterCell1]
Meter=String
X=(33 * #Scale#)
Y=(68 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="1"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(1)"]

[MeterDot1]
Meter=Shape
Shape=Ellipse (33 * #Scale#),(83 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell2]
Meter=String
X=(77 * #Scale#)
Y=(68 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="2"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(2)"]

[MeterDot2]
Meter=Shape
Shape=Ellipse (77 * #Scale#),(83 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell3]
Meter=String
X=(121 * #Scale#)
Y=(68 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="3"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(3)"]

[MeterDot3]
Meter=Shape
Shape=Ellipse (121 * #Scale#),(83 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell4]
Meter=String
X=(165 * #Scale#)
Y=(68 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="4"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(4)"]

[MeterDot4]
Meter=Shape
Shape=Ellipse (165 * #Scale#),(83 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell5]
Meter=String
X=(209 * #Scale#)
Y=(68 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="5"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(5)"]

[MeterDot5]
Meter=Shape
Shape=Ellipse (209 * #Scale#),(83 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell6]
Meter=String
X=(253 * #Scale#)
Y=(68 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="6"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(6)"]

[MeterDot6]
Meter=Shape
Shape=Ellipse (253 * #Scale#),(83 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell7]
Meter=String
X=(297 * #Scale#)
Y=(68 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="7"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(7)"]

[MeterDot7]
Meter=Shape
Shape=Ellipse (297 * #Scale#),(83 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell8]
Meter=String
X=(33 * #Scale#)
Y=(93 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="8"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(8)"]

[MeterDot8]
Meter=Shape
Shape=Ellipse (33 * #Scale#),(108 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell9]
Meter=String
X=(77 * #Scale#)
Y=(93 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="9"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(9)"]

[MeterDot9]
Meter=Shape
Shape=Ellipse (77 * #Scale#),(108 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell10]
Meter=String
X=(121 * #Scale#)
Y=(93 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="10"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(10)"]

[MeterDot10]
Meter=Shape
Shape=Ellipse (121 * #Scale#),(108 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell11]
Meter=String
X=(165 * #Scale#)
Y=(93 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="11"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(11)"]

[MeterDot11]
Meter=Shape
Shape=Ellipse (165 * #Scale#),(108 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell12]
Meter=String
X=(209 * #Scale#)
Y=(93 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="12"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(12)"]

[MeterDot12]
Meter=Shape
Shape=Ellipse (209 * #Scale#),(108 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell13]
Meter=String
X=(253 * #Scale#)
Y=(93 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="13"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(13)"]

[MeterDot13]
Meter=Shape
Shape=Ellipse (253 * #Scale#),(108 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell14]
Meter=String
X=(297 * #Scale#)
Y=(93 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="14"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(14)"]

[MeterDot14]
Meter=Shape
Shape=Ellipse (297 * #Scale#),(108 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell15]
Meter=String
X=(33 * #Scale#)
Y=(118 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="15"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(15)"]

[MeterDot15]
Meter=Shape
Shape=Ellipse (33 * #Scale#),(133 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell16]
Meter=String
X=(77 * #Scale#)
Y=(118 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="16"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(16)"]

[MeterDot16]
Meter=Shape
Shape=Ellipse (77 * #Scale#),(133 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell17]
Meter=String
X=(121 * #Scale#)
Y=(118 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="17"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(17)"]

[MeterDot17]
Meter=Shape
Shape=Ellipse (121 * #Scale#),(133 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell18]
Meter=String
X=(165 * #Scale#)
Y=(118 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="18"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(18)"]

[MeterDot18]
Meter=Shape
Shape=Ellipse (165 * #Scale#),(133 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell19]
Meter=String
X=(209 * #Scale#)
Y=(118 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="19"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(19)"]

[MeterDot19]
Meter=Shape
Shape=Ellipse (209 * #Scale#),(133 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell20]
Meter=String
X=(253 * #Scale#)
Y=(118 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="20"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(20)"]

[MeterDot20]
Meter=Shape
Shape=Ellipse (253 * #Scale#),(133 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell21]
Meter=String
X=(297 * #Scale#)
Y=(118 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="21"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(21)"]

[MeterDot21]
Meter=Shape
Shape=Ellipse (297 * #Scale#),(133 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell22]
Meter=String
X=(33 * #Scale#)
Y=(143 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="22"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(22)"]

[MeterDot22]
Meter=Shape
Shape=Ellipse (33 * #Scale#),(158 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell23]
Meter=String
X=(77 * #Scale#)
Y=(143 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="23"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(23)"]

[MeterDot23]
Meter=Shape
Shape=Ellipse (77 * #Scale#),(158 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell24]
Meter=String
X=(121 * #Scale#)
Y=(143 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="24"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(24)"]

[MeterDot24]
Meter=Shape
Shape=Ellipse (121 * #Scale#),(158 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell25]
Meter=String
X=(165 * #Scale#)
Y=(143 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="25"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(25)"]

[MeterDot25]
Meter=Shape
Shape=Ellipse (165 * #Scale#),(158 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell26]
Meter=String
X=(209 * #Scale#)
Y=(143 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="26"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(26)"]

[MeterDot26]
Meter=Shape
Shape=Ellipse (209 * #Scale#),(158 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell27]
Meter=String
X=(253 * #Scale#)
Y=(143 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="27"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(27)"]

[MeterDot27]
Meter=Shape
Shape=Ellipse (253 * #Scale#),(158 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell28]
Meter=String
X=(297 * #Scale#)
Y=(143 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="28"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(28)"]

[MeterDot28]
Meter=Shape
Shape=Ellipse (297 * #Scale#),(158 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell29]
Meter=String
X=(33 * #Scale#)
Y=(168 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="29"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(29)"]

[MeterDot29]
Meter=Shape
Shape=Ellipse (33 * #Scale#),(183 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell30]
Meter=String
X=(77 * #Scale#)
Y=(168 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="30"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(30)"]

[MeterDot30]
Meter=Shape
Shape=Ellipse (77 * #Scale#),(183 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell31]
Meter=String
X=(121 * #Scale#)
Y=(168 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="31"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(31)"]

[MeterDot31]
Meter=Shape
Shape=Ellipse (121 * #Scale#),(183 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell32]
Meter=String
X=(165 * #Scale#)
Y=(168 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="32"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(32)"]

[MeterDot32]
Meter=Shape
Shape=Ellipse (165 * #Scale#),(183 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell33]
Meter=String
X=(209 * #Scale#)
Y=(168 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="33"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(33)"]

[MeterDot33]
Meter=Shape
Shape=Ellipse (209 * #Scale#),(183 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell34]
Meter=String
X=(253 * #Scale#)
Y=(168 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="34"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(34)"]

[MeterDot34]
Meter=Shape
Shape=Ellipse (253 * #Scale#),(183 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell35]
Meter=String
X=(297 * #Scale#)
Y=(168 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="35"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(35)"]

[MeterDot35]
Meter=Shape
Shape=Ellipse (297 * #Scale#),(183 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell36]
Meter=String
X=(33 * #Scale#)
Y=(193 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="36"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(36)"]

[MeterDot36]
Meter=Shape
Shape=Ellipse (33 * #Scale#),(208 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell37]
Meter=String
X=(77 * #Scale#)
Y=(193 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="37"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(37)"]

[MeterDot37]
Meter=Shape
Shape=Ellipse (77 * #Scale#),(208 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell38]
Meter=String
X=(121 * #Scale#)
Y=(193 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="38"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(38)"]

[MeterDot38]
Meter=Shape
Shape=Ellipse (121 * #Scale#),(208 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell39]
Meter=String
X=(165 * #Scale#)
Y=(193 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="39"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(39)"]

[MeterDot39]
Meter=Shape
Shape=Ellipse (165 * #Scale#),(208 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell40]
Meter=String
X=(209 * #Scale#)
Y=(193 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="40"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(40)"]

[MeterDot40]
Meter=Shape
Shape=Ellipse (209 * #Scale#),(208 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell41]
Meter=String
X=(253 * #Scale#)
Y=(193 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="41"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(41)"]

[MeterDot41]
Meter=Shape
Shape=Ellipse (253 * #Scale#),(208 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1

[MeterCell42]
Meter=String
X=(297 * #Scale#)
Y=(193 * #Scale#)
FontFace=#FontPrimary#
FontSize=#FontSizeCalendarDate#
FontColor=#TextPrimary#
FontWeight=400
StringAlign=Center
AntiAlias=1
DynamicVariables=1
Text="42"
Hidden=0
LeftMouseUpAction=[!CommandMeasure MeasureCalendarScript "SelectDay(42)"]

[MeterDot42]
Meter=Shape
Shape=Ellipse (297 * #Scale#),(208 * #Scale#),(2 * #Scale#),(2 * #Scale#) | Fill Color #CosmicViolet#,255 | StrokeWidth 0
AntiAlias=1
DynamicVariables=1
Hidden=1
