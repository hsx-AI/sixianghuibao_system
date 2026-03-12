import shutil
import subprocess
import tempfile
from pathlib import Path


def _find_soffice_executable() -> Path | None:
    candidates = ["soffice.exe", "soffice", "soffice.com", "soffice.COM"]
    for name in candidates:
        found = shutil.which(name)
        if not found:
            continue
        found_path = Path(found)
        if found_path.suffix.lower() == ".com":
            sibling_exe = found_path.with_suffix(".exe")
            if sibling_exe.exists():
                return sibling_exe
        return found_path

    windows_candidates = [
        Path(r"C:\Program Files\LibreOffice\program\soffice.exe"),
        Path(r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"),
    ]
    for path in windows_candidates:
        if path.exists():
            return path

    for drive in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        candidate = Path(f"{drive}:\\LibreOffice\\program\\soffice.exe")
        if candidate.exists():
            return candidate

    return None


def convert_word_to_pdf(input_path: Path, output_pdf_path: Path, timeout_seconds: int = 60) -> None:
    """
    Convert a Word file (.doc/.docx) to PDF using LibreOffice headless mode.

    Notes:
    - Requires LibreOffice to be installed and `soffice` available in PATH (or default install path).
    - Generates the PDF to `output_pdf_path` (parent dirs will be created).
    """
    soffice = _find_soffice_executable()
    if not soffice:
        raise RuntimeError(
            "LibreOffice 未安装或未加入 PATH，无法将 Word 转为 PDF；"
            "请安装 LibreOffice 并确保命令 `soffice` 可用。"
        )

    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="report_preview_") as tmp_dir:
        tmp_dir_path = Path(tmp_dir)
        tmp_in = tmp_dir_path / input_path.name
        tmp_in.write_bytes(input_path.read_bytes())
        lo_profile_dir = tmp_dir_path / "lo_profile"
        lo_profile_dir.mkdir(parents=True, exist_ok=True)
        user_installation = lo_profile_dir.as_uri().replace("file:///", "file:///")

        cmd = [
            str(soffice),
            "--headless",
            "--nologo",
            "--nofirststartwizard",
            f"-env:UserInstallation={user_installation}",
            "--convert-to",
            "pdf",
            "--outdir",
            str(tmp_dir_path),
            str(tmp_in),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            raise RuntimeError(f"Word 转 PDF 失败：{stderr or stdout or 'unknown error'}")

        tmp_out = tmp_dir_path / f"{tmp_in.stem}.pdf"
        if not tmp_out.exists():
            raise RuntimeError("Word 转 PDF 失败：未生成输出文件")

        output_pdf_path.write_bytes(tmp_out.read_bytes())
