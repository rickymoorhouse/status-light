
import cherrypy
try:
    import blinkt
    blinkt.set_clear_on_exit()
    blinkt.set_brightness(0.1)

except ImportError: 
    print("blinkt not found - local dev")

# Global variable to store the current color
current_color = {"r": 0, "g": 0, "b": 0}


def set_light(r, g, b):
    """Set the LED color."""
    global current_color
    current_color = {"r": r, "g": g, "b": b}
    print(f'Setting LEDs to {r},{g},{b}')
    try:
        for x in range(blinkt.NUM_PIXELS):
            blinkt.set_pixel(x, r, g, b)
        blinkt.show()
    except ImportError:
        print("blinkt not found - local dev")

def clear_light():
    """Clear the LEDs."""
    global current_color
    current_color = {"r": 0, "g": 0, "b": 0}
    print("Clearing LEDs")
    try:
        blinkt.clear()
        blinkt.show()
    except:
        print("blinkt not found - local dev")



class LEDController(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        """Default endpoint."""
        return {"message": "Welcome to the LED Controller API"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def set_rgb(self, r, g, b):
        """Set the LED color using RGB values."""
        set_light(int(r), int(g), int(b))
        return {"status": "success", "color": current_color}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def set_hex(self, hex_color):
        """Set the LED color using a HEX value."""
        if len(hex_color) != 6:
            return {"status": "error", "message": "Invalid HEX color"}
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            set_light(r, g, b)
            return {"status": "success", "color": current_color}
        except ValueError:
            return {"status": "error", "message": "Invalid HEX color"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def clear(self):
        """Clear the LEDs."""
        clear_light()
        return {"status": "success", "message": "LEDs cleared"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_color(self):
        """Get the current LED color."""
        return {"status": "success", "color": current_color}


# Configure and start the CherryPy server
cherrypy.server.socket_host = '0.0.0.0'
cherrypy.server.socket_port = 8080
cherrypy.quickstart(LEDController())