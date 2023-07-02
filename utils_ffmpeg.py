import os, decorator, proglog, time, imageio
import subprocess as sp

def try_cmd(cmd):
    try:
        popen_params = {"stdout": sp.PIPE, "stderr": sp.PIPE, "stdin": sp.DEVNULL}

        # This was added so that no extra unwanted window opens on windows
        # when the child process is created
        if os.name == "nt":
            popen_params["creationflags"] = 0x08000000

        proc = sp.Popen(cmd, **popen_params)
        proc.communicate()
    except Exception as err:
        return False, err
    else:
        return True, None

FFMPEG_BINARY = os.getenv("FFMPEG_BINARY", "ffmpeg-imageio")

if FFMPEG_BINARY == "ffmpeg-imageio":
    from imageio.plugins.ffmpeg import get_exe

    FFMPEG_BINARY = get_exe()

elif FFMPEG_BINARY == "auto-detect":

    if try_cmd(["ffmpeg"])[0]:
        FFMPEG_BINARY = "ffmpeg"
    elif try_cmd(["ffmpeg.exe"])[0]:
        FFMPEG_BINARY = "ffmpeg.exe"
    else:
        FFMPEG_BINARY = "unset"
else:
    success, err = try_cmd([FFMPEG_BINARY])
    if not success:
        raise IOError(
            f"{err} - The path specified for the ffmpeg binary might be wrong"
        )

def check():
    if try_cmd([FFMPEG_BINARY])[0]:
        print(f"ffmpeg successfully found in '{FFMPEG_BINARY}'.")
    else:
        print(f"can't find or access ffmpeg in '{FFMPEG_BINARY}'.")

    #if DOTENV:
    #    print(f"\n.env file content at {DOTENV}:\n")
    #    print(Path(DOTENV).read_text())


def subprocess_call(cmd, logger="bar", errorprint=True):
    """Executes the given subprocess command.
    Set logger to None or a custom Proglog logger to avoid printings.
    """
    logger = proglog.default_bar_logger(logger)
    logger(message="Creating subclips:\n>>> " + " ".join(cmd))

    popen_params = {"stdout": sp.DEVNULL, "stderr": sp.PIPE, "stdin": sp.DEVNULL}

    if os.name == "nt":
        popen_params["creationflags"] = 0x08000000

    proc = sp.Popen(cmd, **popen_params)

    out, err = proc.communicate()  # proc.wait()
    proc.stderr.close()

    if proc.returncode:
        if errorprint:
            logger(message="Moviepy - Command returned an error")
        raise IOError(err.decode("utf8"))
    else:
        logger(message="Subclip created sucessfully")

    del proc

def preprocess_args(fun, varnames):
    """ Applies fun to variables in varnames before launching the function """

    def wrapper(f, *a, **kw):
        func_code = f.__code__

        names = func_code.co_varnames
        new_a = [
            fun(arg) if (name in varnames) and (arg is not None) else arg
            for (arg, name) in zip(a, names)
        ]
        new_kw = {k: fun(v) if k in varnames else v for (k, v) in kw.items()}
        return f(*new_a, **new_kw)

    return decorator.decorator(wrapper)

def convert_path_to_string(varnames):
    """Converts the specified variables to a path string"""
    return preprocess_args(os.fspath, varnames)

@convert_path_to_string(("inputfile", "outputfile"))
def extract_subclip(
    inputfile, recordings_path, name, start_time, end_time, outputfile=None, logger="bar"
):
    """Makes a new video file playing video file ``inputfile`` between
    the times ``start_time`` and ``end_time``."""
    ext = os.path.splitext(inputfile)[1]
    if not outputfile:
        outputfile = recordings_path + "\\" + name + ext

    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-ss",
        "%0.2f" % start_time,
        "-i",
        inputfile,
        "-t",
        "%0.2f" % (end_time - start_time),
        "-aspect",
        "1920:1080",
        "-vcodec",
        "copy",
        "-acodec",
        "copy",
        outputfile,
    ]
    subprocess_call(cmd, logger=logger)

def concatenate_videoclips(txt_file, recordings_path,logger="bar"):
    output = recordings_path + "\\0MOVIE_COMPILATION.mp4"

    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        txt_file,
        "-aspect",
        "1920:1080",
        "-c",
        "copy",
        output,
    ]
    subprocess_call(cmd, logger=logger)