# pyMultiLogger

Very much work in progress.

Extension of the python logging module to allow for multiple handlers to be used at the same time.  Specifically aimed at Python 3.8 because many of the examples online don't work due to old bugs.

The example shows using a TOML config file, whereas all other examples I have found use JSON or YAML.  This relies upon [tomlkit](https://pypi.org/project/tomlkit/) because the standard library parser can't handle tables with empty string names, required for the root logger.

## References

<https://gist.github.com/FhyTan/bef73b8f464589cd8c740608f1e1435c>
<https://github.com/mCodingLLC/VideosSampleCode/tree/master/videos/135_modern_logging>
<https://rob-blackbourn.medium.com/how-to-use-python-logging-queuehandler-with-dictconfig-1e8b1284e27a>
