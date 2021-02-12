'''renderVideo.py'''

# Included Libaries
from usefulFunctions import ProgressBar, sep

# Internal Libraries
import subprocess

def properties(cmd, args, vidFile, ffprobe):
    if(args.video_codec == 'copy'):
        cmd.extend(['-vcodec', ffprobe.getVideoCodec(vidFile)])
    elif(args.video_codec == 'uncompressed'):
        cmd.extend(['-vcodec', 'mpeg4', '-qscale:v', '1'])
    else:
        cmd.extend(['-vcodec', args.video_codec])

        if(args.video_bitrate is None):
            cmd.extend(['-crf', args.constant_rate_factor])
        else:
            cmd.extend(['-b:v', args.video_bitrate])

    if(args.tune != 'none'):
        cmd.extend(['-tune', args.tune])
    cmd.extend(['-preset', args.preset, '-movflags', '+faststart', '-strict', '-2'])
    return cmd


def renderAv(ffmpeg, ffprobe, vidFile: str, args, chunks: list, speeds: list, fps,
    temp, log):
    import av

    totalFrames = chunks[len(chunks) - 1][1]
    videoProgress = ProgressBar(totalFrames, 'Creating new video',
        args.machine_readable_progress, args.no_progress)

    input_ = av.open(vidFile)
    inputVideoStream = input_.streams.video[0]
    inputVideoStream.thread_type = 'AUTO'

    width = inputVideoStream.width
    height = inputVideoStream.height
    pix_fmt = inputVideoStream.pix_fmt

    log.debug(f'   - pix_fmt: {pix_fmt}')

    cmd = [ffmpeg.getPath(), '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo', '-pix_fmt',
        pix_fmt, '-s', f'{width}*{height}', '-framerate', f'{fps}', '-i', '-', '-pix_fmt',
        pix_fmt]

    if(args.scale != 1):
        cmd.extend(['-vf', f'scale=iw*{args.scale}:ih*{args.scale}'])

    cmd = properties(cmd, args, vidFile, ffprobe)
    cmd.append(f'{temp}{sep()}spedup.mp4')

    if(args.show_ffmpeg_debug):
        process2 = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    else:
        process2 = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

    inputEquavalent = 0.0
    outputEquavalent = 0
    index = 0
    chunk = chunks.pop(0)
    for packet in input_.demux(inputVideoStream):
        for frame in packet.decode():
            index += 1
            if(len(chunks) > 0 and index >= chunk[1]):
                chunk = chunks.pop(0)

            if(speeds[chunk[2]] != 99999):
                inputEquavalent += (1 / speeds[chunk[2]])

            while inputEquavalent > outputEquavalent:
                in_bytes = frame.to_ndarray().tobytes()
                process2.stdin.write(in_bytes)
                outputEquavalent += 1

            videoProgress.tick(index - 1)
    process2.stdin.close()
    process2.wait()

    if(log.is_debug):
        log.debug('Writing the output file.')
    else:
        log.conwrite('Writing the output file.')


def renderOpencv(ffmpeg, ffprobe, vidFile: str, args, chunks: list, speeds: list, fps,
    temp, log):
    import cv2

    cap = cv2.VideoCapture(vidFile)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    if(args.scale != 1):
        width = int(width * args.scale)
        height = int(height * args.scale)

    if(width < 2 or height < 2):
        log.error('Resolution too small.')

    log.debug(f'\n Resolution {width}x{height}')
    out = cv2.VideoWriter(f'{temp}/spedup.mp4', fourcc, fps, (width, height))

    totalFrames = chunks[len(chunks) - 1][1]
    cframe = 0

    cap.set(cv2.CAP_PROP_POS_FRAMES, cframe)
    remander = 0
    framesWritten = 0

    videoProgress = ProgressBar(totalFrames, 'Creating new video',
        args.machine_readable_progress, args.no_progress)

    def findState(chunks, cframe) -> int:
        low = 0
        high = len(chunks) - 1

        while low <= high:
            mid = low + (high - low) // 2

            if(cframe >= chunks[mid][0] and cframe < chunks[mid][1]):
                return chunks[mid][2]
            elif(cframe > chunks[mid][0]):
                low = mid + 1
            else:
                high = mid - 1

        # cframe not in chunks
        return 0

    # zoom sheet
    import numpy as np
    from interpolate import interpolate

    zoom_sheet = np.ones((totalFrames + 1), dtype=float)

    zooms = [
        [0, 60, 1, 1.5, 'linear'],
        [60, 120, 1.5, 0.5, 'linear'],
    ]

    for z in zooms:
        zoom_sheet[z[0]:z[1]] = interpolate(z[2], z[3], z[1] - z[0], log, method=z[4])

    if(len(zooms) > 0):
        log.debug(zoom_sheet)

    while cap.isOpened():
        ret, frame = cap.read()
        if(not ret or cframe > totalFrames):
            break

        if(zoom_sheet[cframe] != 1):

            zoom = zoom_sheet[cframe]
            new_size = (int(width * zoom), int(height * zoom))
            blown = cv2.resize(frame, new_size,
                interpolation=cv2.INTER_CUBIC)

            frame = blown[0:height+1, 0:width+1]

        elif(args.scale != 1):
            frame = cv2.resize(frame, (width, height),
                interpolation=cv2.INTER_CUBIC)

        cframe = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) # current frame

        state = findState(chunks, cframe)

        mySpeed = speeds[state]

        if(mySpeed != 99999):
            doIt = (1 / mySpeed) + remander
            for __ in range(int(doIt)):
                out.write(frame)
                framesWritten += 1
            remander = doIt % 1

        videoProgress.tick(cframe)
    log.debug(f'\n   - Frames Written: {framesWritten}')
    log.debug(f'   - Total Frames: {totalFrames}')

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    if(args.video_codec != 'uncompressed'):
        cmd = properties([], args, vidFile, ffprobe)
        cmd.append(f'{temp}/spedup.mp4')
        ffmpeg.run(cmd)

    if(log.is_debug):
        log.debug('Writing the output file.')
    else:
        log.conwrite('Writing the output file.')
