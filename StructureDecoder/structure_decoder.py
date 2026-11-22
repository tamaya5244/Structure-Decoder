import io
import json
import os
import re
import struct
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


def default_output_directory():
    application_path = sys.executable if getattr(sys, "frozen", False) else __file__
    return str(Path(application_path).resolve().parent)


SETTINGS_PATH = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "StructureDecoder" / "settings.json"
DEFAULT_SETTINGS = {
    "language": "en",
    "output_dir": default_output_directory(),
    "output_mode": "new",
    "window_geometry": "760x560",
}


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
        "input_label": "Paste complete mcstructure SNBT or select a .txt/.mcstructure file:",
        "ready": "Ready",
        "choose_file": "Select a structure file",
        "filetype_structure": "Structure/text",
        "filetype_all": "All files",
        "success_title": "Done",
        "error_title": "Error",
        "error_status": "Error: {error}",
        "empty_title": "No input",
        "empty_message": "Paste the complete mcstructure data first.",
        "no_structure": "No structure:[B;...] array or zlib/NBT structure field was found.",
        "no_array": "No structure:[B;...] array was found.",
        "invalid_compressed": "The structure data is invalid or could not be decompressed.",
        "output_mode": "When the output exists:",
        "create_new": "Create a new file",
        "overwrite": "Overwrite the existing file",
        "success_message": "Decompressed mcstructure file:\n{output}",
        "done_status": "Done: {compressed} B compressed -> {decompressed} B decompressed\nOutput: {output}",
        "done_paste_status": "Done: {compressed} B compressed -> {decompressed} B decompressed\nOutput: {output}",
        "invalid_nbt": "The decompressed data is not a valid NBT structure.",
        "missing_metadata": "A complete mcstructure needs format_version and size metadata. Paste the full mcstructure data.",
        "settings_error": "Could not save settings: {error}",
        "settings_load_error": "Could not load settings: {error}",
    },
    "ja": {
        "window_title": "Structure Decompressor",
        "language": "言語:",
        "open_file": "ファイルを開く",
        "decode_pasted": "貼り付け内容を解凍",
        "output_folder": "出力フォルダ",
        "input_label": "mcstructure全体のSNBTを貼り付けるか、.txt/.mcstructureファイルを選択:",
        "ready": "準備完了",
        "choose_file": "構造ファイルを選択",
        "filetype_structure": "構造データ/テキスト",
        "filetype_all": "すべてのファイル",
        "success_title": "完了",
        "error_title": "エラー",
        "error_status": "エラー: {error}",
        "empty_title": "入力なし",
        "empty_message": "mcstructure全体のデータを貼り付けてください。",
        "no_structure": "structure:[B;...] 配列、またはzlib/NBTのstructureフィールドが見つかりません。",
        "no_array": "structure:[B;...] 配列が見つかりません。",
        "invalid_compressed": "構造データが無効か、解凍できませんでした。",
        "output_mode": "出力先に同名ファイルがある場合:",
        "create_new": "新しいファイルを作成",
        "overwrite": "既存ファイルを上書き",
        "success_message": "解凍したmcstructureファイル:\n{output}",
        "done_status": "完了: 圧縮 {compressed} B -> 解凍 {decompressed} B\n出力: {output}",
        "done_paste_status": "完了: 圧縮 {compressed} B -> 解凍 {decompressed} B\n出力: {output}",
        "invalid_nbt": "解凍データが有効なNBT構造ではありません。",
        "missing_metadata": "mcstructureの作成にはformat_versionとsizeの情報が必要です。mcstructure全体のデータを貼り付けてください。",
        "settings_error": "設定を保存できませんでした: {error}",
        "settings_load_error": "設定を読み込めませんでした: {error}",
    },
    "es": {
        "window_title": "Descompresor de estructuras",
        "language": "Idioma:",
        "open_file": "Abrir archivo",
        "decode_pasted": "Descomprimir texto",
        "output_folder": "Carpeta de salida",
        "input_label": "Pegue el SNBT completo de mcstructure o seleccione un archivo .txt/.mcstructure:",
        "ready": "Listo",
        "choose_file": "Seleccionar archivo de estructura",
        "filetype_structure": "Estructura/texto",
        "filetype_all": "Todos los archivos",
        "success_title": "Completado",
        "error_title": "Error",
        "error_status": "Error: {error}",
        "empty_title": "Sin entrada",
        "empty_message": "Pegue primero todos los datos de mcstructure.",
        "no_structure": "No se encontró el arreglo structure:[B;...] ni un campo structure zlib/NBT.",
        "no_array": "No se encontró el arreglo structure:[B;...].",
        "invalid_compressed": "Los datos de estructura no son válidos o no se pudieron descomprimir.",
        "output_mode": "Si ya existe el archivo:",
        "create_new": "Crear un archivo nuevo",
        "overwrite": "Sobrescribir el archivo existente",
        "success_message": "Archivo mcstructure descomprimido:\n{output}",
        "done_status": "Listo: {compressed} B comprimidos -> {decompressed} B descomprimidos\nSalida: {output}",
        "done_paste_status": "Listo: {compressed} B comprimidos -> {decompressed} B descomprimidos\nSalida: {output}",
        "invalid_nbt": "Los datos descomprimidos no son una estructura NBT válida.",
        "missing_metadata": "Un mcstructure completo necesita metadatos format_version y size. Pegue todos los datos de mcstructure.",
        "settings_error": "No se pudo guardar la configuración: {error}",
        "settings_load_error": "No se pudo cargar la configuración: {error}",
    },
    "fr": {
        "window_title": "Décompresseur de structures",
        "language": "Langue :",
        "open_file": "Ouvrir un fichier",
        "decode_pasted": "Décompresser le texte",
        "output_folder": "Dossier de sortie",
        "input_label": "Collez le SNBT complet de mcstructure ou sélectionnez un fichier .txt/.mcstructure :",
        "ready": "Prêt",
        "choose_file": "Sélectionner un fichier de structure",
        "filetype_structure": "Structure/texte",
        "filetype_all": "Tous les fichiers",
        "success_title": "Terminé",
        "error_title": "Erreur",
        "error_status": "Erreur : {error}",
        "empty_title": "Aucune entrée",
        "empty_message": "Collez d'abord toutes les données mcstructure.",
        "no_structure": "Aucun tableau structure:[B;...] ou champ structure zlib/NBT trouvé.",
        "no_array": "Aucun tableau structure:[B;...] trouvé.",
        "invalid_compressed": "Les données de structure sont invalides ou n'ont pas pu être décompressées.",
        "output_mode": "Si le fichier existe déjà :",
        "create_new": "Créer un nouveau fichier",
        "overwrite": "Écraser le fichier existant",
        "success_message": "Fichier mcstructure décompressé :\n{output}",
        "done_status": "Terminé : {compressed} o compressés -> {decompressed} o décompressés\nSortie : {output}",
        "done_paste_status": "Terminé : {compressed} o compressés -> {decompressed} o décompressés\nSortie : {output}",
        "invalid_nbt": "Les données décompressées ne constituent pas une structure NBT valide.",
        "missing_metadata": "Un mcstructure complet nécessite les métadonnées format_version et size. Collez toutes les données mcstructure.",
        "settings_error": "Impossible d'enregistrer les paramètres : {error}",
        "settings_load_error": "Impossible de charger les paramètres : {error}",
    },
    "de": {
        "window_title": "Struktur-Dekomprimierer",
        "language": "Sprache:",
        "open_file": "Datei öffnen",
        "decode_pasted": "Eingefügten Text entpacken",
        "output_folder": "Ausgabeordner",
        "input_label": "Vollständiges mcstructure-SNBT einfügen oder .txt/.mcstructure-Datei auswählen:",
        "ready": "Bereit",
        "choose_file": "Strukturdatei auswählen",
        "filetype_structure": "Struktur/Text",
        "filetype_all": "Alle Dateien",
        "success_title": "Fertig",
        "error_title": "Fehler",
        "error_status": "Fehler: {error}",
        "empty_title": "Keine Eingabe",
        "empty_message": "Fügen Sie zuerst alle mcstructure-Daten ein.",
        "no_structure": "Kein structure:[B;...]-Array oder zlib/NBT-structure-Feld gefunden.",
        "no_array": "Kein structure:[B;...]-Array gefunden.",
        "invalid_compressed": "Die Strukturdaten sind ungültig oder konnten nicht dekomprimiert werden.",
        "output_mode": "Wenn die Ausgabedatei bereits existiert:",
        "create_new": "Neue Datei erstellen",
        "overwrite": "Vorhandene Datei überschreiben",
        "success_message": "Dekomprimierte mcstructure-Datei:\n{output}",
        "done_status": "Fertig: {compressed} B komprimiert -> {decompressed} B dekomprimiert\nAusgabe: {output}",
        "done_paste_status": "Fertig: {compressed} B komprimiert -> {decompressed} B dekomprimiert\nAusgabe: {output}",
        "invalid_nbt": "Die dekomprimierten Daten sind keine gültige NBT-Struktur.",
        "missing_metadata": "Ein vollständiges mcstructure benötigt die Metadaten format_version und size. Fügen Sie alle mcstructure-Daten ein.",
        "settings_error": "Einstellungen konnten nicht gespeichert werden: {error}",
        "settings_load_error": "Einstellungen konnten nicht geladen werden: {error}",
    },
    "pt": {
        "window_title": "Descompactador de estruturas",
        "language": "Idioma:",
        "open_file": "Abrir arquivo",
        "decode_pasted": "Descompactar texto colado",
        "output_folder": "Pasta de saída",
        "input_label": "Cole o SNBT completo do mcstructure ou selecione um arquivo .txt/.mcstructure:",
        "ready": "Pronto",
        "choose_file": "Selecionar arquivo de estrutura",
        "filetype_structure": "Estrutura/texto",
        "filetype_all": "Todos os arquivos",
        "success_title": "Concluído",
        "error_title": "Erro",
        "error_status": "Erro: {error}",
        "empty_title": "Sem entrada",
        "empty_message": "Cole primeiro todos os dados do mcstructure.",
        "no_structure": "Nenhum array structure:[B;...] ou campo structure zlib/NBT foi encontrado.",
        "no_array": "Nenhum array structure:[B;...] foi encontrado.",
        "invalid_compressed": "Os dados da estrutura são inválidos ou não puderam ser descompactados.",
        "output_mode": "Se o arquivo de saída já existir:",
        "create_new": "Criar um novo arquivo",
        "overwrite": "Sobrescrever o arquivo existente",
        "success_message": "Arquivo mcstructure descompactado:\n{output}",
        "done_status": "Concluído: {compressed} B compactados -> {decompressed} B descompactados\nSaída: {output}",
        "done_paste_status": "Concluído: {compressed} B compactados -> {decompressed} B descompactados\nSaída: {output}",
        "invalid_nbt": "Os dados descompactados não são uma estrutura NBT válida.",
        "missing_metadata": "Um mcstructure completo precisa dos metadados format_version e size. Cole todos os dados do mcstructure.",
        "settings_error": "Não foi possível salvar as configurações: {error}",
        "settings_load_error": "Não foi possível carregar as configurações: {error}",
    },
    "ru": {
        "window_title": "Распаковщик структур",
        "language": "Язык:",
        "open_file": "Открыть файл",
        "decode_pasted": "Распаковать вставленный текст",
        "output_folder": "Папка вывода",
        "input_label": "Вставьте полный SNBT mcstructure или выберите файл .txt/.mcstructure:",
        "ready": "Готово к работе",
        "choose_file": "Выберите файл структуры",
        "filetype_structure": "Структура/текст",
        "filetype_all": "Все файлы",
        "success_title": "Готово",
        "error_title": "Ошибка",
        "error_status": "Ошибка: {error}",
        "empty_title": "Нет данных",
        "empty_message": "Сначала вставьте все данные mcstructure.",
        "no_structure": "Массив structure:[B;...] или поле structure zlib/NBT не найдены.",
        "no_array": "Массив structure:[B;...] не найден.",
        "invalid_compressed": "Данные структуры повреждены или не удалось их распаковать.",
        "output_mode": "Если файл уже существует:",
        "create_new": "Создать новый файл",
        "overwrite": "Перезаписать существующий файл",
        "success_message": "Распакованный файл mcstructure:\n{output}",
        "done_status": "Готово: сжато {compressed} Б -> распаковано {decompressed} Б\nВывод: {output}",
        "done_paste_status": "Готово: сжато {compressed} Б -> распаковано {decompressed} Б\nВывод: {output}",
        "invalid_nbt": "Распакованные данные не являются допустимой структурой NBT.",
        "missing_metadata": "Для mcstructure нужны метаданные format_version и size. Вставьте все данные mcstructure.",
        "settings_error": "Не удалось сохранить настройки: {error}",
        "settings_load_error": "Не удалось загрузить настройки: {error}",
    },
    "zh": {
        "window_title": "结构解压器",
        "language": "语言：",
        "open_file": "打开文件",
        "decode_pasted": "解压粘贴的文本",
        "output_folder": "输出文件夹",
        "input_label": "粘贴完整的 mcstructure SNBT，或选择 .txt/.mcstructure 文件：",
        "ready": "就绪",
        "choose_file": "选择结构文件",
        "filetype_structure": "结构/文本",
        "filetype_all": "所有文件",
        "success_title": "完成",
        "error_title": "错误",
        "error_status": "错误：{error}",
        "empty_title": "没有输入",
        "empty_message": "请先粘贴完整的 mcstructure 数据。",
        "no_structure": "未找到 structure:[B;...] 数组或 zlib/NBT structure 字段。",
        "no_array": "未找到 structure:[B;...] 数组。",
        "invalid_compressed": "结构数据无效或无法解压。",
        "output_mode": "如果输出文件已存在：",
        "create_new": "创建新文件",
        "overwrite": "覆盖现有文件",
        "success_message": "已解压的 mcstructure 文件：\n{output}",
        "done_status": "完成：压缩 {compressed} 字节 -> 解压 {decompressed} 字节\n输出：{output}",
        "done_paste_status": "完成：压缩 {compressed} 字节 -> 解压 {decompressed} 字节\n输出：{output}",
        "invalid_nbt": "解压后的数据不是有效的 NBT 结构。",
        "missing_metadata": "完整 mcstructure 需要 format_version 和 size 元数据。请粘贴完整的 mcstructure 数据。",
        "settings_error": "无法保存设置：{error}",
        "settings_load_error": "无法加载设置：{error}",
    },
    "ko": {
        "window_title": "구조 압축 해제기",
        "language": "언어:",
        "open_file": "파일 열기",
        "decode_pasted": "붙여넣은 텍스트 압축 해제",
        "output_folder": "출력 폴더",
        "input_label": "전체 mcstructure SNBT를 붙여넣거나 .txt/.mcstructure 파일을 선택하세요:",
        "ready": "준비됨",
        "choose_file": "구조 파일 선택",
        "filetype_structure": "구조/텍스트",
        "filetype_all": "모든 파일",
        "success_title": "완료",
        "error_title": "오류",
        "error_status": "오류: {error}",
        "empty_title": "입력 없음",
        "empty_message": "먼저 전체 mcstructure 데이터를 붙여넣으세요.",
        "no_structure": "structure:[B;...] 배열 또는 zlib/NBT structure 필드를 찾을 수 없습니다.",
        "no_array": "structure:[B;...] 배열을 찾을 수 없습니다.",
        "invalid_compressed": "구조 데이터가 잘못되었거나 압축을 해제할 수 없습니다.",
        "output_mode": "출력 파일이 이미 있는 경우:",
        "create_new": "새 파일 만들기",
        "overwrite": "기존 파일 덮어쓰기",
        "success_message": "압축 해제된 mcstructure 파일:\n{output}",
        "done_status": "완료: 압축 {compressed} B -> 압축 해제 {decompressed} B\n출력: {output}",
        "done_paste_status": "완료: 압축 {compressed} B -> 압축 해제 {decompressed} B\n출력: {output}",
        "invalid_nbt": "압축 해제된 데이터가 올바른 NBT 구조가 아닙니다.",
        "missing_metadata": "완전한 mcstructure에는 format_version 및 size 메타데이터가 필요합니다. 전체 mcstructure 데이터를 붙여넣으세요.",
        "settings_error": "설정을 저장할 수 없습니다: {error}",
        "settings_load_error": "설정을 불러올 수 없습니다: {error}",
    },
    "it": {
        "window_title": "Decompressore di strutture",
        "language": "Lingua:",
        "open_file": "Apri file",
        "decode_pasted": "Decomprimi testo incollato",
        "output_folder": "Cartella di output",
        "input_label": "Incolla l'SNBT completo di mcstructure o seleziona un file .txt/.mcstructure:",
        "ready": "Pronto",
        "choose_file": "Seleziona un file struttura",
        "filetype_structure": "Struttura/testo",
        "filetype_all": "Tutti i file",
        "success_title": "Completato",
        "error_title": "Errore",
        "error_status": "Errore: {error}",
        "empty_title": "Nessun input",
        "empty_message": "Incolla prima tutti i dati mcstructure.",
        "no_structure": "Array structure:[B;...] o campo structure zlib/NBT non trovato.",
        "no_array": "Array structure:[B;...] non trovato.",
        "invalid_compressed": "I dati della struttura non sono validi o non è stato possibile decomprimerli.",
        "output_mode": "Se il file di output esiste già:",
        "create_new": "Crea un nuovo file",
        "overwrite": "Sovrascrivi il file esistente",
        "success_message": "File mcstructure decompresso:\n{output}",
        "done_status": "Completato: {compressed} B compressi -> {decompressed} B decompressi\nOutput: {output}",
        "done_paste_status": "Completato: {compressed} B compressi -> {decompressed} B decompressi\nOutput: {output}",
        "invalid_nbt": "I dati decompressi non sono una struttura NBT valida.",
        "missing_metadata": "Un mcstructure completo richiede i metadati format_version e size. Incolla tutti i dati mcstructure.",
        "settings_error": "Impossibile salvare le impostazioni: {error}",
        "settings_load_error": "Impossibile caricare le impostazioni: {error}",
    },
}


