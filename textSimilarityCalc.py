import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog)
import sqlite3

# Veritabanı işlemleri
def create_db():
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Jaccard Similarity
def jaccard_similarity(text1, text2):
    words1 = set(text1.split())
    words2 = set(text2.split())
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    if not union:
        return 0
    return len(intersection) / len(union) * 100

# Simple Similarity
def simple_similarity(text1, text2):
    words1 = set(text1.split())
    words2 = set(text2.split())
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    if not union:
        return 0
    return len(intersection) / len(union) * 100

# Kullanıcı kaydetme
def add_user(username, password):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Kullanıcı kontrol etme
def check_user(username, password):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    data = cursor.fetchone()
    conn.close()
    return data is not None

# Login and Registration System
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Giriş Yap / Kayıt Ol')
        
        layout = QVBoxLayout()

        self.username = QLineEdit(self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton('Giriş Yap', self)
        self.register_button = QPushButton('Kayıt Ol', self)
        
        layout.addWidget(QLabel('Kullanıcı Adı:'))
        layout.addWidget(self.username)
        layout.addWidget(QLabel('Şifre:'))
        layout.addWidget(self.password)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)
        
        self.setLayout(layout)
        
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

    def login(self):
        username = self.username.text()
        password = self.password.text()
        if check_user(username, password):
            self.cw = ComparisonWindow()
            self.cw.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Hata', 'Kullanıcı adı veya şifre yanlış!')

    def register(self):
        username = self.username.text()
        password = self.password.text()
        if add_user(username, password):
            QMessageBox.information(self, 'Başarılı', 'Kullanıcı başarıyla kaydedildi!')
        else:
            QMessageBox.warning(self, 'Hata', 'Kullanıcı adı zaten mevcut!')

# Text Comparison Window
class ComparisonWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Metin Karşılaştırma Seçenekleri')
        
        layout = QVBoxLayout()
        
        self.jaccard_button = QPushButton('Jaccard Similarity', self)
        self.simple_button = QPushButton('Simple Intersection/Union Similarity', self)
        self.exit_button = QPushButton('Çıkış Yap', self)
        
        layout.addWidget(self.jaccard_button)
        layout.addWidget(self.simple_button)
        layout.addWidget(self.exit_button)
        
        self.setLayout(layout)
        
        self.jaccard_button.clicked.connect(lambda: self.open_comparison_window(jaccard_similarity))
        self.simple_button.clicked.connect(lambda: self.open_comparison_window(simple_similarity))
        self.exit_button.clicked.connect(self.close)

    def open_comparison_window(self, algorithm):
        text_window = TextComparisonWindow(algorithm)
        text_window.show()

class TextComparisonWindow(QWidget):
    def __init__(self, comparison_algorithm):
        super().__init__()
        self.comparison_algorithm = comparison_algorithm
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Metin Karşılaştırma')
        
        layout = QVBoxLayout()
        h_layout1 = QHBoxLayout()
        h_layout2 = QHBoxLayout()
        
        self.text1 = QLineEdit(self)
        self.text2 = QLineEdit(self)
        self.browse1 = QPushButton('Dosya Seç', self)
        self.browse2 = QPushButton('Dosya Seç', self)
        self.compare_button = QPushButton('Karşılaştır', self)
        self.result_label = QLabel('Sonuç:', self)
        self.exit_button = QPushButton('Çıkış Yap', self)
        
        h_layout1.addWidget(self.text1)
        h_layout1.addWidget(self.browse1)
        h_layout2.addWidget(self.text2)
        h_layout2.addWidget(self.browse2)
        
        layout.addLayout(h_layout1)
        layout.addLayout(h_layout2)
        layout.addWidget(self.compare_button)
        layout.addWidget(self.result_label)
        layout.addWidget(self.exit_button)
        
        self.setLayout(layout)
        
        self.browse1.clicked.connect(lambda: self.select_file(self.text1))
        self.browse2.clicked.connect(lambda: self.select_file(self.text2))
        self.compare_button.clicked.connect(self.compare)
        self.exit_button.clicked.connect(self.close)

    def select_file(self, line_edit):
        filename, _ = QFileDialog.getOpenFileName(self, 'Dosya Seç', '', 'Text Files (*.txt)')
        if filename:
            line_edit.setText(filename)

    def compare(self):
        file1 = self.text1.text()
        file2 = self.text2.text()
        try:
            with open(file1, 'r') as f1, open(file2, 'r') as f2:
                text1 = f1.read()
                text2 = f2.read()
                similarity = self.comparison_algorithm(text1, text2)
                self.result_label.setText(f"Sonuç: {similarity:.2f}%")
        except Exception as e:
            QMessageBox.warning(self, 'Hata', f'Dosyalar açılırken bir hata oluştu: {str(e)}')

# Ana Uygulama
def main():
    app = QApplication(sys.argv)
    create_db()
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


# import sys
# from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog)
# import sqlite3

