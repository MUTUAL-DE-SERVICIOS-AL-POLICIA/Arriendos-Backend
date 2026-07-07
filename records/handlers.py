"""
Handler personalizado de logging que organiza logs en carpetas por fecha.

Estructura:
logs/
├── 2026-07-02/
│   ├── access.log
│   ├── errors.log
│   ├── security.log
│   └── business.log
├── 2026-07-03/
│   ├── access.log
│   └── ...

Autor: Dilan Torrez
Fecha: 2026
"""

import os
import logging
from datetime import datetime


class DailyFolderHandler(logging.Handler):
    """
    Handler que escribe logs en carpetas organizadas por fecha.

    Crea una carpeta con la fecha actual (YYYY-MM-DD) y escribe
    el archivo de log dentro de ella.
    """

    def __init__(self, base_dir, filename, **kwargs):
        self.base_dir = base_dir
        self.filename = filename
        self._current_date = None
        self._stream = None
        super().__init__(**kwargs)

    def _get_log_path(self):
        today = datetime.now().strftime('%Y-%m-%d')
        log_dir = os.path.join(self.base_dir, today)
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, self.filename)

    def _open_stream(self):
        if self._stream:
            self._stream.close()
        log_path = self._get_log_path()
        self._stream = open(log_path, 'a', encoding='utf-8')
        self._current_date = datetime.now().strftime('%Y-%m-%d')

    def emit(self, record):
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            if self._current_date != today or self._stream is None:
                self._open_stream()

            msg = self.format(record)
            self._stream.write(msg + '\n')
            self._stream.flush()
        except Exception:
            self.handleError(record)

    def close(self):
        if self._stream:
            self._stream.close()
        super().close()
