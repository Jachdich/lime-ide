import os
total = 0
files = 0
words = 0
total_text = ""
for f in os.listdir("."):
    if f != "line_counter.py" and f.endswith(".py") and not f.startswith("."):
        files += 1
        with open(f, "r") as f:
            text = f.read()
            words += len(text.split(" "))
            lines = text.split("\n")
            for l in lines:
                if len(l.strip(" ")) > 0:
                    total += 1
                elif len(l.strip(" ")) > 0:
                    print(l.strip(" "))

            total_text += "\n".join(lines)

print(words)
print("There are {t} total lines of code, spread over {f} files, giving an average of {n} lines per file.".format(t = total, f = files, n = float(total) / files))
#with open("line_history.txt", "a") as f:
#    f.write(str(total) + " " + str(files) + "\n")

#with open("total.txt", "w") as f:
#    f.write(total_text)
