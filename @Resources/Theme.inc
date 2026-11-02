; ============================================================================
; SPACEGLASS — CENTRAL THEME & GLASSMORPHISM DESIGN SYSTEM (@Resources/Theme.inc)
; Reproduced from the SpaceGlass Windows 11 reference design specification
; ============================================================================
[Variables]
; --- Core Color Palette (RGB and RGBA values for Rainmeter Shape & String meters) ---
; Primary Orange (#FF7A18)
AccentOrange=255,122,24
AccentOrangeHex=FF7A18

; Amber (#FFB45C)
AccentAmber=255,180,92
AccentAmberHex=FFB45C

; Cosmic Violet (#A66CDB)
CosmicViolet=166,108,219
CosmicVioletHex=A66CDB

; Cosmic Blue (#58A6FF)
CosmicBlue=88,166,255
CosmicBlueHex=58A6FF

; Soft White (#F5F3F7)
TextPrimary=245,243,247,255
TextPrimaryRGB=245,243,247

; Muted Text (#C5BECF)
TextMuted=197,190,207,215
TextMutedRGB=197,190,207
TextDimmed=197,190,207,135

; Danger / Overdue Red
DangerColor=255,107,107,255

; Active Accent (can be switched to #AccentOrange#, #CosmicViolet#, or #CosmicBlue#)
ActiveAccent=255,122,24

; --- Glassmorphism Surface Parameters ---
; Base glass fill: rgba(35, 30, 42, 0.35) -> Alpha ~ 90/255 (configurable via GlassAlpha)
GlassBaseRGB=35,30,42
GlassAlpha=95
GlassSurface=#GlassBaseRGB#,#GlassAlpha#

; Subtle warm nebula reflection gradient top-left to bottom-right
GlassGradientTop=55,42,58,110
GlassGradientBottom=28,24,36,85
GlassAmbientWarm=255,122,24,22

; Specular glass border: rgba(255, 255, 255, 0.20) -> 255,255,255,51
GlassBorderOuter=255,255,255,54
GlassBorderInner=255,255,255,22
GlassHighlightTop=255,255,255,80
GlassCornerRadius=22
GlassBorderWidth=1.2

; --- Windows 11 DWM Blur Mode ---
; Options: Acrylic | Blur | Mica | None
; Paired with FrostedGlass.dll and Backend/glass_effect.py DWM API helper
BlurType=Acrylic
BlurBorder=None

; --- Typography ---
FontPrimary=Segoe UI Variable Display
FontFallback=Segoe UI
FontWeightLight=300
FontWeightRegular=400
FontWeightMedium=500
FontWeightSemibold=600
FontWeightBold=700

; Font Sizes (Matches reference proportions closely)
FontSizeClock=34
FontSizeWeatherTemp=16
FontSizeHeader=11
FontSizeBody=10
FontSizeSub=9
FontSizeCalendarDayHeader=8
FontSizeCalendarDate=9
