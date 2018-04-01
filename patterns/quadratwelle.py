g = """G0 F30
G91"""

doppel_quadrat = """
G1 X0 Y20
G1 X20 Y0
G1 X0 Y-20
G1 X20 Y0"""

for j in range(100//30):
    for i in range(380//40):
        g += doppel_quadrat
    g += """
G1 X20 Y0"""
    g += """
G0 X0 Y30"""

print(g)
with open('quadratwelle.gcode', 'w') as file:
    file.write(g)
