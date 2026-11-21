import io
import json
import re
import sys
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk
import zlib
from pathlib import Path

try:
    import nbtlib
except ImportError:
    nbtlib = None


LANGUAGES = {
    "en": "English",
    "ja": "日本語",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "pt": "Português",
    "ru": "Русский",
    "zh": "简体中文",
    "ko": "한국어",
    "it": "Italiano",
}

TRANSLATIONS = {
    "en": {
        "window_title": "Structure Decompressor",
        "language": "Language:",
        "open_file": "Open File",
        "decode_pasted": "Decode Pasted Text",
        "output_folder": "Output Folder",
        "input_label": "Paste structure:[B;...] data or .txt/.mcstructure content:",
        "ready": "Ready",
        "choose_file": "Select a structure file",
        "filetype_structure": "Structure/text",
        "filetype_all": "All files",
        "success_title": "Done",
        "success_message": "Decompression complete.\n\n{nbt}\n{snbt}\n{json}",
        "done_status": "Done: {compressed} B compressed -> {decompressed} B decompressed\nOutput: {nbt}",
        "done_paste_status": "Done: {compressed} B compressed -> {decompressed} B decompressed",
        "error_title": "Error",
        "error_status": "Error: {error}",
        "empty_title": "No input",
        "empty_message": "Paste structure:[B;...] data first.",
        "no_structure": "No structure:[B;...] array or zlib/NBT structure field was found.",
        "no_array": "No structure:[B;...] array was found.",
        "invalid_compressed": "The structure data is invalid or could not be decompressed.",
    },
    "ja": {
        "window_title": "Structure Decompressor",
        "language": "言語:",
        "open_file": "ファイルを開く",
        "decode_pasted": "貼り付け内容を解凍",
        "output_folder": "出力フォルダ",
        "input_label": "structure:[B;...] または .txt/.mcstructure の内容を貼り付け:",
        "ready": "準備完了",
        "choose_file": "構造ファイルを選択",
        "filetype_structure": "構造データ/テキスト",
        "filetype_all": "すべてのファイル",
        "success_title": "完了",
        "success_message": "解凍しました。\n\n{nbt}\n{snbt}\n{json}",
        "done_status": "完了: 圧縮 {compressed} B -> 解凍 {decompressed} B\n出力: {nbt}",
        "done_paste_status": "完了: 圧縮 {compressed} B -> 解凍 {decompressed} B",
        "error_title": "エラー",
        "error_status": "エラー: {error}",
        "empty_title": "入力なし",
        "empty_message": "structure:[B;...] を貼り付けてください。",
        "no_structure": "structure:[B;...] 配列、またはzlib/NBTのstructureフィールドが見つかりません。",
        "no_array": "structure:[B;...] 配列が見つかりません。",
        "invalid_compressed": "構造データが無効か、解凍できませんでした。",
    },
    "es": {
        "window_title": "Descompresor de estructuras",
        "language": "Idioma:",
        "open_file": "Abrir archivo",
        "decode_pasted": "Descomprimir texto",
        "output_folder": "Carpeta de salida",
        "input_label": "Pegue datos structure:[B;...] o contenido .txt/.mcstructure:",
        "ready": "Listo",
        "choose_file": "Seleccionar archivo de estructura",
        "filetype_structure": "Estructura/texto",
        "filetype_all": "Todos los archivos",
        "success_title": "Completado",
        "success_message": "Descompresión completada.\n\n{nbt}\n{snbt}\n{json}",
        "done_status": "Listo: {compressed} B comprimidos -> {decompressed} B descomprimidos\nSalida: {nbt}",
        "done_paste_status": "Listo: {compressed} B comprimidos -> {decompressed} B descomprimidos",
        "error_title": "Error",
        "error_status": "Error: {error}",
        "empty_title": "Sin entrada",
        "empty_message": "Pegue primero los datos structure:[B;...].",
        "no_structure": "No se encontró el arreglo structure:[B;...] ni un campo structure zlib/NBT.",
        "no_array": "No se encontró el arreglo structure:[B;...].",
        "invalid_compressed": "Los datos de estructura no son válidos o no se pudieron descomprimir.",
    },
    "fr": {
        "window_title": "Décompresseur de structures",
        "language": "Langue :",
        "open_file": "Ouvrir un fichier",
        "decode_pasted": "Décompresser le texte",
        "output_folder": "Dossier de sortie",
        "input_label": "Collez les données structure:[B;...] ou le contenu .txt/.mcstructure :",
        "ready": "Prêt",
        "choose_file": "Sélectionner un fichier de structure",
        "filetype_structure": "Structure/texte",
        "filetype_all": "Tous les fichiers",
        "success_title": "Terminé",
        "success_message": "Décompression terminée.\n\n{nbt}\n{snbt}\n{json}",
        "done_status": "Terminé : {compressed} o compressés -> {decompressed} o décompressés\nSortie : {nbt}",
        "done_paste_status": "Terminé : {compressed} o compressés -> {decompressed} o décompressés",
        "error_title": "Erreur",
        "error_status": "Erreur : {error}",
        "empty_title": "Aucune entrée",
        "empty_message": "Collez d'abord les données structure:[B;...].",
        "no_structure": "Aucun tableau structure:[B;...] ou champ structure zlib/NBT trouvé.",
        "no_array": "Aucun tableau structure:[B;...] trouvé.",
        "invalid_compressed": "Les données de structure sont invalides ou n'ont pas pu être décompressées.",
    },
    "de": {
        "window_title": "Struktur-Dekomprimierer",
        "language": "Sprache:",
        "open_file": "Datei öffnen",
        "decode_pasted": "Eingefügten Text entpacken",
        "output_folder": "Ausgabeordner",
        "input_label": "structure:[B;...]-Daten oder .txt/.mcstructure-Inhalt einfügen:",
        "ready": "Bereit",
        "choose_file": "Strukturdatei auswählen",
        "filetype_structure": "Struktur/Text",
        "filetype_all": "Alle Dateien",
        "success_title": "Fertig",
        "success_message": "Dekomprimierung abgeschlossen.\n\n{nbt}\n{snbt}\n{json}",
        "done_status": "Fertig: {compressed} B komprimiert -> {decompressed} B dekomprimiert\nAusgabe: {nbt}",
        "done_paste_status": "Fertig: {compressed} B komprimiert -> {decompressed} B dekomprimiert",
        "error_title": "Fehler",
        "error_status": "Fehler: {error}",
        "empty_title": "Keine Eingabe",
        "empty_message": "Fügen Sie zuerst structure:[B;...]-Daten ein.",
        "no_structure": "Kein structure:[B;...]-Array oder zlib/NBT-structure-Feld gefunden.",
        "no_array": "Kein structure:[B;...]-Array gefunden.",
        "invalid_compressed": "Die Strukturdaten sind ungültig oder konnten nicht dekomprimiert werden.",
    },
    "pt": {
        "window_title": "Descompactador de estruturas",
        "language": "Idioma:",
        "open_file": "Abrir arquivo",
        "decode_pasted": "Descompactar texto colado",
        "output_folder": "Pasta de saída",
        "input_label": "Cole dados structure:[B;...] ou conteúdo .txt/.mcstructure:",
        "ready": "Pronto",
        "choose_file": "Selecionar arquivo de estrutura",
        "filetype_structure": "Estrutura/texto",
        "filetype_all": "Todos os arquivos",
        "success_title": "Concluído",
        "success_message": "Descompactação concluída.\n\n{nbt}\n{snbt}\n{json}",
        "done_status": "Concluído: {compressed} B compactados -> {decompressed} B descompactados\nSaída: {nbt}",
        "done_paste_status": "Concluído: {compressed} B compactados -> {decompressed} B descompactados",
        "error_title": "Erro",
        "error_status": "Erro: {error}",
        "empty_title": "Sem entrada",
        "empty_message": "Cole primeiro os dados structure:[B;...].",
        "no_structure": "Nenhum array structure:[B;...] ou campo structure zlib/NBT foi encontrado.",
        "no_array": "Nenhum array structure:[B;...] foi encontrado.",
        "invalid_compressed": "Os dados da estrutura são inválidos ou não puderam ser descompactados.",
    },
    "ru": {
        "window_title": "Распаковщик структур",
        "language": "Язык:",
        "open_file": "Открыть файл",
        "decode_pasted": "Распаковать вставленный текст",
        "output_folder": "Папка вывода",
        "input_label": "Вставьте данные structure:[B;...] или содержимое .txt/.mcstructure:",
        "ready": "Готово к работе",
        "choose_file": "Выберите файл структуры",
        "filetype_structure": "Структура/текст",
        "filetype_all": "Все файлы",
        "success_title": "Готово",
        "success_message": "Распаковка завершена.\n\n{nbt}\n{snbt}\n{json}",
        "done_status": "Готово: сжато {compressed} Б -> распаковано {decompressed} Б\nВывод: {nbt}",
        "done_paste_status": "Готово: сжато {compressed} Б -> распаковано {decompressed} Б",
        "error_title": "Ошибка",
        "error_status": "Ошибка: {error}",
        "empty_title": "Нет данных",
        "empty_message": "Сначала вставьте данные structure:[B;...].",
        "no_structure": "Массив structure:[B;...] или поле structure zlib/NBT не найдены.",
        "no_array": "Массив structure:[B;...] не найден.",
        "invalid_compressed": "Данные структуры повреждены или не удалось их распаковать.",
    },
    "zh": {
        "window_title": "结构解压器",
        "language": "语言：",
        "open_file": "打开文件",
        "decode_pasted": "解压粘贴的文本",
        "output_folder": "输出文件夹",
        "input_label": "粘贴 structure:[B;...] 数据或 .txt/.mcstructure 内容：",
        "ready": "就绪",
        "choose_file": "选择结构文件",
        "filetype_structure": "结构/文本",
        "filetype_all": "所有文件",
        "success_title": "完成",
        "success_message": "解压完成。\n\n{nbt}\n{snbt}\n{json}",
        "done_status": "完成：压缩 {compressed} 字节 -> 解压 {decompressed} 字节\n输出：{nbt}",
        "done_paste_status": "完成：压缩 {compressed} 字节 -> 解压 {decompressed} 字节",
        "error_title": "错误",
        "error_status": "错误：{error}",
        "empty_title": "没有输入",
        "empty_message": "请先粘贴 structure:[B;...] 数据。",
        "no_structure": "未找到 structure:[B;...] 数组或 zlib/NBT structure 字段。",
        "no_array": "未找到 structure:[B;...] 数组。",
        "invalid_compressed": "结构数据无效或无法解压。",
    },
    "ko": {
        "window_title": "구조 압축 해제기",
        "language": "언어:",
        "open_file": "파일 열기",
        "decode_pasted": "붙여넣은 텍스트 압축 해제",
        "output_folder": "출력 폴더",
        "input_label": "structure:[B;...] 데이터 또는 .txt/.mcstructure 내용을 붙여넣으세요:",
        "ready": "준비됨",
        "choose_file": "구조 파일 선택",
        "filetype_structure": "구조/텍스트",
        "filetype_all": "모든 파일",
        "success_title": "완료",
        "success_message": "압축 해제가 완료되었습니다.\n\n{nbt}\n{snbt}\n{json}",
        "done_status": "완료: 압축 {compressed} B -> 압축 해제 {decompressed} B\n출력: {nbt}",
        "done_paste_status": "완료: 압축 {compressed} B -> 압축 해제 {decompressed} B",
        "error_title": "오류",
        "error_status": "오류: {error}",
        "empty_title": "입력 없음",
        "empty_message": "먼저 structure:[B;...] 데이터를 붙여넣으세요.",
        "no_structure": "structure:[B;...] 배열 또는 zlib/NBT structure 필드를 찾을 수 없습니다.",
        "no_array": "structure:[B;...] 배열을 찾을 수 없습니다.",
        "invalid_compressed": "구조 데이터가 잘못되었거나 압축을 해제할 수 없습니다.",
    },
    "it": {
        "window_title": "Decompressore di strutture",
        "language": "Lingua:",
        "open_file": "Apri file",
        "decode_pasted": "Decomprimi testo incollato",
        "output_folder": "Cartella di output",
        "input_label": "Incolla i dati structure:[B;...] o il contenuto .txt/.mcstructure:",
        "ready": "Pronto",
        "choose_file": "Seleziona un file struttura",
        "filetype_structure": "Struttura/testo",
        "filetype_all": "Tutti i file",
        "success_title": "Completato",
        "success_message": "Decompressione completata.\n\n{nbt}\n{snbt}\n{json}",
        "done_status": "Completato: {compressed} B compressi -> {decompressed} B decompressi\nOutput: {nbt}",
        "done_paste_status": "Completato: {compressed} B compressi -> {decompressed} B decompressi",
        "error_title": "Errore",
        "error_status": "Errore: {error}",
        "empty_title": "Nessun input",
        "empty_message": "Incolla prima i dati structure:[B;...].",
        "no_structure": "Array structure:[B;...] o campo structure zlib/NBT non trovato.",
        "no_array": "Array structure:[B;...] non trovato.",
        "invalid_compressed": "I dati della struttura non sono validi o non è stato possibile decomprimerli.",
    },
}


