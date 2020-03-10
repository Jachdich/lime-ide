import os
try:
    os.rename("asdf", "asdfx")
except Exception as e:
    print(str(e))
