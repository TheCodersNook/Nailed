import random
obj = int(0)
char = ""
map = [""]
for y in range(128):
    row = ""
    for x in range(128):
        obj = random.randint(1,8)
        if obj == 1:
            char = "G"
        if obj == 2:
            char = "R"
        if obj == 3:
            char = "T"
        if obj == 4:
            char = "F"
        if obj == 5:
            char = "S"
        if obj == 6:
            char = "W"
        if obj == 7:
            char = "B"
        if obj == 8:
            char = "D"

        if char == "W":
            pass
        elif row and row[-1] == "W":
            char = "S"
        elif row and row[-1] == "S" and char == "W":
            char = "S"
        elif char == "T" and row and row[-1] in ["T", "B"]:
            char = "T"
        elif char == "B" and row and row[-1] == "T":
            char = "B"
        elif char == "R" and row and row[-1] == "R":
            char = "R"
        elif char == "F" and row and row[-1] == "G":
            char = "F"
        elif char == "D"  and row and row[-1] == "D":
            char = "D"
        row += char
    map.append(row)
for row in map:
    print(row)
