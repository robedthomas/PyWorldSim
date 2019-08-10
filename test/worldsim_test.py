from PyWorldSim.src.worldsim import GameManager
m = GameManager(width=3, height=2)
for i in range(30):
    m.exec_turn()
m.save("worldsimtest.txt")
