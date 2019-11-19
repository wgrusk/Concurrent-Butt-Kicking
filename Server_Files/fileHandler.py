import mmap

class FileHandler:

    def __init__(self, storyFile):
        self._storyFile = storyFile
        self._sections  = self.readInSections()

    def readInSections(self):
        file = self._storyFile
        with open(file, "rt") as fp:
            mm = mmap.mmap(fp.fileno(), 0, prot=mmap.PROT_READ)
            sections = mm.split("<section>")
            print(sections)

        return "yeet"
