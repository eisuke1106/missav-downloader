import streamlink
from streamlink.stream import StreamIO
from streamlink_cli.output import FileOutput
import time
import sys
import math


def download_stream(title: str, url: str, quality="best"):
    streams = streamlink.streams(url)
    if quality not in streams:
        raise ValueError(f"Quality '{quality}' not available for this stream")

    # ストリームを開く
    stream = streams[quality]
    stream_fd = stream.open()

    # # 出力ファイルを開く
    # output = FileOutput(f"{title}.ts")
    # output.open()

    # # ストリームを読み込み、ファイルに書き込む
    # while True:
    #     data = stream_fd.read(1024)
    #     if not data:
    #         break
    #     output.write(data)
    print(f"{title}.ts")
    checkTime = time.time()
    startTime = checkTime
    totalSize = 0
    preTotalSize = 0

    with open(f"{title}.ts", "wb") as f:
        try:
            while True:
                diffTime = time.time() - checkTime
                diffStartTime = time.time() - startTime
                if diffTime > 1:
                    getSize = totalSize - preTotalSize
                    preTotalSize = totalSize
                    print(
                        f"\r                                                          ",
                        end="",
                    )
                    print(
                        f"\r[DOWNLOADING...] - {convert_size(totalSize)} [{convert_size(getSize)}/sec] ({math.floor(diffStartTime)}sec)\n\033[1A",
                        end="",
                    )
                    checkTime = time.time()
                data = stream_fd.read(1024)
                size = sys.getsizeof(data)
                totalSize += size
                if data == b"":
                    break
                f.write(data)
        except Exception as ex:
            print()
            print(f"{title}.ts closing")
        finally:
            stream_fd.close()

        totalTime = time.time() - startTime
        getSize = totalSize / totalTime
        print(
            f"\r                                                          ",
            end="",
        )
        print(
            f"\r[DOWNLOADED] - {convert_size(totalSize)} [{convert_size(getSize)}/sec] ({math.floor(totalTime)}sec)\n\033[1A",
            end="",
        )
        print()


def convert_size(size):
    units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB")
    i = math.floor(math.log(size, 1024)) if size > 0 else 0
    size = round(size / 1024**i, 2)

    return f"{size}{units[i]}"
