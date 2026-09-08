# -*- mode: python ; coding: utf-8 -*-
import PyInstaller.utils.hooks as h

# copy_metadata() returns (src_dist_info_dir, dest_dir_name) tuples that
# PyInstaller's own datas/TOC handling expands into individual files when
# passed into Analysis(datas=...) directly. Appending them to a.datas
# *after* Analysis() is constructed skips that expansion and hands EXE()
# a directory path where it expects a file, which fails with
# `PermissionError: ... Is a directory` (Windows) while building the PKG.
metadata_datas = []
for p in ['fastapi', 'uvicorn', 'pydantic', 'starlette', 'httpx']:
    try:
        metadata_datas += h.copy_metadata(p)
    except Exception:
        pass

a = Analysis(
    ['run_server.py'], pathex=['src'],
    datas=[('src/rtorrent_mcp', 'rtorrent_mcp')] + metadata_datas,
    hiddenimports=['uvicorn.logging','uvicorn.loops','uvicorn.loops.asyncio','uvicorn.protocols','uvicorn.protocols.http','uvicorn.protocols.http.httptools_impl','uvicorn.protocols.http.h11_impl','uvicorn.lifespan','uvicorn.lifespan.on',
    "_strptime",
],
excludes=['tkinter','setuptools','pip','wheel','test','tests','unittest','_distutils_hack'],
    noarchive=True,
)
# Remove massive binary files from bundled packages
SKIP = ['torch','playwright','bitsandbytes','llvmlite','pyarrow','pymupdf','grpc','numba','Cython','google','azure','boto3','botocore','matplotlib','PIL','pandas','scipy','sklearn','onnxruntime']
a.binaries = [b for b in a.binaries if not any(s in b[0].lower() for s in SKIP)]
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, name='rtorrent-mcp-backend', debug=False, strip=False, upx=False, upx_exclude=[],
     runtime_tmpdir=None, console=False)
