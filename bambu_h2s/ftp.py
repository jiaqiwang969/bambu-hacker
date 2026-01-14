"""
Bambu Lab FTP 文件上传
用于上传打印文件到打印机
"""

import ftplib
import ssl
import os
from typing import Optional, Callable


class BambuFTP:
    """Bambu Lab 打印机 FTP 客户端"""

    def __init__(
        self,
        ip: str,
        access_code: str,
        port: int = 990,
        username: str = "bblp"
    ):
        self.ip = ip
        self.port = port
        self.username = username
        self.access_code = access_code
        self._ftp: Optional[ftplib.FTP_TLS] = None

    def connect(self) -> bool:
        """连接到打印机 FTP"""
        try:
            # 创建 FTP_TLS 连接
            self._ftp = ftplib.FTP_TLS()
            self._ftp.ssl_version = ssl.PROTOCOL_TLS

            # 连接
            self._ftp.connect(self.ip, self.port, timeout=30)

            # 登录
            self._ftp.login(self.username, self.access_code)

            # 切换到安全数据连接
            self._ftp.prot_p()

            print(f"FTP 连接成功: {self.ip}:{self.port}")
            return True

        except Exception as e:
            print(f"FTP 连接失败: {e}")
            return False

    def disconnect(self):
        """断开 FTP 连接"""
        if self._ftp:
            try:
                self._ftp.quit()
            except:
                pass
            self._ftp = None

    def list_files(self, path: str = "/") -> list:
        """列出目录内容"""
        if not self._ftp:
            return []

        try:
            files = []
            self._ftp.retrlines(f"LIST {path}", files.append)
            return files
        except Exception as e:
            print(f"列出文件失败: {e}")
            return []

    def upload_file(
        self,
        local_path: str,
        remote_path: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """
        上传文件到打印机

        Args:
            local_path: 本地文件路径
            remote_path: 远程路径（默认为 /cache/）
            progress_callback: 进度回调函数 (已上传字节, 总字节)
        """
        if not self._ftp:
            print("未连接到 FTP")
            return False

        if not os.path.exists(local_path):
            print(f"文件不存在: {local_path}")
            return False

        filename = os.path.basename(local_path)
        if remote_path is None:
            remote_path = f"/cache/{filename}"

        file_size = os.path.getsize(local_path)
        uploaded = [0]  # 使用列表以便在闭包中修改

        def callback(data):
            uploaded[0] += len(data)
            if progress_callback:
                progress_callback(uploaded[0], file_size)

        try:
            with open(local_path, "rb") as f:
                # 使用 STOR 命令上传
                self._ftp.storbinary(
                    f"STOR {remote_path}",
                    f,
                    blocksize=8192,
                    callback=callback
                )

            print(f"上传成功: {local_path} -> {remote_path}")
            return True

        except Exception as e:
            print(f"上传失败: {e}")
            return False

    def download_file(
        self,
        remote_path: str,
        local_path: str,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> bool:
        """
        从打印机下载文件

        Args:
            remote_path: 远程文件路径
            local_path: 本地保存路径
            progress_callback: 进度回调函数 (已下载字节)
        """
        if not self._ftp:
            print("未连接到 FTP")
            return False

        downloaded = [0]

        def callback(data):
            downloaded[0] += len(data)
            if progress_callback:
                progress_callback(downloaded[0])
            return data

        try:
            with open(local_path, "wb") as f:
                def write_callback(data):
                    downloaded[0] += len(data)
                    if progress_callback:
                        progress_callback(downloaded[0])
                    f.write(data)

                self._ftp.retrbinary(f"RETR {remote_path}", write_callback)

            print(f"下载成功: {remote_path} -> {local_path}")
            return True

        except Exception as e:
            print(f"下载失败: {e}")
            return False

    def delete_file(self, remote_path: str) -> bool:
        """删除远程文件"""
        if not self._ftp:
            return False

        try:
            self._ftp.delete(remote_path)
            print(f"删除成功: {remote_path}")
            return True
        except Exception as e:
            print(f"删除失败: {e}")
            return False

    def mkdir(self, path: str) -> bool:
        """创建目录"""
        if not self._ftp:
            return False

        try:
            self._ftp.mkd(path)
            return True
        except Exception as e:
            print(f"创建目录失败: {e}")
            return False

    def get_size(self, remote_path: str) -> int:
        """获取文件大小"""
        if not self._ftp:
            return -1

        try:
            return self._ftp.size(remote_path)
        except:
            return -1

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
