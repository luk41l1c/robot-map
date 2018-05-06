import http.server, os, json

class robot:
    def __init__(self):
        self.x = None
        self.y = None
        self.f = None
        self.placed = False
        self.movementX = []
        self.movementY = []
    def place(self,x,y,f):
        if 0 <= x <5 and 0 <= y < 5 and f in ['NORTH','SOUTH','EAST','WEST']:
            self.x = x
            self.y = y
            self.f = f
            self.placed = True
    def move(self):
        if not self.placed: return
        if self.f == "SOUTH" and self.y > 0:
            self.y -= 1
            self.movementX.append(self.x)
            self.movementY.append(self.y)
        elif self.f == "NORTH" and self.y < 4:
            self.y += 1
            self.movementX.append(self.x)
            self.movementY.append(self.y)
        elif self.f == "EAST" and self.x < 4:
            self.x += 1
            self.movementX.append(self.x)
            self.movementY.append(self.y)
        elif self.f == "WEST" and self.x > 0:
            self.x -= 1
            self.movementX.append(self.x)
            self.movementY.append(self.y)
    def left(self):
        if not self.placed: return
        if self.f == "SOUTH": self.f = "EAST"
        elif self.f == "EAST": self.f = "NORTH"
        elif self.f == "NORTH": self.f = "WEST"
        elif self.f == "WEST": self.f = "SOUTH"
    def right(self):
        if not self.placed: return
        if self.f == "SOUTH": self.f = "WEST"
        elif self.f == "WEST": self.f = "NORTH"
        elif self.f == "NORTH": self.f = "EAST"
        elif self.f == "EAST": self.f = "SOUTH"
    def report(self):
        koordinate = [self.x, self.y, self.f]
        return koordinate
    def movementXs(self):
        return self.movementX
    def movementYs(self):
        return self.movementY

BaseHandler = http.server.BaseHTTPRequestHandler
class Handler(BaseHandler):
    def _set_headers(self, type):
        self.send_response(200)
        self.send_header('Content-type', type)
        self.end_headers()
    def do_GET(self):
        filename = self.path.split("/")[-1]
        if filename == "" : filename = "index.html"
        if os.access(filename, os.R_OK) and not os.path.isdir(filename):
            ext = filename.split(".")[-1]                       # Klijent zahteva fajl
            mode = "r"
            if ext in ["html","htm"]: content_type = "text/html"
            elif ext in ["txt","js","py","php"]: content_type = "text/plain"
            elif ext in ["css"]: content_type = "text/css"
            elif ext in ["ico","jpg","jpeg","png","gif"]:
                content_type = "image/x-icon"
                mode = "rb"
            content = open(filename, mode).read()
            if mode == "r": content = str.encode(content)
            self._set_headers(content_type)
            self.wfile.write(content)
        else:                                 # Ajax zahtev
            odgovor = {"metod":"GET", "path": self.path, "sadrzaj": ""}
            self._set_headers("text/json")
            self.wfile.write(str.encode(str(odgovor)))
    def do_POST(self):
        putanja = self.path
        metod = self.command
        duzina_sadrzaja = int(self.headers['Content-Length'])
        komanda = self.rfile.read(duzina_sadrzaja).decode("utf-8")
        #print(komanda)
        d = json.loads(komanda)
        #print(d)
        r = robot()
        komanda = d['zadata_komanda'].split()
        i = 0
        while 1:
            if i >= len(komanda): break
            #print(komanda[i])
            if komanda[i] == 'PLACE':
                x,y,f = komanda[i+1].split(',')
                r.place(int(x),int(y),f)
                i += 2
            elif komanda[i] == "LEFT":
                r.left()
                i+= 1
            elif komanda[i] == "RIGHT":
                r.right()
                i += 1
            elif komanda[i] == "MOVE":
                r.move()
                i += 1
            elif komanda[i] == "REPORT":
                odgovor = {"metod": metod, "putanja": putanja, "sadrzaj": r.report(), "movementX": r.movementXs(), "movementY": r.movementYs()}
                self._set_headers("text/json")
                self.wfile.write(str.encode(str(odgovor)))
                i += 1
            else:
                odgovor = {"metod": metod, "putanja": putanja, "sadrzaj": 0}
                self._set_headers("text/json")
                self.wfile.write(str.encode(str(odgovor)))
                break
        
try:
    httpd = http.server.HTTPServer(('',8888), Handler)
    print("Server startovan...port: 8888")
    httpd.serve_forever()
except:
    print("Server stopiran")

