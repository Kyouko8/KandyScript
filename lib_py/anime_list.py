# Anime List
import tkinter as tk
from tkinter import ttk
from verticalscrolledframe import VerticalScrolledFrame

DEFAULT_JSON_FILE = "./anime.json"
STAR = "\u2605"
STAR_WHITE = "\u2606"


class AnimeData:
    def __init__(self, id_anime, name, seasons=1, genre=None, view_count=0, view_date=None, review=None,
                 stars=0, like=True, path=None, url_path=None, japanese_name=None, spanish_name=None,
                 language='original', subtitles=False, subtitles_language='spanish'):

        self.id_anime = id_anime
        self.name = name
        self.japanese_name = japanese_name
        self.spanish_name = spanish_name
        self.seasons = seasons
        self.genre = genre
        self.view_count = view_count
        self.view_date = view_date
        self.review = review
        self.stars = stars
        self.like = like
        self.path = path
        self.url_path = url_path
        self.language = language
        self.subtitles = subtitles
        self.subtitles_language = subtitles_language

    def get_as_dict(self):
        return {
            'id_anime': self.id_anime,
            'name': self.name,
            'japanese_name': self.japanese_name,
            'spanish_name': self.spanish_name,
            'seasons': self.seasons,
            'genre': self.genre,
            'view_count': self.view_count,
            'view_date': self.view_date,
            'stars': self.stars,
            'like': self.like,
            'path': self.path,
            'url_path': self.url_path,
            'language': self.language,
            'subtitles': self.subtitles,
            'subtitles_language': self.subtitles_language
        }

    def from_dict(self, dic):
        return AnimeData(**dic)

    def get_id(self):
        return self.id_anime


class MainFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.width = 800
        self.height = 550
        self.root = parent
        self.data = {'animes': [], 'hexids': {}}
        self._init_styles()
        self._init_main_widgets()
        self.layout()

    def _init_styles(self):
        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 12))  # Modify the font of the body
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 13, 'bold'))  # Modify the font of the headings
        # style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders
        self.style = style

    def _init_main_widgets(self):
        frame = self
        self.notebook = ttk.Notebook(frame)
        self.anime_list = AnimeListFrame(self.notebook, frame)

        self.notebook.add(self.anime_list, text="Listado")

    def layout(self):
        self.notebook.place(x=5, y=5, width=self.width-10, height=self.height-20)


