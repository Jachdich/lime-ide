from os.path import join
from datetime import datetime
resource_path = "resources"
icon_folder = join(resource_path, "folder.png")

icons = {'aac': 'aac.png', 'ai': 'ai.png', 'aiff': 'aiff.png', 'avi': 'avi.png',
         'bmp': 'bmp.png', 'c': 'c.png', 'cpp': 'cpp.png', 'css': 'css.png',
         'csv': 'csv.png', 'dat': 'dat.png', 'dmg': 'dmg.png', 'doc': 'doc.png',
         'dotx': 'dotx.png', 'dwg': 'dwg.png', 'dxf': 'dxf.png', 'eps': 'eps.png',
         'exe': 'exe.png', 'file': 'file.png', 'flv': 'flv.png', 'gif': 'gif.png',
         'h': 'h.png', 'hpp': 'hpp.png', 'html': 'html.png', 'ics': 'ics.png',
         'iso': 'iso.png', 'java': 'java.png', 'jpg': 'jpg.png', 'js': 'js.png',
         'key': 'key.png', 'less': 'less.png', 'mid': 'mid.png', 'mp3': 'mp3.png',
         'mp4': 'mp4.png', 'mpg': 'mpg.png', 'odf': 'odf.png', 'ods': 'ods.png',
         'odt': 'odt.png', 'otp': 'otp.png', 'ots': 'ots.png', 'ott': 'ott.png',
         'pdf': 'pdf.png', 'php': 'php.png', 'png': 'png.png', 'ppt': 'ppt.png',
         'psd': 'psd.png', 'py': 'py.png', 'pyc': 'py.png', 'py': 'py.png',
         'qt': 'qt.png', 'rar': 'rar.png', 'rb': 'rb.png', 'rtf': 'rtf.png',
         'sass': 'sass.png', 'scss': 'scss.png', 'sql': 'sql.png', 'tga': 'tga.png',
         'tgz': 'tgz.png', 'tiff': 'tiff.png', 'txt': 'txt.png', 'md': 'txt.png', 'wav': 'wav.png',
         'xls': 'xls.png', 'xlsx': 'xlsx.png', 'xml': 'xml.png', 'iml': 'xml.png',
         'yml': 'yml.png', 'zip': 'zip.png'}

config = "config.json"
styles = "styles.json"

PORT = 64452
DEBUGGER_PORT = 25565
HOST = "127.0.0.1"

indent_level = 4
current_logfile = str(datetime.now()).replace(":", "-")
