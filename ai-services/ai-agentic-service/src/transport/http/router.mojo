@fieldwise_init
struct Route(Copyable):
    var method: String
    var path: String
    var name: String


struct Router(Copyable):
    var routes: List[Route]

    def __init__(out self):
        self.routes = List[Route]()

    def get(mut self, path: String, name: String):
        self.routes.append(Route("GET", path, name))

    def post(mut self, path: String, name: String):
        self.routes.append(Route("POST", path, name))

    def match(self, method: String, path: String) -> String:
        for route in self.routes:
            if route.method == method and route.path == path:
                return route.name.copy()
        return ""
