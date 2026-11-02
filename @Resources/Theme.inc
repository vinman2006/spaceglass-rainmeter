; ============================================================================

; SPACEGLASS — CENTRAL THEME & GLASSMORPHISM DESIGN SYSTEM (@Resources/Theme.inc)

; Unified Visual Styling: Cosmic Translucent Glassmorphism

; ============================================================================

[Variables]

; --- Core Color Palette ---

; Cosmic Blue Accent (#388BFD)

AccentOrange=56,139,253

AccentOrangeHex=388BFD



; Amber (#FFB45C)

AccentAmber=255,180,92

AccentAmberHex=FFB45C



; Cosmic Violet (#A66CDB)

CosmicViolet=166,108,219

CosmicVioletHex=A66CDB



; Cosmic Blue (#388BFD)

CosmicBlue=56,139,253

CosmicBlueHex=388BFD



; Soft White & Muted Text

TextPrimary=245,243,247,255

TextPrimaryRGB=245,243,247

TextMuted=197,190,207,215

TextMutedRGB=197,190,207

TextDimmed=197,190,207,135



; Danger / Overdue Red

DangerColor=255,107,107,255



; Active Accent (Cosmic Blue)

ActiveAccent=56,139,253



; --- Glassmorphism Surface Parameters ---

; Cool translucent cosmic glass tones with subtle diagonal gradient

BgGradTop=14,16,24,130

BgGradBottom=10,12,18,150

CardBorder=255,255,255,38



; Dual Specular Highlights

GlassBorderOuter=255,255,255,38

GlassBorderInner=255,255,255,18

GlassHighlightTop=255,255,255,45



; Backward compatibility tokens

GlassBaseRGB=14,16,24

GlassAlpha=95

GlassSurface=14,16,24,140

GlassGradientTop=14,16,24,130

GlassGradientBottom=10,12,18,150

GlassAmbientWarm=56,139,253,18

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

FontSizeClock=(28 * #Scale#)

FontSizeWeatherTemp=(16 * #Scale#)

FontSizeHeader=(11.5 * #Scale#)

FontSizeBody=10

FontSizeSub=(9.5 * #Scale#)

FontSizeCalendarDayHeader=(8.5 * #Scale#)

FontSizeCalendarDate=(9.5 * #Scale#)

