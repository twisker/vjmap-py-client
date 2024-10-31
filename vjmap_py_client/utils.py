import hashlib


def file_md5(file_path: str) -> str:
    """
    获取文件的MD5值
    :param file_path: 文件的路径
    :return: 文件的MD5哈希值
    """
    chunk_size = 2097152  # 2MB
    md5_hash = hashlib.md5()  # 创建MD5哈希对象

    try:
        with open(file_path, 'rb') as file:
            while chunk := file.read(chunk_size):  # 按块读取文件
                md5_hash.update(chunk)  # 更新哈希对象

        return md5_hash.hexdigest()  # 返回十六进制格式的MD5值

    except Exception as e:
        raise IOError(f"Error reading file: {e}")


def file_object_md5(file_object) -> str:
    """
    获取文件对象的MD5值
    :param file_object: 文件对象
    :return: 文件的MD5哈希值
    """
    md5_hash = hashlib.md5()  # 创建MD5哈希对象
    chunk_size = 2097152  # 2MB

    try:
        while chunk := file_object.read(chunk_size):    # 按块读取文件
            md5_hash.update(chunk)  # 更新哈希对象

        return md5_hash.hexdigest()  # 返回十六进制格式的MD5值

    except Exception as e:
        raise IOError(f"Error reading file: {e}")