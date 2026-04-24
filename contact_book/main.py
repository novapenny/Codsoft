import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, QTimer

# -------------------- PATH FIX -------------------- #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_image(path):
    full_path = os.path.join(BASE_DIR, "images", path)
    pixmap = QPixmap(full_path)

    if pixmap.isNull():
        print(f"ERROR: Failed to load {full_path}")

    return pixmap

# -------------------- APP SETUP -------------------- #

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Floating Contact Book")
window.setFixedSize(512, 512)

window.setWindowFlag(Qt.WindowType.FramelessWindowHint)
window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

window.oldPos = None

# -------------------- DRAG WINDOW -------------------- #

def mousePressEvent(event):
    if event.button() == Qt.MouseButton.LeftButton:
        window.oldPos = event.globalPosition().toPoint()

def mouseMoveEvent(event):
    if window.oldPos:
        delta = event.globalPosition().toPoint() - window.oldPos
        window.move(window.x() + delta.x(), window.y() + delta.y())
        window.oldPos = event.globalPosition().toPoint()

window.mousePressEvent = mousePressEvent
window.mouseMoveEvent = mouseMoveEvent

# -------------------- CONSTANTS -------------------- #

WINDOW_SIZE = 512
SCALE_FACTOR = 1.2

contacts = []

# -------------------- IMAGE HELPER -------------------- #

def create_scaled_label(parent, image_name, width, height, x_offset=0):
    label = QLabel(parent)
    pixmap = get_image(image_name)

    scaled = pixmap.scaled(
        width, height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )

    x = (WINDOW_SIZE - scaled.width()) // 2 + x_offset
    y = (WINDOW_SIZE - scaled.height()) // 2

    label.setPixmap(scaled)
    label.setGeometry(x, y, scaled.width(), scaled.height())

    return label, scaled, x, y

# -------------------- COVER -------------------- #

cover, cover_scaled, cover_x, cover_y = create_scaled_label(
    window, "cover.png",
    int(291 * SCALE_FACTOR), int(327 * SCALE_FACTOR), 15
)

# -------------------- PAGES -------------------- #

pages, page_scaled, page_x, page_y = create_scaled_label(
    window, "pages.png",
    cover_scaled.width(), cover_scaled.height()
)
pages.hide()

pages2, page2_scaled, _, _ = create_scaled_label(
    window, "pages_2.png",
    cover_scaled.width(), cover_scaled.height()
)
pages2.hide()

# -------------------- INPUT FIELDS -------------------- #

def create_input(placeholder, y):
    field = QLineEdit(window)
    field.setPlaceholderText(placeholder)
    field.setGeometry(page_x + 115, page_y + y, 170, 28)
    field.hide()
    return field

name_field = create_input("Name", 80)
phone_field = create_input("Phone", 120)
email_field = create_input("Email", 160)
address_field = create_input("Address", 200)

phone_field.setMaxLength(13)

search_field = create_input("Search", 80)

# -------------------- BUTTONS -------------------- #

def create_button(text, x, y, w=120, h=32):
    btn = QPushButton(text, window)
    btn.setGeometry(x, y, w, h)
    btn.hide()
    return btn

open_button = QPushButton("Open Book", window)
open_button.setGeometry(206, 460, 100, 30)

save_button = create_button("Save Contact", page_x + 140, page_y + 240)
next_page_button = create_button("Next Page", page_x + 140, page_y + 310)
prev_page_button = create_button("Previous Page", page_x + 140, page_y + 350)

# -------------------- LABELS -------------------- #

def create_label(text, y):
    lbl = QLabel(text, window)
    lbl.setGeometry(page_x + 140, page_y + y, 120, 30)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.hide()
    return lbl

title_label = create_label("Add Contact", 40)
contact_info_label = create_label("Contact Info", 40)

success_label = QLabel("", window)
success_label.setGeometry(page_x + 120, page_y + 275, 200, 25)
success_label.hide()

# -------------------- CLOSE BUTTON -------------------- #

close_button = QPushButton("✕", window)
close_button.setGeometry(page_x + 270, page_y + 30, 24, 24)
close_button.setStyleSheet("""
QPushButton {
    background-color: white;
    color: red;
    border-radius: 12px;
    border: 1px solid red;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #ffe5e5;
}
""")
close_button.clicked.connect(app.quit)

