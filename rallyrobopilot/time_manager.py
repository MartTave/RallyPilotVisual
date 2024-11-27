def log(*args):
    print("[Time]", *args)


class Time:

    fps: int
    dt: float
    realTime: bool
    currStep: int = 0
    subscribers = {}

    def __init__(self, realTime=False, dt: float = None, fps: int = None):
        if dt is not None and dt > 0.1:
            log("Warning: dt is greater than 0.1, you will have some precision loss...")
        if realTime:
            if fps is not None:
                self.dt = 1.0 / fps
                self.fps = fps
            elif dt is not None:
                assert 1.0 / dt == int(1.0 / dt)
                self.fps = 1.0 / dt
                self.dt = dt
            else:
                self.dt = 0.1
                self.fps = 10
        else:
            if dt is not None:
                self.dt = dt
            else:
                self.dt = 0.1
            if fps is not None:
                self.fps = fps
            else:
                self.fps = -1
        log(f"Simulation will be running with a dt of {self.dt} and at {self.fps} fps")

    def executeNow(self, frequency) -> bool:
        assert 1.0 / frequency % self.dt == 0
        return self.currStep % int(1.0 / frequency / self.dt) == 0

    def cbAtHerz(self, frequency, cb):
        assert 1.0 / frequency % self.dt == 0
        nbStep = int(1.0 / frequency / self.dt)
        if nbStep not in self.subscribers:
            self.subscribers[nbStep] = []
        self.subscribers[nbStep].append(cb)

    def step(self):
        self.currStep += 1
        for freq in self.subscribers.keys():
            if self.currStep % freq == 0:
                for cb in self.subscribers[freq]:
                    cb()


if __name__ == "__main__":
    a = Time(realTime=True, fps=20)
    assert a.dt == 0.05
    assert a.fps == 20
    a = Time(realTime=True, dt=0.05)
    count = 0

    def increment():
        global count
        count += 1

    a.cbAtHerz(10, increment)
    a.step()
    a.step()
    a.step()
    a.step()
    assert count == 2
    a.step()
    assert count == 2
    a.step()
    assert count == 3
    try:  # Test invalid frequency
        a.cbAtHerz(3, increment)
        raise Exception("Should have raised exception")
    except AssertionError:
        pass
    try:  # Test invalid frequency
        a.cbAtHerz(40, increment)
        raise Exception("Should have raised exception")
    except AssertionError:
        pass
    assert a.dt == 0.05
    assert a.fps == 20
