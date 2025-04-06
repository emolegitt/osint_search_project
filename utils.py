from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QRect

def animate_title(widget):
    animation = QPropertyAnimation(widget, b"pos")
    animation.setDuration(1000)
    animation.setStartValue(widget.pos())
    animation.setEndValue(widget.pos() + QPoint(0, -10))
    animation.setEasingCurve(QEasingCurve.InOutQuad)
    animation.setLoopCount(-1)
    animation.start()

def animate_button(button):
    animation = QPropertyAnimation(button, b"geometry")
    animation.setDuration(500)
    start_rect = button.geometry()
    end_rect = QRect(start_rect.x(), start_rect.y() - 5, start_rect.width(), start_rect.height())
    animation.setStartValue(start_rect)
    animation.setEndValue(end_rect)
    animation.setEasingCurve(QEasingCurve.InOutQuad)
    animation.setLoopCount(-1)
    animation.start()

def animate_results(widget):
    animation = QPropertyAnimation(widget, b"geometry")
    animation.setDuration(500)
    start_rect = widget.geometry()
    animation.setStartValue(QRect(start_rect.x(), start_rect.y() + 20, start_rect.width(), start_rect.height()))
    animation.setEndValue(start_rect)
    animation.setEasingCurve(QEasingCurve.InBounce)
    animation.start()