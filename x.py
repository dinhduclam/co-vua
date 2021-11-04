count = 0
class XYZ:
    def pr(self):
        print("Truoc:", count)
        a.inc()
        print("Sau:", count)
class ABC:
    def inc(self):
        global count
        count = count + 1

a = ABC()
x = XYZ()
x.pr()


