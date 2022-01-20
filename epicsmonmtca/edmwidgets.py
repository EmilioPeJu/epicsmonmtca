from string import Template
GRID = 8
TW = GRID * 16   # default text width
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
endScreenProperties
''').safe_substitute(**locals())


def static_text(x, y, s):
    w = TW
    h = TH
    return Template('''
# (Static Text)
object activeXTextClass
beginObjectProperties
major 4
minor 1
release 1
x ${x}
y ${y}
w ${w}
h ${h}
font "arial-medium-r-12.0"
fgColor index 14
bgColor index 3
value {
  "${s}"
}
endObjectProperties
''').safe_substitute(**locals())


def text_monitor(x, y, pv):
    w = TW
    h = TH
    return Template('''
# (Text Monitor)
object activeXTextDspClass:noedit
beginObjectProperties
major 4
minor 6
release 0
x ${x}
y ${y}
w ${w}
h ${h}
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
    w = TW
    h = TH
    return Template('''
# (Text Control)
object activeXTextDspClass
beginObjectProperties
major 4
minor 6
release 0
x ${x}
y ${y}
w ${w}
h ${h}
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
    w = WW
    h = WH
    return Template('''
# (Button)
object activeButtonClass
beginObjectProperties
major 4
minor 1
release 0
x ${x}
y ${y}
w ${w}
h ${h}
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
    h = BH
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
h ${h}
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


def embedded_grid(title, w_h_filenames, max_width=1600):
    """ Creates a grid of embedded screens
        Arguments:
           title: title of the screen
           w_h_filenames: a list of tuples with (width, height, name) of
                            each screen in question
           max_width: the maximum width beyond which a new row is created
                      in the grid
        Returns:
           A tuple with the edm description of a grid of embedded screens and
           the screen size
    """
    row_w = 0
    row_h = 0
    max_w = 0
    prev_max_h = BH + GRID
    max_h = prev_max_h
    x = GRID
    y = BH + GRID
    macros = ""
    parts = []

    for part_w, part_h, part_filename in w_h_filenames:
        if x + part_w >= max_width:
            x = GRID
            y += row_h + GRID
            prev_max_h += row_h + GRID
            row_w = 0
        parts.append(embed(x, y, part_w, part_h, part_filename, macros))
        row_w += part_w
        max_w = max(max_w, row_w)
        row_h = max(row_h, part_h + GRID)
        max_h = max(max_h, row_h + prev_max_h)
        x += part_w

    max_w += 2 * GRID
    parts.insert(0, banner(max_w, title))
    parts.insert(0, screen(max_w, max_h, title))
    return "".join(parts), (max_w, max_h)
