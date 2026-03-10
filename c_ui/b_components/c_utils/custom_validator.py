from PySide6.QtGui import QIntValidator, QDoubleValidator, QValidator

class EmptyOrIntValidator(QIntValidator):
    def validate(self, input_str, pos):
        if not input_str:
            return QValidator.State.Acceptable, input_str, pos
        return super().validate(input_str, pos)

    def fixup(self, input_str):
        if not input_str:
            return ""
        return super().fixup(input_str)

class EmptyOrDoubleValidator(QDoubleValidator):
    def validate(self, input_str, pos):
        if not input_str:
            return QValidator.State.Acceptable, input_str, pos
        return super().validate(input_str, pos)

    def fixup(self, input_str):
        if not input_str:
            return ""
        return super().fixup(input_str)
