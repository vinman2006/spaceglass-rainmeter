; ============================================================================
; SPACEGLASS — CENTRAL THEME & GLASSMORPHISM DESIGN SYSTEM (@Resources/Theme.inc)
; Unified Visual Styling: Warm Charcoal / Espresso Glassmorphism
; ============================================================================
[Variables]
; --- Core Color Palette ---
; Primary Orange (#F07B1A)
AccentOrange=240,123,26
AccentOrangeHex=F07B1A

; Amber (#FFB45C)
AccentAmber=255,180,92
AccentAmberHex=FFB45C

; Cosmic Violet (#A66CDB)
CosmicViolet=166,108,219
CosmicVioletHex=A66CDB

; Cosmic Blue (#58A6FF)
CosmicBlue=88,166,255
CosmicBlueHex=58A6FF

; Soft White & Muted Text
TextPrimary=245,243,247,255
TextPrimaryRGB=245,243,247
TextMuted=197,190,207,215
TextMutedRGB=197,190,207
TextDimmed=197,190,207,135

; Danger / Overdue Red
DangerColor=255,107,107,255

; Active Accent
ActiveAccent=255,122,24

; --- Glassmorphism Surface Parameters ---
; Deep warm charcoal / espresso tones with subtle diagonal gradient
BgGradTop=32,24,20,215
BgGradBottom=22,16,14,230
CardBorder=255,255,255,28

; Dual Specular Highlights
GlassBorderOuter=255,255,255,28
GlassBorderInner=255,255,255,16
GlassHighlightTop=255,255,255,35

; Backward compatibility tokens
GlassBaseRGB=28,20,18
GlassAlpha=95
GlassSurface=28,20,18,220
GlassGradientTop=32,24,20,215
GlassGradientBottom=22,16,14,230
GlassAmbientWarm=240,123,26,18
GlassCornerRadius=22
GlassBorderWidth=(1 * #Scale#)

; --- Typography ---
FontPrimary=Segoe UI Variable Display
FontFallback=Segoe UI
FontWeightLight=300
FontWeightRegular=400
FontWeightMedium=500
FontWeightSemibold=600
FontWeightBold=700

; Font Sizes (Scalable with High-DPI Scale factor)
FontSizeClock=(34 * #Scale#)
FontSizeWeatherTemp=(16 * #Scale#)
FontSizeHeader=(11.5 * #Scale#)
FontSizeBody=10
FontSizeSub=(9.5 * #Scale#)
FontSizeCalendarDayHeader=(8.5 * #Scale#)
FontSizeCalendarDate=(9.5 * #Scale#)