# -------------------- CONTACT LIST -------------------- #

contact_list = QListWidget(window)
contact_list.setGeometry(page_x + 115, page_y + 120, 170, 110)
contact_list.hide()

# -------------------- HELPERS -------------------- #

def show_message(text, color="red"):
    success_label.setText(text)
    success_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    success_label.raise_()
    success_label.show()

def is_valid_phone(phone):
    return (
        (phone.isdigit() and len(phone) == 10) or
        (phone.startswith("+91") and phone[3:].isdigit() and len(phone) == 13)
    )

def is_valid_email(email):
    return email.endswith("@gmail.com") and not email.startswith("@")

def animate(widget):
    anim = QPropertyAnimation(widget, b"geometry")
    anim.setDuration(900)
    anim.setStartValue(widget.geometry())
    anim.setEndValue(QRect(widget.x(), widget.y(), 0, widget.height()))
    anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
    return anim

# -------------------- CORE FUNCTIONS -------------------- #

def refresh_contact_list():
    contact_list.clear()

    if not contacts:
        item = QListWidgetItem("No saved contacts")
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        item.setForeground(Qt.GlobalColor.gray)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        contact_list.addItem(item)
    else:
        for c in contacts:
            contact_list.addItem(QListWidgetItem(c["name"]))

def save_contact():
    name = name_field.text().strip()
    phone = phone_field.text().strip()
    email = email_field.text().strip()
    address = address_field.text().strip()

    if not all([name, phone, email, address]):
        show_message("All fields required")
        return

    if not is_valid_phone(phone):
        show_message("Invalid phone number")
        return

    if not is_valid_email(email):
        show_message("Invalid email")
        return

    contacts.append({
        "name": name,
        "phone": phone,
        "email": email,
        "address": address
    })

    refresh_contact_list()
    show_message("Contact saved successfully!", "green")

    name_field.clear()
    phone_field.clear()
    email_field.clear()
    address_field.clear()

# -------------------- PAGE TRANSITIONS -------------------- #

def open_book():
    open_button.hide()
    pages.show()
    pages.lower()

    anim = animate(cover)

    def finished():
        cover.hide()
        pages.raise_()

        for w in [title_label, name_field, phone_field, email_field,
                  address_field, save_button, next_page_button, close_button]:
            w.show()
            w.raise_()

    anim.finished.connect(finished)
    anim.start()
    window.anim = anim

def open_page2():
    pages.show()
    pages.raise_()
    pages2.show()
    pages2.lower()

    for w in [title_label, name_field, phone_field, email_field,
              address_field, save_button, success_label, next_page_button]:
        w.hide()

    anim = animate(pages)

    def finished():
        pages.hide()
        pages2.raise_()

        for w in [contact_info_label, search_field, contact_list, prev_page_button]:
            w.show()
            w.raise_()

    anim.finished.connect(finished)
    anim.start()
    window.anim2 = anim

def go_back_page1():
    anim = animate(pages2)

    def finished():
        pages2.hide()
        pages.show()
        pages.raise_()

        for w in [title_label, name_field, phone_field, email_field,
                  address_field, save_button, next_page_button]:
            w.show()
            w.raise_()

        for w in [prev_page_button, contact_info_label, search_field, contact_list]:
            w.hide()

    anim.finished.connect(finished)
    anim.start()
    window.anim3 = anim

# -------------------- SEARCH -------------------- #

def search_contact():
    text = search_field.text().strip().lower()
    contact_list.clearSelection()

    for i in range(contact_list.count()):
        item = contact_list.item(i)
        if item.text().lower() == text:
            contact_list.setCurrentItem(item)
            contact_list.scrollToItem(item)
            break

# -------------------- SIGNALS -------------------- #

open_button.clicked.connect(open_book)
save_button.clicked.connect(save_contact)
next_page_button.clicked.connect(open_page2)
prev_page_button.clicked.connect(go_back_page1)
search_field.returnPressed.connect(search_contact)

# -------------------- INIT -------------------- #

refresh_contact_list()
window.show()

sys.exit(app.exec())