def signed_byte(value):
    value = int(value)
    return value - 256 if value > 127 else value


def extract_structure_bytes(text):
    match = re.search(r"structure\s*:\s*\[B\s*;\s*(.*?)\]", text, re.DOTALL)
    if not match:
        return None
    values = re.findall(r"-?\d+\s*b", match.group(1), re.IGNORECASE)
    if not values:
        return None
    return bytes(signed_byte(re.search(r"-?\d+", value).group()) & 0xff for value in values)


def to_plain(value):
    if nbtlib is not None:
        if isinstance(value, nbtlib.ByteArray):
            return list(value)
        if isinstance(value, (nbtlib.IntArray, nbtlib.LongArray)):
            return [to_plain(item) for item in value]
        if isinstance(value, nbtlib.List):
            return [to_plain(item) for item in value]
        if isinstance(value, nbtlib.Compound):
            return {str(key): to_plain(item) for key, item in value.items()}
        if isinstance(value, nbtlib.Numeric):
            return value.real
        if isinstance(value, nbtlib.String):
            return str(value)
    if isinstance(value, dict):
        return {str(key): to_plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_plain(item) for item in value]
    if hasattr(value, "item"):
        return value.item()
    return value


def find_structure_in_nbt(path):
    if nbtlib is None:
        raise RuntimeError("nbtlib is required")
    root = nbtlib.load(str(path), byteorder="little")
    if "structure" not in root:
        raise RuntimeError("This NBT file does not contain a 'structure' field")
    return bytes(root["structure"]), root


