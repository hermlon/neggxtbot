g = """G0 F30
G91"""

punkt = """
G1
G0 X15"""

for i in range(404//15):
    g += punkt

for a in range(9):
    g += """
    G0 X0 Y10"""
    for i in range(404//15):
        g += punkt


print(g)
with open('quadratwelle_1.gcode', 'w') as file:
    file.write(g)
