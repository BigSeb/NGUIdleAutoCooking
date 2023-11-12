import pandas
import easyocr

reader = easyocr.Reader(['en'])


def to_text_tesseract(img, whitelist="") -> pandas.DataFrame:
    import pytesseract

    config = ""
    if (whitelist):
        config = f"-c tessedit_char_whitelist={whitelist}"
    text = pytesseract.image_to_data(img, output_type=pytesseract.Output.DATAFRAME, config=config)
    # Remove NaN
    text = text.dropna()
    # Remove white spaces
    text = text[text.text.map(lambda asd: asd.strip()) != ""]
    return text


def to_text_easyocr(img, whitelist="") -> pandas.DataFrame:
    result = reader.readtext(img, allowlist=whitelist)
    return pandas.DataFrame(result, columns=["rect", "text", "conf"])


def to_text(img, whitelist="") -> pandas.DataFrame:
    # return to_text_tesseract(img, whitelist)
    return to_text_easyocr(img, whitelist)
