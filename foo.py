from textual.app import App
from textual.widgets import Placeholder


class GridTest(App):
    async def on_mount(self) -> None:
        """Make a simple grid arrangement."""
        grid = await self.view.dock_grid(edge="left", name="left")

        grid.add_column(fraction=1, name="left", min_size=20)
        grid.add_column(size=30, name="center")
        grid.add_column(fraction=1, name="right")

        grid.add_row(fraction=5, name="top", min_size=2)
        grid.add_row(fraction=3, name="middle")
        grid.add_row(fraction=1, name="middle-next")
        grid.add_row(fraction=1, name="bottom")

        grid.add_areas(
            area1="left-start|center-end,top-start|middle-end",
            area2="right,top-start|middle-end",
            area3="left-start|center-end,middle-next",
            area4="left-start|center-end,bottom",
            area5="right,middle-next-start|bottom-end",
        )

        grid.place(
            area1=Placeholder(name="area1"),
            area2=Placeholder(name="area2"),
            area3=Placeholder(name="area3"),
            area4=Placeholder(name="area4"),
            area5=Placeholder(name="area5"),
        )


GridTest.run(title="Grid Test", log="textual.log")
