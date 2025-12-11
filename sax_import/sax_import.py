"""Example of a custom annotator."""

from sparv.api import Annotation, Output, annotator


@annotator("Convert every word to uppercase")
def uppercase(
    word: Annotation = Annotation("<token:word>"),
    out: Output = Output("<token>:sbx_uppercase.upper"),
    # some_config_variable: str = Config("sbx_uppercase.some_setting")
) -> None:
    """Convert to uppercase."""
    out.write([val.upper() for val in word.read()])
