import threading
import time
import cherrypy
try:
    import blinkt
    blinkt.set_clear_on_exit()
    blinkt.set_brightness(0.1)

except ImportError: 
    print("blinkt not found - local dev")

# Global variable to store the current color
current_color = {"r": 0, "g": 0, "b": 0}
current_brightness = 0.1


def set_light(r, g, b):
    """Set the LED color."""
    global current_color
    current_color = {"r": r, "g": g, "b": b}
    print(f'Setting LEDs to {r},{g},{b}')
    try:
        blinkt.set_all(r, g, b, current_brightness)
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
    def leds(self, r=0, g=0, b=0):
        """Manage LED colors."""
        if cherrypy.request.method == "GET":
            # Get the current color
            return {"status": "success", "color": current_color}
        elif cherrypy.request.method == "POST":
            try:
                r = int(r)
                g = int(g)
                b = int(b)
                set_light(r, g, b)
                return {"status": "success", "color": current_color}
            except ValueError:
                raise cherrypy.HTTPError(400, "Invalid RGB values")
        elif cherrypy.request.method == "DELETE":
            # Clear the LEDs
            clear_light()
            return {"status": "success", "message": "LEDs cleared"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def brightness(self, brightness=0.1):
        """Manage LED brightness."""
        global current_brightness
        if cherrypy.request.method == "GET":
            # Get the current brightness
            return {"status": "success", "brightness": current_brightness}
        elif cherrypy.request.method == "POST":
            try:
                brightness = float(brightness)
                if 0.0 <= brightness <= 1.0:
                    current_brightness = brightness
                    blinkt.set_brightness(current_brightness)
                    blinkt.show()
                    return {"status": "success", "brightness": current_brightness}
                else:
                    raise cherrypy.HTTPError(400, "Brightness must be between 0.0 and 1.0")
            except ValueError:
                raise cherrypy.HTTPError(400, "Invalid brightness value")
                
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
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def set_brightness(self, brightness):
        """Set the brightness level."""
        global current_brightness
        try:
            brightness = float(brightness)
            if 0.0 <= brightness <= 1.0:
                current_brightness = brightness
                blinkt.set_brightness(current_brightness)
                blinkt.show()
                return {"status": "success", "brightness": current_brightness}
            else:
                return {"status": "error", "message": "Brightness must be between 0.0 and 1.0"}
        except ValueError:
            return {"status": "error", "message": "Invalid brightness value"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_brightness(self):
        """Get the current brightness level."""
        return {"status": "success", "brightness": current_brightness}
    

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def orange(self):
        """Set the LEDs to orange for 5 minutes."""
        if cherrypy.request.method == "POST":
            def reset_after_delay():
                time.sleep(300)  # Wait for 5 minutes
                clear_light()
                print("LEDs reset after 5 minutes")

            # Set the light to orange
            set_light(255, 65, 0)  # RGB for orange
            threading.Thread(target=reset_after_delay, daemon=True).start()
            return {"status": "success", "message": "LEDs set to orange for 5 minutes"}





# Configure and start the CherryPy server
cherrypy.server.socket_host = '0.0.0.0'
cherrypy.server.socket_port = 8080
cherrypy.quickstart(LEDController())