def decompress_bytes(compressed):
    return zlib.decompress(compressed)


def process_input(source, output_dir=None, source_name=None):
    source_path = Path(source) if isinstance(source, (str, Path)) and not isinstance(source, bytes) else None

    if source_path and source_path.is_file():
        source_name = source_path.stem
        data = source_path.read_bytes()
        text = data.decode("utf-8", "ignore")
        compressed = extract_structure_bytes(text)
        root = None

        if compressed is None:
            try:
                if nbtlib is not None:
                    root = nbtlib.load(str(source_path), byteorder="little")
                    if "structure" in root:
                        compressed = bytes(root["structure"])
            except Exception:
                pass

        if compressed is None:
            if data.startswith(b"\x78\x9c") or data.startswith(b"\x78\xda") or data.startswith(b"\x78\x01"):
                compressed = data
            else:
                raise RuntimeError("No structure:[B;...] array or zlib/NBT structure field was found")
    else:
        text = source.decode("utf-8", "ignore") if isinstance(source, bytes) else str(source)
        source_name = source_name or "structure"
        compressed = extract_structure_bytes(text)
        if compressed is None:
            raise RuntimeError("No structure:[B;...] array was found")
        root = None

    decompressed = decompress_bytes(compressed)
    output_dir = Path(output_dir) if output_dir else (source_path.parent if source_path else Path.cwd())
    output_dir.mkdir(parents=True, exist_ok=True)
    base = output_dir / f"{source_name}_decompressed"

    nbt_path = base.with_suffix(".nbt")
    snbt_path = base.with_suffix(".snbt")
    json_path = base.with_suffix(".json")
    bin_path = base.with_suffix(".bin")

    nbt_path.write_bytes(decompressed)
    bin_path.write_bytes(compressed)

    if nbtlib is not None:
        decoded = nbtlib.File.from_fileobj(io.BytesIO(decompressed), byteorder="little")
        snbt_path.write_text(decoded.snbt(), encoding="utf-8")
        json_path.write_text(
            json.dumps(to_plain(decoded), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    else:
        snbt_path.write_text("nbtlib is not installed; open the decompressed .nbt file with an NBT tool.\n", encoding="utf-8")
        json_path.write_text(json.dumps({"error": "nbtlib is not installed"}, indent=2), encoding="utf-8")

    return {
        "compressed_bytes": len(compressed),
        "decompressed_bytes": len(decompressed),
        "nbt": str(nbt_path),
        "snbt": str(snbt_path),
        "json": str(json_path),
        "bin": str(bin_path),
    }


class DecoderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.language_code = "en"
        self.title(TRANSLATIONS[self.language_code]["window_title"])
        self.geometry("760x560")

        top = tk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)
        self.open_button = tk.Button(top, command=self.open_file, width=16)
        self.open_button.pack(side="left")
        self.decode_button = tk.Button(top, command=self.decode_pasted, width=20)
        self.decode_button.pack(side="left", padx=8)
        self.output_button = tk.Button(top, command=self.choose_output, width=16)
        self.output_button.pack(side="left")

        self.output_dir = tk.StringVar(value=str(Path.cwd()))
        path_bar = tk.Frame(self)
        path_bar.pack(fill="x", padx=10, pady=(0, 8))
        self.output_path_label = tk.Label(
            path_bar,
            textvariable=self.output_dir,
            anchor="w",
            justify="left",
            wraplength=730,
        )
        self.output_path_label.pack(fill="x")

        language_bar = tk.Frame(self)
        language_bar.pack(fill="x", padx=10, pady=(0, 8))
        self.language_label = tk.Label(language_bar)
        self.language_label.pack(side="left")
        self.language_var = tk.StringVar(value=LANGUAGES["en"])
        self.language_menu = ttk.Combobox(
            language_bar,
            textvariable=self.language_var,
            values=list(LANGUAGES.values()),
            state="readonly",
            width=18,
        )
        self.language_menu.pack(side="left", padx=(6, 0))
        self.language_menu.bind("<<ComboboxSelected>>", self.change_language)

        self.input_label = tk.Label(self)
        self.input_label.pack(anchor="w", padx=10)
        self.text = scrolledtext.ScrolledText(self, height=18)
        self.text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._status_key = "ready"
        self._status_values = {}
        self.status = tk.StringVar()
        self.status_label = tk.Label(self, textvariable=self.status, anchor="w", justify="left")
        self.status_label.pack(fill="x", padx=10, pady=(0, 10))
        self.update_language()

    def translate(self, key, **values):
        return TRANSLATIONS[self.language_code][key].format(**values)

    def set_status(self, key, **values):
        self._status_key = key
        self._status_values = values
        self.status.set(self.translate(key, **values))

    def change_language(self, _event=None):
        selected = self.language_var.get()
        self.language_code = next(code for code, name in LANGUAGES.items() if name == selected)
        self.update_language()

    def update_language(self):
        self.title(self.translate("window_title"))
        self.language_label.configure(text=self.translate("language"))
        self.open_button.configure(text=self.translate("open_file"))
        self.decode_button.configure(text=self.translate("decode_pasted"))
        self.output_button.configure(text=self.translate("output_folder"))
        self.input_label.configure(text=self.translate("input_label"))
        self.status.set(self.translate(self._status_key, **self._status_values))

    def choose_output(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir.get())
        if folder:
            self.output_dir.set(folder)

    def open_file(self):
        path = filedialog.askopenfilename(
            title=self.translate("choose_file"),
            filetypes=[
                (self.translate("filetype_structure"), "*.txt *.mcstructure *.nbt"),
                (self.translate("filetype_all"), "*.*"),
            ],
        )
        if not path:
            return
        try:
            result = process_input(path, self.output_dir.get())
            self.set_status(
                "done_status",
                compressed=result["compressed_bytes"],
                decompressed=result["decompressed_bytes"],
                nbt=result["nbt"],
            )
            messagebox.showinfo(
                self.translate("success_title"),
                self.translate("success_message", nbt=result["nbt"], snbt=result["snbt"], json=result["json"]),
            )
        except Exception as exc:
            error = self.localize_error(exc)
            self.set_status("error_status", error=error)
            messagebox.showerror(self.translate("error_title"), error)

    def decode_pasted(self):
        source = self.text.get("1.0", "end").strip()
        if not source:
            messagebox.showwarning(self.translate("empty_title"), self.translate("empty_message"))
            return
        try:
            result = process_input(source, self.output_dir.get(), "pasted_structure")
            self.set_status(
                "done_paste_status",
                compressed=result["compressed_bytes"],
                decompressed=result["decompressed_bytes"],
            )
            messagebox.showinfo(
                self.translate("success_title"),
                self.translate("success_message", nbt=result["nbt"], snbt=result["snbt"], json=result["json"]),
            )
        except Exception as exc:
            error = self.localize_error(exc)
            self.set_status("error_status", error=error)
            messagebox.showerror(self.translate("error_title"), error)

    def localize_error(self, exc):
        if str(exc) == "No structure:[B;...] array or zlib/NBT structure field was found":
            return self.translate("no_structure")
        if str(exc) == "No structure:[B;...] array was found":
            return self.translate("no_array")
        if isinstance(exc, zlib.error):
            return self.translate("invalid_compressed")
        return str(exc)


def cli_main():
    if len(sys.argv) < 2:
        return None
    output = sys.argv[2] if len(sys.argv) >= 3 else None
    result = process_input(sys.argv[1], output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        cli_main()
    else:
        app = DecoderApp()
        app.mainloop()
