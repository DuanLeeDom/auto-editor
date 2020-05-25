[![Build Status](https://travis-ci.com/WyattBlue/auto-editor.svg?branch=master)](https://travis-ci.com/WyattBlue/auto-editor)
 &nbsp;&nbsp;<sup>version 20w21d hot fix
# Auto-Editor
Auto-Editor is a video editing tool that can automatically edit raw source video into a entertaining and polished video.
It works by analyzing the video's audio to detect when a section needs to be cut, kept in, or zoomed in, then auto-editor runs a subproccess called ffmpeg to create the new video.

# Usage
## Minimal Example

Create an edited version of example.mp4 with the default parameters.
```console
$ python auto-editor.py example.mp4
```

## Change the Feel
You can change feel of the video by changing how much frames

```console
$ python auto-editor.py example.mp4 --frame_margin 8 --silent_threshold 0.03
```

See [the docs](/github%20resources/docs.md) for more commands and usages.


# Installing Auto-Editor
[Installing for Windows](/github%20resources/install_win.md)

[Installing for Mac](/github%20resources/install_mac.md)

[Installing for Linux](/github%20resources/install_lin.md)

# Help or Issues
If you have a bug or a suggestion, you can [create a new issue](https://github.com/WyattBlue/auto-editor/issues/new) on this github page. If you'll like to discuss this or contact the dev personally. You can do that by [joining the discord server](https://discord.com/invite/kMHAWJJ).
