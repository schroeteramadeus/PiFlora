import os
import subprocess
import threading
import time

class VueCompiler:

    #the interval (in sec) on which to check if the compile has finished
    COMPILE_POLL_INTERVALL : float = 2

    def __init__(self, vuePath : str) -> None:
        self.__vuePath : str = vuePath
        self.__cancellationLock : threading.Lock = threading.Lock()
        self.__cancellationToken : threading.Event = None
        self.__compileThread : threading.Thread = None
        self.__compileTask : subprocess.Popen = None
        self.__output  : list[str] = []

    @property
    def IsCompiling(self) -> bool:
        with self.__cancellationLock:
            return self.__cancellationToken != None

    def StartCompile(self) -> None:
        if not self.IsCompiling:
            self.__output = []
            self.__cancellationToken = threading.Event()
            self.__compileThread = threading.Thread(target=self.__compile, args=[self.__cancellationToken, VueCompiler.COMPILE_POLL_INTERVALL])
            self.__compileTask = subprocess.Popen("npm --prefix \"{}\" run build".format(self.__vuePath), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
            self.__compileThread.start()

    def AbortCompile(self) -> str:
        if self.IsCompiling:
            self.__cancellationToken.set()
        return self.Wait()
    
    def Wait(self) -> str:
        if self.__compileThread != None:
            self.__compileThread.join()
        return self.__output

    def __compile(self, cancellationToken : threading.Event, pollInterval : float):
        output : list[str] = [] 
        while self.__compileTask.poll() == None:
            output.extend(self.__compileTask.stdout.readlines())
            time.sleep(pollInterval)
            if cancellationToken.is_set():
                self.__compileTask.kill()

        self.__output = output

        with self.__cancellationLock:
            self.__compileTask = None
            self.__compileThread = None
            self.__cancellationToken = None