import io
import json
import re
import sys
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import tkinter.scrolledtext as scrolledtext
import zlib
from pathlib import Path

try:
    import nbtlib
except ImportError:
    nbtlib = None


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
        self.title("Structure Decompressor")
        self.geometry("760x560")

        top = tk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)
        tk.Button(top, text="ファイルを開く", command=self.open_file, width=16).pack(side="left")
        tk.Button(top, text="貼り付け内容を解凍", command=self.decode_pasted, width=18).pack(side="left", padx=8)
        tk.Button(top, text="出力フォルダ", command=self.choose_output, width=14).pack(side="left")

        self.output_dir = tk.StringVar(value=str(Path.cwd()))
        tk.Label(top, textvariable=self.output_dir).pack(side="left", padx=8)

        tk.Label(self, text="structure:[B;...] または .txt/.mcstructure を貼り付け:").pack(anchor="w", padx=10)
        self.text = scrolledtext.ScrolledText(self, height=18)
        self.text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.status = tk.StringVar(value="準備完了")
        tk.Label(self, textvariable=self.status, anchor="w").pack(fill="x", padx=10, pady=(0, 10))

    def choose_output(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir.get())
        if folder:
            self.output_dir.set(folder)

    def open_file(self):
        path = filedialog.askopenfilename(
            title="構造ファイルを選択",
            filetypes=[
                ("Structure/text", "*.txt *.mcstructure *.nbt"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        try:
            result = process_input(path, self.output_dir.get())
            self.status.set(
                f"完了: 圧縮 {result['compressed_bytes']} B -> 解凍 {result['decompressed_bytes']} B\n"
                f"出力: {result['nbt']}"
            )
            messagebox.showinfo("完了", f"解凍しました。\n\n{result['nbt']}\n{result['snbt']}\n{result['json']}")
        except Exception as exc:
            self.status.set(f"エラー: {exc}")
            messagebox.showerror("エラー", str(exc))

    def decode_pasted(self):
        source = self.text.get("1.0", "end").strip()
        if not source:
            messagebox.showwarning("入力なし", "structure:[B;...] を貼り付けてください")
            return
        try:
            result = process_input(source, self.output_dir.get(), "pasted_structure")
            self.status.set(
                f"完了: 圧縮 {result['compressed_bytes']} B -> 解凍 {result['decompressed_bytes']} B"
            )
            messagebox.showinfo("完了", f"解凍しました。\n\n{result['nbt']}\n{result['snbt']}\n{result['json']}")
        except Exception as exc:
            self.status.set(f"エラー: {exc}")
            messagebox.showerror("エラー", str(exc))


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