def signed_byte(value):
    value = int(value)
    return value - 256 if value > 127 else value


def load_settings():
    settings = DEFAULT_SETTINGS.copy()
    try:
        saved = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return settings, None
    except (OSError, json.JSONDecodeError) as exc:
        return settings, str(exc)
    if not isinstance(saved, dict):
        return settings, "settings file must contain an object"
    if saved.get("language") in LANGUAGES:
        settings["language"] = saved["language"]
    if isinstance(saved.get("output_dir"), str) and saved["output_dir"]:
        settings["output_dir"] = saved["output_dir"]
    if saved.get("output_mode") in ("new", "overwrite"):
        settings["output_mode"] = saved["output_mode"]
    if isinstance(saved.get("window_geometry"), str) and re.fullmatch(
        r"\d+x\d+(?:[+-]\d+[+-]\d+)?", saved["window_geometry"]
    ):
        settings["window_geometry"] = saved["window_geometry"]
    return settings, None


def save_settings(settings):
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(
        json.dumps(settings, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def iter_byte_arrays(value, path=()):
    if nbtlib is None:
        return
    if isinstance(value, nbtlib.ByteArray):
        yield path, bytes(value)
    elif isinstance(value, nbtlib.Compound):
        for key, child in value.items():
            yield from iter_byte_arrays(child, path + (str(key),))
    elif isinstance(value, nbtlib.List):
        for index, child in enumerate(value):
            yield from iter_byte_arrays(child, path + (str(index),))


def find_compressed_payload(root):
    candidates = list(iter_byte_arrays(root))
    candidates.sort(
        key=lambda item: (
            not item[0] or item[0][-1].lower() not in ("structure", "compressed"),
            not item[0] or item[0][-1].lower() != "structure",
        )
    )
    for _, payload in candidates:
        try:
            return payload, decompress_bytes(payload)
        except zlib.error:
            continue
    return None


def parse_snbt_root(text):
    if nbtlib is None:
        raise RuntimeError("nbtlib is required to create mcstructure files")
    text = text.strip().lstrip("\ufeff")
    wrapped = text.startswith("{") and text.endswith("}")
    body = text[1:-1] if wrapped else text
    depth = 0
    quote = None
    escaped = False
    normalized = []
    for character in body:
        if quote:
            normalized.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in ("'", '"'):
            quote = character
            normalized.append(character)
        elif character in "[{":
            depth += 1
            normalized.append(character)
        elif character in "]}":
            depth -= 1
            normalized.append(character)
        elif character in "\r\n" and depth == 0:
            previous = next((item for item in reversed(normalized) if not item.isspace()), None)
            if previous is not None and previous not in ",{":
                normalized.append(",")
        else:
            normalized.append(character)
    compound = "{" + "".join(normalized).strip().rstrip(",") + "}"
    return nbtlib.File(nbtlib.parse_nbt(compound))


def decompress_bytes(compressed):
    return zlib.decompress(compressed)


def serialize_nbt(root):
    buffer = io.BytesIO()
    root.write(buffer, byteorder="little")
    return buffer.getvalue()


def choose_output_path(output_dir, source_name, output_mode):
    base = Path(output_dir) / f"{source_name}_decompressed.mcstructure"
    if output_mode == "overwrite" or not base.exists():
        return base
    index = 1
    while True:
        candidate = base.with_name(f"{base.stem} ({index}){base.suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def process_input(source, output_dir=None, source_name=None, output_mode="new"):
    if nbtlib is None:
        raise RuntimeError("nbtlib is required to create mcstructure files")
    source_path = Path(source) if isinstance(source, (str, Path)) and not isinstance(source, bytes) else None

    if source_path and source_path.is_file():
        source_name = source_path.stem
        data = source_path.read_bytes()
        text = data.decode("utf-8", "ignore")
        if data and (data[0] == 10 or data[0] == 9):
            root = nbtlib.load(str(source_path), byteorder="little")
        else:
            root = parse_snbt_root(text)
    else:
        text = source.decode("utf-8", "ignore") if isinstance(source, bytes) else str(source)
        source_name = source_name or "structure"
        root = parse_snbt_root(text)

    if "format_version" not in root or "size" not in root:
        raise RuntimeError("A complete mcstructure needs format_version and size metadata")
    compressed_entry = find_compressed_payload(root)
    if compressed_entry is None:
        raise RuntimeError("No compressed NBT byte array was found")
    payload, decompressed = compressed_entry
    try:
        nbtlib.File.from_fileobj(io.BytesIO(decompressed), byteorder="little")
    except (
        EOFError,
        IndexError,
        KeyError,
        nbtlib.InvalidLiteral,
        struct.error,
        TypeError,
        UnicodeDecodeError,
        ValueError,
    ) as exc:
        raise RuntimeError("The decompressed data is not a valid NBT structure") from exc

    root["structure"] = nbtlib.ByteArray(
        [signed_byte(value) for value in decompressed]
    )
    root.pop("compression", None)
    output_bytes = serialize_nbt(root)

    output_dir = Path(output_dir) if output_dir else (source_path.parent if source_path else Path.cwd())
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = choose_output_path(output_dir, source_name, output_mode)
    if output_mode == "overwrite":
        output_path.write_bytes(output_bytes)
    else:
        with output_path.open("xb") as output_file:
            output_file.write(output_bytes)

    return {
        "compressed_bytes": len(payload),
        "decompressed_bytes": len(decompressed),
        "output": str(output_path),
    }


class DecoderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings, settings_error = load_settings()
        self.language_code = self.settings["language"]
        self.output_mode = self.settings["output_mode"]
        self.title(TRANSLATIONS[self.language_code]["window_title"])
        self.geometry(self.settings["window_geometry"])
        self.protocol("WM_DELETE_WINDOW", self.close)

        top = tk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)
        self.open_button = tk.Button(top, command=self.open_file, width=16)
        self.open_button.pack(side="left")
        self.decode_button = tk.Button(top, command=self.decode_pasted, width=20)
        self.decode_button.pack(side="left", padx=8)
        self.output_button = tk.Button(top, command=self.choose_output, width=16)
        self.output_button.pack(side="left")

        self.output_dir = tk.StringVar(value=self.settings["output_dir"])
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
        self.language_var = tk.StringVar(value=LANGUAGES[self.language_code])
        self.language_menu = ttk.Combobox(
            language_bar,
            textvariable=self.language_var,
            values=list(LANGUAGES.values()),
            state="readonly",
            width=18,
        )
        self.language_menu.pack(side="left", padx=(6, 0))
        self.language_menu.bind("<<ComboboxSelected>>", self.change_language)

        self.output_mode_label = tk.Label(language_bar)
        self.output_mode_label.pack(side="left", padx=(18, 6))
        self.output_mode_var = tk.StringVar()
        self.output_mode_menu = ttk.Combobox(
            language_bar,
            textvariable=self.output_mode_var,
            state="readonly",
            width=24,
        )
        self.output_mode_menu.pack(side="left")
        self.output_mode_menu.bind("<<ComboboxSelected>>", self.change_output_mode)

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
        if settings_error:
            messagebox.showwarning(
                self.translate("error_title"),
                self.translate("settings_load_error", error=settings_error),
            )

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
        self.persist_settings()

    def update_language(self):
        self.title(self.translate("window_title"))
        self.language_label.configure(text=self.translate("language"))
        self.output_mode_label.configure(text=self.translate("output_mode"))
        self.open_button.configure(text=self.translate("open_file"))
        self.decode_button.configure(text=self.translate("decode_pasted"))
        self.output_button.configure(text=self.translate("output_folder"))
        self.input_label.configure(text=self.translate("input_label"))
        self.output_mode_menu.configure(
            values=(self.translate("create_new"), self.translate("overwrite"))
        )
        self.output_mode_var.set(
            self.translate("overwrite" if self.output_mode == "overwrite" else "create_new")
        )
        self.status.set(self.translate(self._status_key, **self._status_values))

    def persist_settings(self, show_error=True):
        self.settings["language"] = self.language_code
        self.settings["output_dir"] = self.output_dir.get()
        self.settings["output_mode"] = self.output_mode
        self.settings["window_geometry"] = self.geometry()
        try:
            save_settings(self.settings)
        except OSError as exc:
            if show_error:
                messagebox.showerror(
                    self.translate("error_title"),
                    self.translate("settings_error", error=exc),
                )
            return False
        return True

    def change_output_mode(self, _event=None):
        selected = self.output_mode_var.get()
        self.output_mode = (
            "overwrite" if selected == self.translate("overwrite") else "new"
        )
        self.persist_settings()

    def choose_output(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir.get())
        if folder:
            self.output_dir.set(folder)
            self.persist_settings()

    def close(self):
        self.persist_settings()
        self.destroy()

    def open_file(self):
        path = filedialog.askopenfilename(
            title=self.translate("choose_file"),
            filetypes=[
                (self.translate("filetype_structure"), "*.txt *.snbt *.mcstructure *.nbt"),
                (self.translate("filetype_all"), "*.*"),
            ],
        )
        if not path:
            return
        try:
            result = process_input(
                path,
                self.output_dir.get(),
                output_mode=self.output_mode,
            )
            self.set_status(
                "done_status",
                compressed=result["compressed_bytes"],
                decompressed=result["decompressed_bytes"],
                output=result["output"],
            )
            messagebox.showinfo(
                self.translate("success_title"),
                self.translate("success_message", output=result["output"]),
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
            result = process_input(
                source,
                self.output_dir.get(),
                "pasted_structure",
                self.output_mode,
            )
            self.set_status(
                "done_paste_status",
                compressed=result["compressed_bytes"],
                decompressed=result["decompressed_bytes"],
                output=result["output"],
            )
            messagebox.showinfo(
                self.translate("success_title"),
                self.translate("success_message", output=result["output"]),
            )
        except Exception as exc:
            error = self.localize_error(exc)
            self.set_status("error_status", error=error)
            messagebox.showerror(self.translate("error_title"), error)

    def localize_error(self, exc):
        if str(exc) == "No compressed NBT byte array was found":
            return self.translate("no_structure")
        if str(exc) == "The decompressed data is not a valid NBT structure":
            return self.translate("invalid_nbt")
        if str(exc) == "A complete mcstructure needs format_version and size metadata":
            return self.translate("missing_metadata")
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
