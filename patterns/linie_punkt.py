g = """G0 F30
G91"""

punkt = """
G1 X0 Y0
G0 X15"""

linie = """
G1 X380 Y0"""



g += linie

for a in range(3):
    g += """
G0 X0 Y15"""
    for i in range(380//15 - 1):
        g += punkt
    g += """
G0 X0 Y15"""
    g += linie

g += """
G0 X0 Y5"""
g += linie

g += """
G0 X0 Y5"""
g += linie

print(g)
with open('linie_punkt.gcode', 'w') as file:
    file.write(g)
