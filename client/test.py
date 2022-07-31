from rich import print
from rich.table import Table

grid = Table.grid()

for i in range(30):
    grid.add_column()


for i in range(30):
    grid.add_row(*("▆ " for _ in range(30)))

print(grid)
