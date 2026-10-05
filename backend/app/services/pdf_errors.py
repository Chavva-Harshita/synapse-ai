class PDFUploadTooLargeError(ValueError):
    pass


class PDFPageCountExceededError(ValueError):
    pass


class EmptyPDFError(ValueError):
    pass


class EncryptedPDFError(ValueError):
    pass


class PDFTextLimitExceededError(ValueError):
    pass


class PDFExtractionError(ValueError):
    pass
