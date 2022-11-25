import ffmpeg
import cv2
# 屏幕录制画面大小
width = 1920
height = 1080
# 录制帧率，在cv2录制中，发现帧率比较固定且偏小，主要原因为ImageGrab间隔时间稍长
# 这里可以调整的稍微大一点，当然越大对固件性能越好，推荐在15~60之间（含）
fps = 30
# 录制画面是否包含鼠标，0：不包含，1：包含
# 录制方式为gdigrab模式，包含鼠标在录制过程会看到鼠标频闪的现象，可自行搜索模块插件解决
draw_mouse = 0
# 屏幕画面录制偏移距离
offset_x = 0
offset_y = 0
# 文件名称
filename = 'test.mp4'

# 定义cv2流

# def cv2_stream():



# 录制桌面
process = (
            ffmpeg.output(
                ffmpeg.input(
                    filename='desktop', format='gdigrab', framerate=fps, offset_x=offset_x, offset_y=offset_y,
                    draw_mouse=draw_mouse, s=f'{width}x{height}'),
                filename=filename, pix_fmt='yuv420p'
            ).overwrite_output()
        )

# cmd: ffmpeg路径，如不设置，会搜寻环境变量下的ffmpeg
# 可直接下载ffmpeg.exe到工程文件目录下



ffmpeg_path = 'ffmpeg.exe'
process.run_async(cmd=ffmpeg_path, pipe_stdin=True, pipe_stdout=False, pipe_stderr=False)

# 输出到cv2窗口



# 自定义延时函数
# delay()


# 传入中断参数，在调用之前，尽量在之前有足够的延时
process.communicate(str.encode("q"))
process.terminate()
