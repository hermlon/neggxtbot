g = """G0 F30
G91"""

punkt = """
G1
G0 X15"""

for a in range(6):
    for i in range(404//15):
        g += punkt



print(g)