class AnimeListFrame(ttk.Frame):
    def __init__(self, parent_notebook, parent_frame):
        super().__init__(parent_notebook)
        self.width = 800
        self.height = 540
        self.root = parent_frame
        self.notebook = parent_notebook
        self._init_main_widgets()
        self.layout()

    def _init_main_widgets(self):
        frame = self
        self.treeview = ttk.Treeview(frame, columns=("name", "seasons", "seen", "stars"), style="mystyle.Treeview")
        # Columns:
        self.treeview.column("#0", width=50, minwidth=50, stretch=tk.YES)
        self.treeview.column("name", width=450, minwidth=400, stretch=tk.YES)
        self.treeview.column("seasons", width=100, minwidth=70, stretch=tk.YES)
        self.treeview.column("seen", width=50, minwidth=50, stretch=tk.YES)
        self.treeview.column("stars", width=90, minwidth=90, stretch=tk.YES)
        # Headings:
        self.treeview.heading("#0", text="ID", anchor="w", command=self.sort_by_id)
        self.treeview.heading("name", text="Nombre", anchor="w", command=self.sort_by_name)
        self.treeview.heading("seasons", text="Temporadas", anchor="w", command=self.sort_by_season)
        self.treeview.heading("seen", text="Visto", anchor="w", command=self.sort_by_seen)
        self.treeview.heading("stars", text="Puntuación", anchor="w", command=self.sort_by_stars)
        # Tags:
        self.treeview.tag_configure("green_0", background="#88ff88", )
        self.treeview.tag_configure("green_1", background="#b2ffb2")
        self.treeview.tag_configure("red_0", background="#ff8888")
        self.treeview.tag_configure("red_1", background="#ffb2b2")
        # VSB:
        self.vsb = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.treeview['yscrollcommand'] = self.vsb.set
        self.vsb['command'] = self.treeview.yview

        self.load_from_list([
            AnimeData(0, "Nanatsu no Taizai", 4),
            AnimeData(1, "Mirai Nikki", 1),
            AnimeData(2, "Nanatsu no Taizai", 4),
            AnimeData(3, "Mirai Nikki", 1),
            AnimeData(4, "Nanatsu no Taizai", 4),
            AnimeData(5, "Mirai Nikki", 1),
            AnimeData(6, "Nanatsu no Taizai", 4, None, 1, stars=5),
            AnimeData(7, "Mirai Nikki", 1, None, 1, stars=4),
            AnimeData(8, "Nanatsu no Taizai", 4, None, 1, stars=3),
            AnimeData(9, "Mirai Nikki", 1, None, 1, stars=2),
            AnimeData(10, "Nanatsu no Taizai", 4, None, 1, stars=1),
            AnimeData(11, "Mirai Nikki", 1, None, 1),
            AnimeData(12, "Nanatsu no Taizai", 4),
            AnimeData(13, "Mirai Nikki", 1),
            AnimeData(14, "Nanatsu no Taizai", 4),
            AnimeData(15, "Mirai Nikki", 1),
            AnimeData(16, "Nanatsu no Taizai", 4),
            AnimeData(17, "Mirai Nikki", 1),
            AnimeData(18, "Nanatsu no Taizai", 4, None, 1, stars=5),
            AnimeData(19, "Mirai Nikki", 1, None, 1, stars=4),
            AnimeData(20, "Nanatsu no Taizai", 4, None, 1, stars=3),
            AnimeData(21, "Mirai Nikki", 1, None, 1, stars=2),
            AnimeData(22, "Nanatsu no Taizai", 4, None, 1, stars=1),
            AnimeData(23, "Mirai Nikki", 1, None, 1),
            AnimeData(24, "Nanatsu no Taizai", 4),
            AnimeData(25, "Mirai Nikki", 1),
            AnimeData(26, "Nanatsu no Taizai", 4),
            AnimeData(27, "Mirai Nikki", 1),
            AnimeData(28, "Nanatsu no Taizai", 4),
            AnimeData(29, "Mirai Nikki", 1),
            AnimeData(30, "Nanatsu no Taizai", 4, None, 1, stars=5),
            AnimeData(31, "Mirai Nikki", 1, None, 1, stars=4),
            AnimeData(32, "Nanatsu no Taizai", 4, None, 1, stars=3),
            AnimeData(33, "Mirai Nikki", 1, None, 1, stars=2),
            AnimeData(34, "Nanatsu no Taizai", 4, None, 1, stars=1),
            AnimeData(35, "Mirai Nikki", 1, None, 1)
        ])

        # Botones:
        self.but_add = ttk.Button(self, text="Agregar")
        self.but_edit = ttk.Button(self, text="Editar")
        self.but_delete = ttk.Button(self, text="Quitar")
        self.but_refresh = ttk.Button(self, text="Actualizar")

    def layout(self):
        self.treeview.place(x=8, y=8, width=self.width-56, height=self.height-80)
        self.vsb.place(x=self.width-44, y=8, width=20, height=self.height-80)
        self.but_add.place(x=8, y=self.height-64, width=185, height=24)
        self.but_edit.place(x=201, y=self.height-64, width=185, height=24)
        self.but_delete.place(x=394, y=self.height-64, width=185, height=24)
        self.but_refresh.place(x=584, y=self.height-64, width=185, height=24)

    def load_from_list(self, lst):
        n = len(self.treeview.get_children())
        for anime in lst:
            hexid = hex(anime.get_id())
            if hexid in self.root.data['hexids']:
                continue

            self.root.data['hexids'][hexid] = anime
            # Seen
            seen = "Sí" if anime.view_count > 0 else "No"
            tag_seen = "green_" if anime.view_count > 0 else "red_"
            tag_seen += str(n % 2)
            # Stars
            anime.stars = max(0, min(5, anime.stars))
            stars = STAR * anime.stars + STAR_WHITE * (5-anime.stars)
            # Update table
            self.treeview.insert("", anime.get_id(), iid=hexid, text=anime.get_id()+1, values=(anime.name, anime.seasons, seen, stars), tags=(tag_seen,))
            n += 1

    def sort_by_id(self, reverse=False):
        new_pos = 0
        items = self.treeview.get_children()

        for iid in sorted(items, key=lambda item: int(item[2:], 16), reverse=reverse):
            self.treeview.move(iid, "", new_pos)
            # Update color:
            anime = self.root.data['hexids'][iid]
            tag_seen = "green_" if anime.view_count > 0 else "red_"
            tag_seen += str(new_pos % 2)

            self.treeview.item(iid, tags=(tag_seen,))
            # Update pos:
            new_pos += 1

        self.treeview.heading("#0", command=lambda s=self: s.sort_by_id(not reverse))

    def sort_by_name(self, reverse=False):
        new_pos = 0
        ls = self.treeview.get_children()
        items = []
        for i in ls:
            item = self.treeview.item(i)
            name = item['values'][0]
            items.append((i, name))

        for iid, name in sorted(items, key=lambda item: item[1], reverse=reverse):
            self.treeview.move(iid, "", new_pos)
            # Update Color:
            anime = self.root.data['hexids'][iid]
            tag_seen = "green_" if anime.view_count > 0 else "red_"
            tag_seen += str(new_pos % 2)

            self.treeview.item(iid, tags=(tag_seen,))
            # Update pos:
            new_pos += 1

        self.treeview.heading("name", command=lambda s=self: s.sort_by_name(not reverse))

    def sort_by_season(self, reverse=False):
        new_pos = 0
        ls = self.treeview.get_children()
        items = []
        for i in ls:
            item = self.treeview.item(i)
            seasons = int(item['values'][1])
            items.append((i, seasons))

        for iid, seasons in sorted(items, key=lambda item: item[1], reverse=reverse):
            self.treeview.move(iid, "", new_pos)
            # Update Color:
            anime = self.root.data['hexids'][iid]
            tag_seen = "green_" if anime.view_count > 0 else "red_"
            tag_seen += str(new_pos % 2)

            self.treeview.item(iid, tags=(tag_seen,))
            # Update pos:
            new_pos += 1

        self.treeview.heading("seasons", command=lambda s=self: s.sort_by_season(not reverse))

    def sort_by_seen(self, reverse=False):
        new_pos = 0
        ls = self.treeview.get_children()
        items = []
        for i in ls:
            item = self.treeview.item(i)
            seen = item['values'][2] == "Sí"
            items.append((i, seen))

        for iid, seen in sorted(items, key=lambda item: (item[1], int(item[0][2:], 16)), reverse=reverse):
            self.treeview.move(iid, "", new_pos)
            # Update Color:
            anime = self.root.data['hexids'][iid]
            tag_seen = "green_" if anime.view_count > 0 else "red_"
            tag_seen += str(new_pos % 2)

            self.treeview.item(iid, tags=(tag_seen,))
            # Update pos:
            new_pos += 1

        self.treeview.heading("seen", command=lambda s=self: s.sort_by_seen(not reverse))

    def sort_by_stars(self, reverse=False):
        new_pos = 0
        ls = self.treeview.get_children()
        items = []
        for i in ls:
            item = self.treeview.item(i)
            anime = self.root.data['hexids'][i]
            stars = anime.stars
            seen = item['values'][2] == "Sí"
            items.append((i, stars, seen))

        for iid, stars, seen in sorted(items, key=lambda item: (item[1], item[2], int(item[0][2:], 16)), reverse=reverse):
            self.treeview.move(iid, "", new_pos)
            # Update Color:
            anime = self.root.data['hexids'][iid]
            tag_seen = "green_" if anime.view_count > 0 else "red_"
            tag_seen += str(new_pos % 2)

            self.treeview.item(iid, tags=(tag_seen,))
            # Update pos:
            new_pos += 1

        self.treeview.heading("stars", command=lambda s=self: s.sort_by_stars(not reverse))


class AnimeDataFrame(ttk.Frame):
    def __init__(self, parent_list, parent_frame):
        super().__init__(parent_list.notebook)
        self.width = 800
        self.height = 540
        self.root = parent_frame
        self.parent_list = parent_list
        self.notebook = parent_list.notebook
        self._init_main_widgets()
        self.layout()

    def _init_main_widgets(self):
        self.label_id = ttk.Label(self, text="ID:")
        self.label_name = ttk.Label(self, text="Nombre:")
        self.label_id = ttk.Label(self, text="ID:")
        self.label_name = ttk.Label(self, text="Nombre:")

    def layout(self):
        self.notebook.place(x=5, y=5, width=self.width-10, height=self.height-20)


if __name__ == '__main__':
    print("Starting app...")
    root = tk.Tk()
    root.geometry("810x550")
    root.title("Anime List Control - Medina Dylan")
    root.resizable(False, False)

    main = MainFrame(root)
    main.place(x=5, y=5, width=800, height=540)

    root.mainloop()
    print("Ending app...")
