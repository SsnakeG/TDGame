class AutoResizableNum:
    defaultScreenX: int
    defaultScreenY: int

    guiInts = []
    blockInts = []
    enemyInts = []
    towerInts = []

    ints = [guiInts, blockInts, enemyInts, towerInts]

    currentScreenX: int
    currentScreenY: int

    def __init__(self, val, intList):
        if type(val) == type(self):
            val = val.initial()

        self.initialVal = val
        self.currentVal = val

        match intList:
            case 0:
                self.list=[]
            case 1:
                self.list = self.guiInts
            case 2:
                self.list = self.blockInts
            case 3:
                self.list = self.enemyInts
            case 4:
                self.list = self.towerInts
        self.list.append(self)

        try:
            self.updateSingle()
        except AttributeError:
            pass

    def initial(self):          # returns original value
        return self.initialVal

    def get(self):              # returns current resized value
        return self.currentVal

    def endInitial(self):              # gives initial value and stops this val from being updated anymore (used for values not used anymore)
        self.list.remove(self)
        return self.initial()

    def end(self):
        try:
            self.list.remove(self)
        except ValueError:
            pass
        return self.get()

    def updateSingle(self):
        xRatio = AutoResizableNum.currentScreenX / self.defaultScreenX
        yRatio = AutoResizableNum.currentScreenY / self.defaultScreenY

        if yRatio < xRatio:
            xRatio, yRatio = yRatio, xRatio
        ratio = xRatio
        self.currentVal = self.initialVal * ratio

    @staticmethod
    def update(screenX, screenY):
        AutoResizableNum.currentScreenX = screenX
        AutoResizableNum.currentScreenY = screenY
        for intList in AutoResizableNum.ints:
            for i in intList:
                xRatio = screenX / i.defaultScreenX
                yRatio = screenY / i.defaultScreenY

                if yRatio < xRatio:
                    xRatio, yRatio = yRatio, xRatio
                ratio = xRatio
                i.currentVal = i.initialVal * ratio

    @staticmethod
    def setupDefaults(x, y):
        AutoResizableNum.defaultScreenX = x
        AutoResizableNum.defaultScreenY = y

        AutoResizableNum.currentScreenX = x
        AutoResizableNum.currentScreenY = y

    def __add__(self, other):
        if type(other) == type(self):
            return rNum(other.get() + self.get(), self.list)
        else:
            return rNum(other + self.get(), self.list)

    def __sub__(self, other):
        if type(other) == type(self):
            return rNum(other.get() - self.get(), self.list)
        else:
            return rNum(other - self.get(), self.list)

    def __mul__(self, other):
        if type(other) == type(self):
            return rNum(other.get() * self.get(), self.list)
        else:
            return rNum(other * self.get(), self.list)

    def __le__(self, other):
        if type(other) == type(self):
            return self.get() <= other.get()
        else:
            return self.get() <= other

    def __ge__(self, other):
        if type(other) == type(self):
            return self.get() >= other.get()
        else:
            return self.get() >= other

    def __lt__(self, other):
        if type(other) == type(self):
            return self.get() < other.get()
        else:
            return self.get() < other

    def __gt__(self, other):
        if type(other) == type(self):
            return self.get() > other.get()
        else:
            return self.get() > other

    def __int__(self):
        return self.currentVal

    def __str__(self):
        return str(self.currentVal)


class AutoResizableSet:
    def __init__(self, *vals, intList):
        self.vals: list[AutoResizableNum] = [rNum(val, intList) for val in vals]
        self.update()

    def get(self):
        return [val.get() for val in self.vals]

    def getIdx(self, idx):
        return self.vals[idx].get()

    def initial(self):
        return [val.initial() for val in self.vals]

    def initialIdx(self, idx):
        return self.vals[idx].initial()

    def end(self):
        return [val.end() for val in self.vals]

    def endIdx(self, idx):
        return self.vals[idx].end()

    def endInitial(self):
        return [val.endInitial() for val in self.vals]

    def endIdxInitial(self, idx):
        return self.vals[idx].endInitial()

    def update(self):
        for val in self.vals:
            val.updateSingle()


def rNums(*v, intList=None) -> AutoResizableSet:
    return AutoResizableSet(*v, intList=intList)


def rNum(v, intList) -> AutoResizableNum:
    return AutoResizableNum(v, intList)