# # Veritabanı işlemleri
# def create_db():
#     conn = sqlite3.connect('user.db')
#     cursor = conn.cursor()
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS users (
#         username TEXT PRIMARY KEY,
#         password TEXT
#     )
#     ''')
#     conn.commit()
#     conn.close()

# # Jaccard Similarity
# def jaccard_similarity(text1, text2):
#     words1 = set(text1.split())
#     words2 = set(text2.split())
#     intersection = words1.intersection(words2)
#     union = words1.union(words2)
#     if not union:
#         return 0
#     return len(intersection) / len(union) * 100

# # Simple Similarity
# def simple_similarity(text1, text2):
#     words1 = set(text1.split())
#     words2 = set(text2.split())
#     intersection = words1.intersection(words2)
#     union = words1.union(words2)
#     if not union:
#         return 0
#     return len(intersection) / len(union) * 100

# # Kullanıcı kaydetme
# def add_user(username, password):
#     conn = sqlite3.connect('user.db')
#     cursor = conn.cursor()
#     try:
#         cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
#         conn.commit()
#         return True
#     except sqlite3.IntegrityError:
#         return False
#     finally:
#         conn.close()

# # Kullanıcı kontrol etme
# def check_user(username, password):
#     conn = sqlite3.connect('user.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
#     data = cursor.fetchone()
#     conn.close()
#     return data is not None

# # Login and Registration System
# class LoginWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
    
#     def initUI(self):
#         self.setWindowTitle('Giriş Yap / Kayıt Ol')
        
#         layout = QVBoxLayout()

#         self.username = QLineEdit(self)
#         self.password = QLineEdit(self)
#         self.password.setEchoMode(QLineEdit.Password)
#         self.login_button = QPushButton('Giriş Yap', self)
#         self.register_button = QPushButton('Kayıt Ol', self)
        
#         layout.addWidget(QLabel('Kullanıcı Adı:'))
#         layout.addWidget(self.username)
#         layout.addWidget(QLabel('Şifre:'))
#         layout.addWidget(self.password)
#         layout.addWidget(self.login_button)
#         layout.addWidget(self.register_button)
        
#         self.setLayout(layout)
        
#         self.login_button.clicked.connect(self.login)
#         self.register_button.clicked.connect(self.register)

#     def login(self):
#         username = self.username.text()
#         password = self.password.text()
#         if check_user(username, password):
#             self.cw = ComparisonWindow()
#             self.cw.show()
#             self.close()
#         else:
#             QMessageBox.warning(self, 'Hata', 'Kullanıcı adı veya şifre yanlış!')

#     def register(self):
#         username = self.username.text()
#         password = self.password.text()
#         if add_user(username, password):
#             QMessageBox.information(self, 'Başarılı', 'Kullanıcı başarıyla kaydedildi!')
#         else:
#             QMessageBox.warning(self, 'Hata', 'Kullanıcı adı zaten mevcut!')

# # Text Comparison Window
# class ComparisonWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
    
#     def initUI(self):
#         self.setWindowTitle('Metin Karşılaştırma Seçenekleri')
        
#         layout = QVBoxLayout()
        
#         self.jaccard_button = QPushButton('Jaccard Similarity', self)
#         self.simple_button = QPushButton('Simple Intersection/Union Similarity', self)
#         self.exit_button = QPushButton('Çıkış Yap', self)
        
#         layout.addWidget(self.jaccard_button)
#         layout.addWidget(self.simple_button)
#         layout.addWidget(self.exit_button)
        
#         self.setLayout(layout)
        
#         self.jaccard_button.clicked.connect(lambda: self.open_comparison_window(jaccard_similarity))
#         self.simple_button.clicked.connect(lambda: self.open_comparison_window(simple_similarity))
#         self.exit_button.clicked.connect(self.close)

#     def open_comparison_window(self, algorithm):
#         text_window = TextComparisonWindow(algorithm)
#         text_window.show()

# class TextComparisonWindow(QWidget):
#     def __init__(self, comparison_algorithm):
#         super().__init__()
#         self.comparison_algorithm = comparison_algorithm
#         self.initUI()
    
#     def initUI(self):
#         self.setWindowTitle('Metin Karşılaştırma')
        
#         layout = QVBoxLayout()
#         h_layout1 = QHBoxLayout()
#         h_layout2 = QHBoxLayout()
        
#         self.text1 = QLineEdit(self)
#         self.text2 = QLineEdit(self)
#         self.browse1 = QPushButton('Dosya Seç', self)
#         self.browse2 = QPushButton('Dosya Seç', self)
#         self.compare_button = QPushButton('Karşılaştır', self)
#         self.result_label = QLabel('Sonuç:', self)
        
#         h_layout1.addWidget(self.text1)
#         h_layout1.addWidget(self.browse1)
#         h_layout2.addWidget(self.text2)
#         h_layout2.addWidget(self.browse2)
        
#         layout.addLayout(h_layout1)
#         layout.addLayout(h_layout2)
#         layout.addWidget(self.compare_button)
#         layout.addWidget(self.result_label)
        
#         self.setLayout(layout)
        
#         self.browse1.clicked.connect(lambda: self.select_file(self.text1))
#         self.browse2.clicked.connect(lambda: self.select_file(self.text2))
#         self.compare_button.clicked.connect(self.compare)

#     def select_file(self, line_edit):
#         filename, _ = QFileDialog.getOpenFileName(self, 'Dosya Seç', '', 'Text Files (*.txt)')
#         if filename:
#             line_edit.setText(filename)

#     def compare(self):
#         file1 = self.text1.text()
#         file2 = self.text2.text()
#         try:
#             with open(file1, 'r') as f1, open(file2, 'r') as f2:
#                 text1 = f1.read()
#                 text2 = f2.read()
#                 similarity = self.comparison_algorithm(text1, text2)
#                 self.result_label.setText(f"Sonuç: {similarity:.2f}%")#####
#         except Exception as e:
#             QMessageBox.warning(self, 'Hata', f'Dosyalar açılırken bir hata oluştu: {str(e)}')

# # Ana Uygulama
# def main():
#     app = QApplication(sys.argv)
#     create_db()
#     login = LoginWindow()
#     login.show()
#     sys.exit(app.exec_())

# if __name__ == '__main__':
#     main()
