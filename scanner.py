import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from PyQt6.QtCore import QThread, pyqtSignal

from utils import get_service_info, resolve_host


class PortScannerThread(QThread):
    progress_updated = pyqtSignal(int, int)
    status_updated = pyqtSignal(str, int, float)
    port_scanned = pyqtSignal(dict)
    scan_finished = pyqtSignal(int)
    scan_error = pyqtSignal(str)

    def __init__(self, target, ports, timeout_ms, thread_count, parent=None):
        super().__init__(parent)
        self.target = target
        self.ports = ports
        self.timeout = max(timeout_ms, 1) / 1000.0
        self.thread_count = thread_count
        self._stop_event = threading.Event()
        self._start_time = 0.0
        self._scanned_count = 0
        self._lock = threading.Lock()

    def stop(self):
        self._stop_event.set()

    def run(self):
        try:
            ip = resolve_host(self.target)
        except ValueError as error:
            self.scan_error.emit(str(error))
            return
        except Exception as error:
            self.scan_error.emit(f"Unable to resolve target: {error}")
            return

        self._start_time = time.time()
        self._scanned_count = 0
        total_ports = len(self.ports)

        try:
            with ThreadPoolExecutor(max_workers=self.thread_count) as executor:
                futures = [
                    executor.submit(self._scan_single_port, ip, port)
                    for port in self.ports
                ]
                for future in futures:
                    if self._stop_event.is_set():
                        break
                    future.result()
        except Exception as error:
            self.scan_error.emit(f"Unexpected scanning error: {error}")
            return

        if self._stop_event.is_set():
            self.scan_finished.emit(self._scanned_count)
        else:
            self.scan_finished.emit(total_ports)

    def _scan_single_port(self, ip, port):
        if self._stop_event.is_set():
            return

        elapsed = time.time() - self._start_time
        self.status_updated.emit(ip, port, elapsed)

        state = "Closed"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    state = "Open"
                elif result in (110, 111, 10061):
                    state = "Closed"
                else:
                    state = "Filtered"
        except socket.timeout:
            state = "Filtered"
        except (socket.gaierror, OSError):
            state = "Filtered"
        except Exception:
            state = "Filtered"

        if self._stop_event.is_set():
            return

        service, description = get_service_info(port)
        result_row = {
            "port": port,
            "state": state,
            "service": service,
            "protocol": "TCP",
            "description": description,
        }
        self.port_scanned.emit(result_row)

        with self._lock:
            self._scanned_count += 1
            count = self._scanned_count
        self.progress_updated.emit(count, len(self.ports))
