from pyworldsim.gui import Application
from time import sleep
a = Application()
a.launch()
a.display_game()
for i in range(15):
    a.pass_turn()
    a.display_game()
    sleep(3)
a.close()
