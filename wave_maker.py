import tkinter as tk
import tkinter.messagebox

wave_part_number = 0


def new_wave_part():
    global wave_part_number
    wave_part_number += 1
    WavePartMaker(root, wave_part_number)
    new_wave_part_btn.place(x=100, y=wave_part_number * 35 + 150)


def combineWaveParts():
    wavePart = None
    timelineInterval = 0.1
    timeSinceSpawn = 0
    timeline = []
    wave_parts: list[WavePartMaker] = WavePartMaker.wave_parts.copy()
    try:
        for wavePart in wave_parts:
            wavePart.getValues()
            wavePart.timeInterval = round(wavePart.timeInterval, 1)
            wavePart.nextSpawnTime = round(wavePart.nextSpawnTime, 1)
    except AttributeError:
        tkinter.messagebox.showerror('Info Error',
                                     f'There is no information in the entry boxes for wave part maker number {wavePart.number + 1}')
        return
    while wave_parts:
        for wavePart in wave_parts:
            if wavePart.nextSpawnTime > 0: wavePart.nextSpawnTime = round(wavePart.nextSpawnTime - timelineInterval, 1)
            if wavePart.nextSpawnTime == 0:
                timeline.append([wavePart.enemyType, 1, round(timeSinceSpawn, 1)])
                wavePart.nextSpawnTime = wavePart.timeInterval
                timeSinceSpawn = 0
                wavePart.num -= 1
                if wavePart.num == 0:
                    wave_parts.pop(wave_parts.index(wavePart))
        timeSinceSpawn += timelineInterval
    print(mergeDown(timeline))
    print('\n\n\n')


def mergeDown(timeline):
    newTimeline = []
    for enemy in timeline:
        if newTimeline:
            lastEnemy = newTimeline[-1]
            if enemy[0] == lastEnemy[0] and enemy[2] == lastEnemy[2]:
                lastEnemy[1] += 1
            else:
                newTimeline.append(enemy)
        else:
            newTimeline.append(enemy)
    return newTimeline


class WavePartMaker:
    wave_parts = []

    def __init__(self, win, number):
        self.root = win
        self.number = number
        self.option = tk.StringVar(win)
        tk.OptionMenu(self.root, self.option, "Normal", "Slow", "Fast", "Tank", "Boss", "Slow Boss", "Fast Boss",
                      "Tank Boss", "Final Boss").place(x=35, y=self.number * 35 + 95)
        self.amount = tk.Entry(self.root)
        self.amount.place(x=150, y=self.number * 35 + 100)
        self.initialTime = tk.Entry(self.root)
        self.initialTime.place(x=300, y=self.number * 35 + 100)
        self.finalTime = tk.Entry(self.root)
        self.finalTime.place(x=450, y=self.number * 35 + 100)
        WavePartMaker.wave_parts.append(self)

    def getValues(self):
        try:
            self.enemyType = self.option.get()
            self.num = int(self.amount.get())
            time1 = float(self.initialTime.get())
            time2 = float(self.finalTime.get())
            if time1 <= time2:
                self.time1 = time1
                self.time2 = time2
            elif time2 < time1:
                self.time1 = time2
                self.time2 = time1
            timeDifference = self.time2 - self.time1
            self.startTime = time1
            self.timeInterval = timeDifference / self.num
            self.nextSpawnTime = self.time1
        except ValueError:
            return

    def __str__(self) -> str:
        self.getValues()
        try:
            return f"{self.num} {self.enemyType}(s) from {self.time1} to {self.time2}"
        except AttributeError:
            return f"Incomplete Entry"


root = tk.Tk()
root.title('Wave Maker')
root.geometry('600x600')

tk.Label(root, height=45, width=90, bg='#bbbbbb').place(x=0, y=0)
tk.Label(root, height=5, width=90, bg='#999999').place(x=0, y=0)
tk.Label(root, text='Number', bg="#999999").place(x=150, y=50)
tk.Label(root, text='Start Time', bg="#999999").place(x=300, y=50)
tk.Label(root, text='Finish Time', bg="#999999").place(x=450, y=50)

new_wave_part_btn = tk.Button(root, text="New Wave Part", command=new_wave_part)
new_wave_part_btn.place(x=100, y=wave_part_number * 100 + 150)

finishButton = tk.Button(root, text="Finish Wave Making", command=combineWaveParts)
finishButton.place(x=25, y=50)

wavePart1 = WavePartMaker(root, wave_part_number)

wave_string = ''

if __name__ == '__main__':
    root.mainloop()
