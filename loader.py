# idea: find size of root dir set that equal to goal
# call a load method on each processed .hiec before processing
# collect size
# on save, call load method that subtracts this size
# from initial goal size.
# derive loading print statments from this.
import pathlib

class loader:

    def __init__(self, root_path):
        self.root_size = self.get_root_size(root_path)
        self.processed_sum = 0
        self.progress = 0

    def get_root_size(self, root_path):
        # returns the size of the given filesystem
        size = 0
        path = pathlib.Path(root_path)

        for file in path.rglob('*'):
            if file.is_file():
                size += file.stat().st_size

        return size
    
    def load(self, file_path):
        # increments the size of processed files.
        file_size = 0

        if file_path.is_file():
            file_size = file_path.stat().st_size
        else:
            print("Error in loader module load()")

        self.processed_sum += file_size

        self.print_progress()

    def print_progress(self):
        self.progress = self.processed_sum / self.root_size

        print(f'Loading... {self.progress}% complete')

