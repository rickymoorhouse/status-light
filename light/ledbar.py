import ledshim
ledshim.set_clear_on_exit()


def set_light(r, g, b):
    print('Setting Blinkt to {r},{g},{b}'.format(r=r, g=g, b=b))
    ledshim.set_clear_on_exit(False)
    ledshim.set_all(r, g, b)
    ledshim.show()

set_light(255,255,255)