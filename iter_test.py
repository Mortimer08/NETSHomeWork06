class test:
    def getSt(self):
        return 1

test1 = test()
test2 = test()
li = []
li.append(test1)
li.append(test2)
print(test2)
print(li[0].getSt())