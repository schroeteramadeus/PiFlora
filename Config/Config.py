import ssl

class Config:
    def __init__(self) -> None:
        self.StandardPath = "index.html"
        self.HostAddress = "127.0.0.1"
        self.ServerPort = 8080
        self.Title = "Home"
        self.ServeableFileExtensions = (".html", ".htm", ".ico", ".png", ".svg", ".jpeg", ".jpg", ".gif", ".tiff", ".ttf", ".woff2", ".js", ".ts", ".css", ".min", ".json", ".map")
        self.RunningDirectory = "www"
        self.SaveFileFolder = "Config/Save"
        self.SSLKeyPath = "Config/SSL/cert.key"
        self.SSLCertPath = "Config/SSL/cert.csr"
        self.TSLMinimumVersion = ssl.TLSVersion.TLSv1_3