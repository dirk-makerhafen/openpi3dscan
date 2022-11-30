import glob, os
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
files = glob.glob(os.path.join(SCRIPT_DIR, "*.rcproj"))
for file in files:
    content = open(file,"r").read()
    path = content.split('input fileName="')[1].split('\\images\\')[0]
    content = content.replace(path, SCRIPT_DIR)
    open(file,"w").write(content)