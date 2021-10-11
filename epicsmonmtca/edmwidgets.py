from string import Template
GRID = 8
TW = GRID * 15   # default text width
TH = GRID * 2    # default text heigth
WH = GRID * 2    # default widget heigth
WW = GRID * 8    # default widget width
BH = GRID * 4    # default banner height


def screen(w, h, title):
    return Template('''4 0 1
beginScreenProperties
major 4
minor 0
release 1
x 20
y 20
w ${w}
h ${h}
font "arial-medium-r-12.0"
ctlFont "arial-medium-r-12.0"
btnFont "arial-medium-r-12.0"
fgColor index 14
bgColor index 3
textColor index 14
ctlFgColor1 index 14
ctlFgColor2 index 0
ctlBgColor1 index 0
ctlBgColor2 index 14
topShadowColor index 1
botShadowColor index 11
title "${title}"
showGrid
snapToGrid
gridSize 8
disableScroll
endScreenProperties
''').safe_substitute(**locals())


def static_text(x, y, s):
    return Template('''
# (Static Text)
object activeXTextClass
beginObjectProperties
major 4
minor 1
release 1
x ${x}
y ${y}
w 120
h 16
font "arial-medium-r-12.0"
fgColor index 14
bgColor index 3
value {
  "${s}"
}
endObjectProperties
''').safe_substitute(**locals())


def text_monitor(x, y, pv):
    return Template('''
# (Text Monitor)
object activeXTextDspClass:noedit
beginObjectProperties
major 4
minor 6
release 0
x ${x}
y ${y}
w 120
h 16
controlPv "${pv}"
format "float"
font "courier-medium-r-12.0"
fontAlign "right"
fgColor index 16
fgAlarm
bgColor index 10
limitsFromDb
nullColor index 0
fastUpdate
useHexPrefix
showUnits
newPos
objType "monitors"
endObjectProperties
''').safe_substitute(**locals())


def text_control(x, y, pv):
    return Template('''
# (Text Control)
object activeXTextDspClass
beginObjectProperties
major 4
minor 6
release 0
x ${x}
y ${y}
w 120
h 16
controlPv "${pv}"
font "courier-medium-r-12.0"
fontAlign "right"
fgColor index 25
bgColor index 5
editable
limitsFromDb
nullColor index 0
useHexPrefix
newPos
objType "controls"
endObjectProperties
''').safe_substitute(**locals())


def button_toggle(x, y, spv, rpv):
    return Template('''
# (Button)
object activeButtonClass
beginObjectProperties
major 4
minor 1
release 0
x ${x}
y ${y}
w 64
h 32
fgColor index 14
onColor index 4
offColor index 4
inconsistentColor index 0
topShadowColor index 1
botShadowColor index 11
controlPv "${spv}"
indicatorPv "${rpv}"
3d
font "arial-medium-r-12.0"
objType "controls"
endObjectProperties
''').safe_substitute(**locals())


def button_push(x, y, spv, rpv):
    return Template('''
# (Button)
object activeButtonClass
beginObjectProperties
major 4
minor 1
release 0
x ${x}
y ${y}
w 32
h 32
fgColor index 14
onColor index 4
offColor index 4
inconsistentColor index 0
topShadowColor index 1
botShadowColor index 11
controlPv "${spv}"
indicatorPv "${rpv}"
buttonType "push"
3d
font "arial-medium-r-12.0"
objType "controls"
endObjectProperties
''').safe_substitute(**locals())


def menu(x, y, spv, rpv):
    return Template('''
# (Menu Button)
object activeMenuButtonClass
beginObjectProperties
major 4
minor 0
release 0
x ${x}
y ${y}
w 132
h 32
fgColor index 14
bgColor index 4
inconsistentColor index 0
topShadowColor index 1
botShadowColor index 11
controlPv "${spv}"
indicatorPv "${rpv}"
font "arial-medium-r-12.0"
endObjectProperties
''').safe_substitute(**locals())


def byte(x, y, pv, c1=15, c2=19):  # default colors: green on and green off
    return Template('''
# (Byte)
object ByteClass
beginObjectProperties
major 4
minor 0
release 0
x ${x}
y ${y}
w 16
h 16
controlPv "${pv}"
lineColor index 14
onColor index ${c1}
offColor index ${c2}
numBits 1
endObjectProperties
''').safe_substitute(**locals())


def banner(w, title="$(device)"):
    return Template('''
# (Static Text)
object activeXTextClass
beginObjectProperties
major 4
minor 1
release 1
x 0
y 0
w ${w}
h 32
font "arial-medium-r-18.0"
fontAlign "center"
fgColor index 14
bgColor index 68
value {
  "${title}"
}
border
endObjectProperties
''').safe_substitute(**locals())


def waveform(x, y, pv):
    return Template('''
# (X-Y Graph)
object xyGraphClass
beginObjectProperties
major 4
minor 8
release 0
# Geometry
x ${x}
y ${y}
w 328
h 168
# Appearance
border
fgColor index 14
bgColor index 0
gridColor index 14
font "arial-medium-r-12.0"
# Operating Modes
nPts 2
# X axis properties
showXAxis
xAxisSrc "fromUser"
xMin 0
xMax 200
# Y axis properties
showYAxis
yAxisSrc "AutoScale"
yMax 1
# Y2 axis properties
y2AxisSrc "AutoScale"
y2Max 1
# Trace Properties
numTraces 1
yPv {
  0 "{pv}"
}
plotColor {
  0 index 14
}
endObjectProperties
''').safe_substitute(**locals())


def embed(x, y, w, h, filename, macros):
    return Template('''
# (Embedded Window)
object activePipClass
beginObjectProperties
major 4
minor 1
release 0
x ${x}
y ${y}
w ${w}
h ${h}
fgColor index 14
bgColor index 10
topShadowColor index 1
botShadowColor index 11
displaySource "menu"
filePv "LOC\\\\$(!W)tabi=e:0,TAB1"
sizeOfs 5
numDsps 1
displayFileName {
  0 "${filename}"
}
symbols {
  0 "${macros}"
}
noScroll
endObjectProperties
''').safe_substitute(**locals())


def related_display(x, y, w, h, label, filename, macros):
    return Template('''
# (Related Display)
object relatedDisplayClass
beginObjectProperties
major 4
minor 4
release 0
x ${x}
y ${y}
w ${w}
h ${h}
bgColor index 3
botShadowColor index 11
buttonLabel "${label}"
displayFileName {
  0 "${filename}"
}
fgColor index 43
font "arial-bold-r-14.0"
numDsps 1
numPvs 4
symbols {
  0 "${macros}"
}
topShadowColor index 1
endObjectProperties
''').safe_substitute(**locals())
