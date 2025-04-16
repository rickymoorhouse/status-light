
import cherrypy
try:
    import ledshim
    ledshim.set_clear_on_exit()
except: 
    print("ledshim not found - local dev")


def set_light(r, g, b):
    print('Setting Blinkt to {r},{g},{b}'.format(r=r, g=g, b=b))
    try:
        ledshim.set_clear_on_exit(False)
        ledshim.set_all(r, g, b)
        ledshim.show()
    except:
        print("ledshim not found - local dev")



set_light(255,255,255)

class HelloWorld(object):
    @cherrypy.expose
    def index(self, r=0, g=0, b=0):
        set_light(int(r), int(g), int(b))
        return "Hello World! " + str(r) + ","+str(g)+","+str(b)+""

cherrypy.quickstart(HelloWorld())